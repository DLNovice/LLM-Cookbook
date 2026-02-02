import os
import re
from pathlib import Path

# ================= 配置 =================
PROJECT_ROOT = Path(".").resolve()
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp"}
DRY_RUN = False         # True: 仅输出，不删除
ASSETS_DIR_NAME = "assets"

# ================= 正则 =================
# ![alt](path)
MD_IMG_RE = re.compile(r'!\[[^\]]*\]\(([^)]+)\)')
# <img src="path">
HTML_IMG_RE = re.compile(r'<img[^>]+src=["\']([^"\']+)["\']')

used_images = set()
all_images = set()

# ================= 1. 扫描所有 md 文件 =================
for md_path in PROJECT_ROOT.rglob("*.md"):
    try:
        content = md_path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        continue

    matches = MD_IMG_RE.findall(content) + HTML_IMG_RE.findall(content)

    for img_ref in matches:
        # 去掉 query / hash
        img_ref = img_ref.split("?")[0].split("#")[0].strip()

        # 跳过网络图片
        if img_ref.startswith(("http://", "https://")):
            continue

        # 相对 md 文件解析
        img_path = (md_path.parent / img_ref).resolve()

        if img_path.suffix.lower() in IMAGE_EXTS:
            used_images.add(img_path)

# ================= 2. 收集所有 assets 下的图片 =================
for assets_dir in PROJECT_ROOT.rglob(ASSETS_DIR_NAME):
    if assets_dir.is_dir():
        for img in assets_dir.rglob("*"):
            if img.suffix.lower() in IMAGE_EXTS:
                all_images.add(img.resolve())

# ================= 3. 差集 =================
unused_images = sorted(all_images - used_images)

# ================= 4. 输出 / 删除 =================
print(f"\n📦 assets 中图片总数: {len(all_images)}")
print(f"✅ 已使用图片数量: {len(used_images)}")
print(f"🗑 未使用图片数量: {len(unused_images)}\n")

import stat

failed = []

for img in unused_images:
    print(img)
    if not DRY_RUN:
        try:
            img.chmod(stat.S_IWRITE)
            img.unlink()
        except Exception as e:
            failed.append(img)

if failed:
    print("\n❌ 以下文件删除失败（可能被占用）：")
    for f in failed:
        print(f)

