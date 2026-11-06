# ChineseBQB · AstrBot 表情包

> **全部表情资源来源：[zhaoolee/ChineseBQB](https://github.com/zhaoolee/ChineseBQB)。**
>
> 本仓库的全部 5,770 张表情图片及封面均整理自该上游仓库的
> [固定快照 `85f369b`](https://github.com/zhaoolee/ChineseBQB/tree/85f369bb520c44147c7bfc7ee1abf77cface46d1)。
> 原素材由上游维护者及社区贡献者收集；本项目仅进行 AstrBot 格式适配、分类整理与去重，未修改图片字节。
> **上游是素材收集来源，不代表每张图片的原创作者或版权人；图片版权归各自权利人。**
> 上游快照未提供统一 LICENSE，授权情况见 [RIGHTS.md](RIGHTS.md)。

将 [ChineseBQB](https://github.com/zhaoolee/ChineseBQB) 整理为 [AstrBot meme_manager](https://github.com/anka-afk/astrbot_plugin_meme_manager) 可通过 GitHub 地址安装的资源包。

![封面](previews/cover.jpg)

## 在 AstrBot 安装

1. 打开 **插件 → 表情包管理器 → 资源广场**。
2. 选择通过 GitHub 仓库地址安装，填写：

   ```text
   https://github.com/DumKing/ChineseBQB-AstrBot
   ```

   如需分别填写，仓库为 `DumKing/ChineseBQB-AstrBot`，分支为 `main`，子目录为 `.`。
3. 安装完成后，在 **设置中心 → 使用规则** 选择此包，设为默认或绑定指定会话／人格，然后保存。

管理页面切换选中的包只影响浏览；聊天使用哪个包由使用规则决定。GitHub 下载需要可用网络。

## 内容与体积

- **5,770 张图片，115 个系列分类**，图片总量约 **517 MiB**。
- 来自上游正式编号系列及两个社区表情目录，排除 README、网页和生成工具的配图。
- 分类内部按图片内容去重，移除 116 份重复文件；保持不同系列独立。
- 原始 GIF 保留动画；支持 PNG、JPEG、GIF、WebP。完整分类见 [CATEGORIES.md](CATEGORIES.md)。
- **按系列归类，未逐图做情绪、OCR 或语义标注**。例如“猫和老鼠”内可有多种情绪；需要准确按语义选图时，可按需在插件中生成描述和索引。
- 全量分类会增加提供给模型的分类提示；若只想用少量角色，可安装后在管理页整理成自己的小包。
- 无需下载模型到服务器；主要增加磁盘占用。安装过程会暂存和复制文件，建议至少留出 **3 GB** 空间。

## 结构与验证

`manifest.json` 和 `memes/<category>/<image>` 位于根目录，符合 meme_manager 资源包规范。清单已经过官方 JSON Schema 及当前部署插件的校验；每张图均通过 Pillow 读取检查。来源、哈希和去重记录见 [source_index.json](source_index.json)。

## 从固定上游快照重新构建

在本仓库以外准备空的输出目录，安装 `tools/requirements.txt`，下载下列快照 ZIP，然后执行：

```text
上游：https://github.com/zhaoolee/ChineseBQB
提交：85f369bb520c44147c7bfc7ee1abf77cface46d1
```

```bash
python tools/build_pack.py /path/to/upstream.zip /path/to/empty-pack   --commit 85f369bb520c44147c7bfc7ee1abf77cface46d1   --schema tools/manifest.schema.json
```

不自动拉取上游更新，避免未知内容变化。适配代码与图片权利范围见 [RIGHTS.md](RIGHTS.md)。
