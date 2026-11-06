# ChineseBQB · AstrBot 表情包

> **全部表情资源来源：[zhaoolee/ChineseBQB](https://github.com/zhaoolee/ChineseBQB)。**
>
> 本仓库全部表情图片及封面均整理自该上游的
> [固定快照 `85f369b`](https://github.com/zhaoolee/ChineseBQB/tree/85f369bb520c44147c7bfc7ee1abf77cface46d1)。
> 上游维护者及社区贡献者为素材收集者，不代表每张图片的原创作者或版权人；图片版权归各自权利人。
> 本项目仅做格式适配、内容分类和去重，保持原始图片字节。上游未附统一 LICENSE，详见 [RIGHTS.md](RIGHTS.md)。

适用于 [AstrBot meme_manager](https://github.com/anka-afk/astrbot_plugin_meme_manager)。
**v1.1.0 按图片画面、可见文字和聊天用途分类，已替换旧版 `series_xxx` 角色系列目录。**

![封面](previews/cover.jpg)

## 安装与启用

1. 打开 **插件 → 表情包管理器 → 资源广场 → GitHub 仓库安装**。
2. 填入：

   ```text
   https://github.com/DumKing/ChineseBQB-AstrBot
   ```

   仓库 `DumKing/ChineseBQB-AstrBot`，分支 `main`（或固定 tag `v1.1.0`），子目录 `.`。
3. 安装后，到 **设置中心 → 使用规则** 将本包设为默认或绑定指定会话／人格，再保存。

可直接使用「分类级标签 → 主模型自选」，**无需向量模型**。包内附带中文图片描述；如需语义检索，可在插件中按自己的向量模型重建索引，未分发任何本机向量、账号密钥或运行状态。

## 分类与处理范围

- 全量检查旧版的 **5,770 张图片**，跨系列重复内容合并为 **5,755 份唯一内容**。
- 当前聊天包包含 **5,173 张图片、28 个情绪／用途分类**，图片约 **448.9 MiB**。
- 类别包括开心 `happy`、难过 `sad`、疑惑 `confused`、吐槽 `teasing`、感谢 `thanks`、拒绝 `refuse` 等；实际非空分类、数量与适用描述见 [CATEGORIES.md](CATEGORIES.md)。
- **571 份含义不清、低置信度或无法完整解码的内容**未纳入聊天包，另有 **11 份被模型标记不宜分发的内容**未纳入。
- 未纳入内容仅保留复核记录，不在 `memes/` 中分发对应图片。旧版仍保留在历史 tag；本版索引只指向 `v1.1.0`。
- GIF 原文件及动画保持原样；识别时对动画抽取多个时刻，不能保证理解每一帧。

分类和描述由 Codex 辅助完成：部分经 `gpt-6.1-sol` 接口识别，部分在当前会话中逐批看图整理，并对样本进行复核；已有可见文字记录随包保留。**分类和内容初筛可能有误，不等于逐图人工审核或版权授权。** 发现不合适的分类可在插件管理页调整，或附图片文件名提交 Issue。

## 文件格式与来源

- `manifest.json`：包清单及分类说明。
- `memes/<category>/<sha256>.<ext>`：按情绪／用途存放的原始图片。
- `semantic_metadata.json`：可选图片描述扩展，含可见文字和来源方式，不包含向量。
- `source_index.json`：保留上游图片路径、原始文件哈希与去重关系。
- `classification_labels.jsonl`：完整分类决策；未纳入内容的描述和文字已作占位处理。
- `classification-review.json`：未纳入内容的复核清单，不包含图片。

清单与语义元数据按官方 JSON Schema 验证，分类目录及每张图片的路径、SHA-256 和条目 ID 均作关联校验。下载和安装需要可用的 GitHub 网络及临时磁盘空间，建议至少预留 **3 GB**。

## 重建

需先在独立目录解压旧版 `v1.0.1`（原始图片及来源记录），再使用本版本的分类决策重建到一个不存在的目录：

```bash
python tools/build_pack.py /path/to/v1.0.1 classification_labels.jsonl /path/to/new-pack
```

这一步只复制原图并生成清单，不会发起模型请求。分类算法不是仅将角色系列改名；目录移动由逐图识别结果决定。

适配代码许可与第三方图片的权利范围见 [RIGHTS.md](RIGHTS.md)。
