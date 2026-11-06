"""Create a classified pack from reviewed/checkpointed public-image labels."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import shutil


DESCRIPTIONS = {
    "happy": "开心、大笑、兴奋、得意、庆祝，适合轻松正向回应。",
    "sad": "伤心、哭泣、委屈、失落或遗憾，适合表达低落和需要安慰。",
    "angry": "生气、愤怒、抱怨或抗议，避免在严肃冲突中进一步激化矛盾。",
    "confused": "疑惑、问号、不理解、求解释或怀疑，需要对方澄清。",
    "surprised": "惊讶、震惊、意外或不可思议，适合突发消息和超出预期的情况。",
    "shy": "害羞、脸红、不好意思、腼腆，适合温和互动。",
    "like": "喜欢、爱心、亲亲、抱抱，适合友好的亲密表达，尊重对方边界。",
    "approval": "点赞、认可、夸奖、佩服或赞同，用于正向反馈。",
    "thanks": "感谢、感激、致谢，用于收到帮助或善意。",
    "apology": "道歉、认错、请求原谅，用于承认失误和缓和误会。",
    "sigh": "无语、无奈、叹气、疲惫或认命，适合表达招架不住、暂时不想说话。",
    "sleep": "困了、睡觉、休息或晚安，适合作息提醒和结束夜聊。",
    "greeting": "你好、早安、打招呼、欢迎或报到，适合开启聊天。",
    "farewell": "再见、告辞、离开、溜走或下线，适合结束当前对话。",
    "food": "吃饭、饮茶、喝水、食物或饿了，适合吃喝话题。",
    "work": "工作、学习、写代码、任务、加班或忙碌，适合讨论进度和任务。",
    "waiting": "等待、催促、请求回复，适合询问进展或等待对方回应。",
    "watching": "围观、吃瓜、偷看、关注后续或看戏，适合轻松关注正在发生的事。",
    "teasing": "调侃、吐槽、反讽、玩笑或轻微嘲讽；仅用于友善斗图，不用于仇恨或霸凌。",
    "refuse": "拒绝、不行、不想、否认、禁止或别说了，适合明确表达不接受。",
    "encourage": "加油、鼓励、支持、打气或坚持，适合给对方力量。",
    "request": "求帮助、拜托、求求、要东西、讨红包或报酬，适合轻松请求。",
    "awkward": "尴尬、心虚、掩饰、社死或装作无事，适合自嘲和缓和冷场。",
    "thinking": "思考、沉思、脑子卡住、反思或认真判断，适合需要想一想时。",
    "sick": "生病、受伤、身体不舒服或带病聊天，用于表达自身身体状况。",
    "fear": "害怕、紧张、恐惧或瑟瑟发抖，用于表达不安和担心。",
    "comfort": "安慰、摸摸头、拍拍、别难过或照顾对方，适合温和关怀。",
    "gift": "送礼、递东西、给你或分享物品，适合友好赠予和交换。",
}


def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("original", type=Path)
    ap.add_argument("labels", type=Path)
    ap.add_argument("destination", type=Path)
    args = ap.parse_args()
    if args.destination.exists():
        raise SystemExit("Destination must not already exist")
    idx = json.loads((args.original / "source_index.json").read_text())
    labels = {}
    for line in args.labels.read_text().splitlines():
        row = json.loads(line)
        labels[row["sha256"]] = row
    hashes = {x["sha256"] for x in idx["images"]}
    original_count = len({x["relative_path"] for x in idx["images"]})
    if set(labels) != hashes:
        raise SystemExit(f"Incomplete classification: {len(labels)} labels / {len(hashes)} contents")
    out = args.destination
    out.mkdir(parents=True)
    for name in ["RIGHTS.md", "LICENSE-CODE", ".gitignore"]:
        shutil.copyfile(args.original / name, out / name)
    shutil.copytree(args.original / "previews", out / "previews")
    semantics, sources, omitted, seen = {}, [], {}, set()
    counts = Counter()
    for item in idx["images"]:
        digest = item["sha256"]
        row = labels[digest]
        category = row["category"]
        if row["exclude"] or category == "review" or float(row["confidence"]) < .65:
            omitted[digest] = {"sha256": digest, "upstream_path": item["upstream_path"],
                               "reason": row.get("exclusion_reason") or "unclear_or_low_confidence"}
            continue
        if category not in DESCRIPTIONS:
            raise ValueError(f"Unknown category: {category}")
        original = args.original / item["relative_path"]
        relative = f"memes/{category}/{digest}{original.suffix.lower()}"
        duplicate = digest in seen
        if not duplicate:
            target = out / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            # Byte-identical originals: no watermarks, transcoding, or image edits.
            shutil.copyfile(original, target)
            if hashlib.sha256(target.read_bytes()).hexdigest() != digest:
                raise ValueError("Image content hash mismatch")
            seen.add(digest); counts[category] += 1
            entry_id = hashlib.sha256((digest + "\0" + category + "\0" + relative).encode()).hexdigest()
            semantics[entry_id] = {"entry_id": entry_id, "content_sha256": digest,
                                  "relative_path": relative, "category": category,
                                  "caption": row["caption"].strip(), "caption_status": "done",
                                  "tags": [category], "visible_text": row.get("visible_text", ""),
                                  "provenance": "Classification and caption: " + row.get("model", "Codex-assisted visual review") + "; GIFs use sampled frames; not exhaustively human-reviewed"}
        sources.append({**item, "relative_path": relative, "deduplicated": duplicate})
    if not counts:
        raise ValueError("No publishable images")
    cover = out / "previews/cover.jpg"
    if hashlib.sha256(cover.read_bytes()).hexdigest() not in seen:
        replacement = next((p for p in (out / "memes/happy").glob("*.jpg")), None)
        if replacement is None:
            replacement = next((out / "memes").rglob("*.jpg"))
        shutil.copyfile(replacement, cover)
    m = json.loads((args.original / "manifest.json").read_text())
    m.update(version="1.1.0", categories={k: {"description": v} for k, v in DESCRIPTIONS.items() if counts[k]},
             description=f"整理自 ChineseBQB，按图片画面和文字分为 {len(counts)} 个情绪/用途分类，共 {len(seen)} 张去重图片，附逐图中文描述。模糊、低置信度或被标记为不宜分发的图片未纳入聊天包；自动分类尚可能有误。",
             tags=["community", "chinese", "chinesebqb", "semantic", "animated", "static"],
             extensions={"semantic": {"version": 1, "file": "semantic_metadata.json"}})
    m["source"]["ref"] = "v1.1.0"
    dump(out / "manifest.json", m)
    dump(out / "memes_data.json", {k: v["description"] for k, v in m["categories"].items()})
    dump(out / "semantic_metadata.json", {"schema_version": "2.0", "pack_id": m["id"], "images": semantics})
    dump(out / "source_index.json", {**idx, "images": sources})
    stats = {"original_images": original_count, "classified_unique_contents": len(labels), "images": len(seen),
             "categories": len(counts), "cross_series_duplicates": original_count - len(labels),
             "review_omitted": sum(x["category"] == "review" and not x["exclude"] for x in labels.values()),
             "flagged_omitted": sum(bool(x["exclude"]) for x in labels.values()),
             "image_bytes": sum(p.stat().st_size for p in (out / "memes").rglob("*") if p.is_file()),
             "category_counts": dict(counts)}
    dump(out / "build-summary.json", stats)
    # Review inventory is metadata only; omitted image bytes are not distributed.
    dump(out / "classification-review.json", {"description": "Omitted; these images are not in memes/ and are not selected for chat.", "images": list(omitted.values())})
    rights = (out / "RIGHTS.md").read_text().replace("全部 5,770 张表情图片", "全部表情图片")
    rights += "\n本版本采用模型辅助的情绪/用途分类和初筛；自动初筛不等于人工逐图审核或版权授权。无法可靠识别或被标记不宜分发的图片未纳入本版本聊天资源。\n"
    (out / "RIGHTS.md").write_text(rights, encoding="utf-8")
    lines = ["# 情绪与用途分类", "", "按实际画面、可见文字和聊天用途分类；不再按角色系列编号分组。", "",
             "| 分类 | 图片数 | 使用场景 |", "| --- | --- | --- |"]
    for k, v in m["categories"].items(): lines.append(f"| `{k}` | {counts[k]} | {v['description']} |")
    (out / "CATEGORIES.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(stats, ensure_ascii=False))


if __name__ == "__main__":
    main()
