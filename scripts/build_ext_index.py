#!/usr/bin/env python3
# 扫 ext/<id>/*.zip 与 *.mtextra，从包内 manifest.json 生成 ext/index.json。
# 上传者只需要把 zip 丢进 ext/<id>/，不用手改任何 JSON；CI 会校验并重建索引。
import hashlib, json, os, sys, zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXT = os.environ.get("EXT_DIR") or os.path.join(ROOT, "repo", "ext")

def find_manifest(z):
    names = z.namelist()
    cands = [n for n in names if n == "manifest.json" or n.endswith("/manifest.json")]
    cands.sort(key=lambda n: (n.count("/"), n))
    for n in cands:
        if n.count("/") <= 2:
            try:
                return json.loads(z.read(n).decode("utf-8")), n
            except Exception:
                continue
    return None, None

def vkey(v):
    return [int(x) if str(x).isdigit() else str(x) for x in str(v).replace("-", ".").split(".")]

def main():
    errors, entries = [], []
    if not os.path.isdir(EXT):
        print("no ext dir"); return 0
    for d in sorted(os.listdir(EXT)):
        p = os.path.join(EXT, d)
        if not os.path.isdir(p) or d.startswith("."):
            continue
        zips = sorted(f for f in os.listdir(p) if f.lower().endswith((".zip", ".mtextra")))
        if not zips:
            errors.append(f"{d}: 目录里没有 .zip / .mtextra"); continue
        for fn in zips:
            zp = os.path.join(p, fn)
            try:
                z = zipfile.ZipFile(zp)
            except Exception as e:
                errors.append(f"{d}/{fn}: 不是有效 zip（{e}）"); continue
            man, mn = find_manifest(z)
            if not man:
                errors.append(f"{d}/{fn}: 包内找不到 manifest.json（放 zip 根或单层目录下）"); continue
            if not str(man.get("framework", "")).startswith("v2"):
                errors.append(f"{d}/{fn}: manifest framework 必须是 v2.x（当前 {man.get('framework')}）"); continue
            # 市场要求"一个目录一个扩展"：多扩展合包只能走本地安装，不能上市场
            extras = []
            for n in z.namelist():
                if n == mn or not n.endswith("manifest.json") or n.count("/") > 2:
                    continue
                try:
                    om = json.loads(z.read(n).decode("utf-8"))
                except Exception:
                    continue
                if str(om.get("framework", "")).startswith("v2"):
                    extras.append(n)
            if extras:
                errors.append(f"{d}/{fn}: 包内有多个扩展 manifest（{', '.join(extras[:3])}）；多扩展合包请拆成单扩展再上架"); continue
            eid = str(man.get("id", ""))
            if not eid:
                errors.append(f"{d}/{fn}: manifest 缺 id"); continue
            if eid != d:
                errors.append(f"{d}/{fn}: manifest id（{eid}）与目录名（{d}）不一致"); continue
            dylib = str(man.get("dylib", ""))
            prefix = mn[:-len("manifest.json")]
            if dylib and (prefix + dylib) not in z.namelist():
                errors.append(f"{d}/{fn}: 包里没有 manifest 声明的 {prefix + dylib}"); continue
            data = open(zp, "rb").read()
            sb = man.get("sidebar") or {}
            items = sb.get("items") or [{}]
            entries.append({
                "id": eid, "name": man.get("name") or eid,
                "version": str(man.get("version") or "0"),
                "author": man.get("author") or "",
                "description": man.get("description") or "",
                "category": sb.get("category") or man.get("category") or "扩展",
                "icon": (items[0] or {}).get("icon") or "puzzlepiece.extension",
                "iconImage": man.get("iconImage") or "",
                "size": len(data),
                "sha256": hashlib.sha256(data).hexdigest(),
                "download": f"{d}/{fn}",
                "format": "mtextra" if fn.lower().endswith(".mtextra") else "zip",
            })
    byid = {}
    for e in entries:
        cur = byid.get(e["id"])
        if not cur or vkey(e["version"]) > vkey(cur["version"]):
            byid[e["id"]] = e
    idx = {"name": "MTFile 扩展市场", "extensions": sorted(byid.values(), key=lambda e: e["name"])}
    open(os.path.join(EXT, "index.json"), "w", encoding="utf-8").write(json.dumps(idx, ensure_ascii=False, indent=2) + "\n")
    print(f"index: {len(byid)} 个扩展")
    for e in errors:
        print("ERROR:", e, file=sys.stderr)
    return 1 if errors else 0

if __name__ == "__main__":
    sys.exit(main())
