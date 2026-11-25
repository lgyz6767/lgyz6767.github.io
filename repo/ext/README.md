# MTFile 扩展市场（本目录）

市场内容就是这里的文件夹：**每个扩展一个目录，目录名 = manifest.json 里的 `id`，里面放 zip**。

```
repo/ext/
├── index.json                              # 自动生成，别手改
├── com.lgyz.mtext.game2048/
│   └── MT2048Ext.zip
└── com.lgyz.mt.ext.demo/
    └── MTDemoExt.zip
```

## 上传一个扩展

1. 扩展包（`.mtextra`，或 `.zip`）里必须有 `manifest.json`（`framework` 以 `v2` 开头）和它声明的 dylib：
   ```
   扩展.zip
   ├── manifest.json
   └── YourExt.dylib
   ```
   （放在 zip 根目录，或包一层同名文件夹都可以。）
2. 新建目录 `repo/ext/<manifest 里的 id>/`，把 zip 放进去。
3. 不用改 `index.json` —— 推上来后 GitHub Actions 会跑 `scripts/build_ext_index.py`，
   校验 manifest、id 与目录名一致、dylib 存在，然后自动重建 `index.json` 并提交回仓库。
4. 合并后 MTFile 打开扩展市场（扩展管理页右上角「市场」）刷新即可看到。

## 开发文档

扩展怎么写、权限怎么申请、包格式怎么组织：见 `lgyz6767/Mtfile-iOS-extras-SDK` 仓库（`readme.md` + `MARKET.md` + `demo`/`template`）。

## 给别人提交申请

仓库是公开的，任何人都可以提 PR 而不需要写权限：

- Fork `lgyz6767/lgyz6767.github.io` → 在 `repo/ext/` 下加目录和包 → 提 PR。
- PR 会自动跑上面的校验；`ext/index.json` 由 CI 生成，不用自己改，也不会冲突。
- 没有 GitHub 账号或不会提 PR 的，把 zip 发到反馈群（QQ 1137296245），由维护者合入。

维护者侧不需要做任何手工操作；校验失败会在 Actions 里直接指出是哪个包、哪一项不合格。
