"""Build a pinned ChineseBQB archive into an AstrBot meme_manager pack."""
import argparse
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import re
import shutil
import warnings
import zipfile

from PIL import Image
import jsonschema


def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("archive", type=Path)
    parser.add_argument("destination", type=Path)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--schema", type=Path, required=True)
    args = parser.parse_args()
    dest = args.destination
    dest.mkdir(parents=True, exist_ok=True)
    if (dest / "memes").exists():
        raise SystemExit("Use an empty destination to avoid mixing pack versions.")
    categories, sources, seen, skipped = {}, [], set(), []
    formats = {"PNG": ".png", "JPEG": ".jpg", "GIF": ".gif", "WEBP": ".webp"}
    source_groups = {}
    with zipfile.ZipFile(args.archive) as archive:
        for member in sorted(archive.infolist(), key=lambda item: item.filename):
            parts = PurePosixPath(member.filename).parts
            if len(parts) < 3 or member.is_dir() or ".." in parts:
                continue
            relative = PurePosixPath(*parts[1:])
            series = parts[1]
            if not (re.match(r"^\d{3}", series) or series in {
                "微信网友贡献表情包_暂存_有时间慢慢整理BQB", "斗图之王BQB"
            }):
                continue
            if relative.suffix.lower() not in {".png", ".jpg", ".jpeg", ".gif", ".webp"}:
                continue
            if re.match(r"^\d{3}", series):
                category = "series_" + series[:3]
            else:
                category = "community" if series.startswith("微信") else "meme_king"
            data = archive.read(member)
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("error", Image.DecompressionBombWarning)
                    with Image.open(io.BytesIO(data)) as image:
                        extension = formats.get(image.format)
                        if not extension:
                            raise ValueError("unsupported format")
                        image.verify()
            except Exception as exc:
                skipped.append({"path": str(relative), "reason": type(exc).__name__})
                continue
            digest = hashlib.sha256(data).hexdigest()
            target = f"memes/{category}/{digest}{extension}"
            duplicate = (category, digest) in seen
            if not duplicate:
                path = dest / target
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(data)
                seen.add((category, digest))
            source_groups[category] = series
            sources.append({"upstream_path": str(relative), "relative_path": target,
                            "sha256": digest, "deduplicated": duplicate})
    for category, series in sorted(source_groups.items()):
        categories[category] = {"description": (
            f"ChineseBQB 的「{series}」系列表情。适合用户提及此角色、题材，或明确要求此系列斗图时使用。"
            "本分类按原仓库系列整理，包含多种情绪；未逐图做情绪或文字识别，请勿据此假定图片的具体含义。"
        )}
    if not seen:
        raise SystemExit("No valid meme images found")
    manifest = {
        "schema_version": 1, "id": "chinesebqb-astrbot", "name": "ChineseBQB 中文表情包合集",
        "version": "1.0.0", "author": "原素材：zhaoolee/ChineseBQB 及贡献者；适配：DumKing",
        "description": f"ChineseBQB 的 AstrBot 适配包：{len(seen)} 张有效图片，{len(categories)} 个原始系列分类。保留 GIF 动画，排除网站和 README 配图，分类内去重。未逐图做语义标注。",
        "homepage": "https://github.com/DumKing/ChineseBQB-AstrBot",
        "license": "SEE RIGHTS.md；素材版权归各自权利人，上游未提供统一许可证",
        "tags": ["chinese", "memes", "collection", "chinesebqb"],
        "source": {"type": "github", "repo": "DumKing/ChineseBQB-AstrBot", "ref": "main", "subpath": "."},
        "compat": {"min_plugin_version": "4.0.0"}, "categories": categories,
    }
    # Reuse an actual supplied image as cover; never rewrite source image bytes.
    cover = next((s for s in sources if s["relative_path"].startswith("memes/series_010/")
                  and s["relative_path"].endswith(".jpg")), sources[0])
    cover_path = "previews/cover" + Path(cover["relative_path"]).suffix
    (dest / "previews").mkdir(exist_ok=True)
    shutil.copyfile(dest / cover["relative_path"], dest / cover_path)
    manifest.update(icon=cover_path, previews=[cover_path])
    jsonschema.Draft202012Validator(json.loads(args.schema.read_text())).validate(manifest)
    dump(dest / "manifest.json", manifest)
    dump(dest / "memes_data.json", {key: value["description"] for key, value in categories.items()})
    dump(dest / "source_index.json", {"upstream": "zhaoolee/ChineseBQB", "commit": args.commit,
          "images": sources, "skipped": skipped})
    stats = {"images": len(seen), "categories": len(categories), "original_image_paths": len(sources),
             "duplicates_removed": len(sources) - len(seen), "skipped_invalid": len(skipped),
             "image_bytes": sum(p.stat().st_size for p in (dest / "memes").rglob("*") if p.is_file())}
    dump(dest / "build-summary.json", stats)
    print(json.dumps(stats, ensure_ascii=False))


if __name__ == "__main__":
    main()
