"""
使用图片生成接口的示例

这个文件展示了如何使用 image_generator.py 中的接口来生成称号图片
"""

from image_generator import generate_titles_images

# 示例 1: 根据称号名称生成图片
print("=" * 60)
print("示例 1: 根据称号名称生成图片")
print("=" * 60)

# 查询名为 "月下打人" 的所有称号（不同稀有度都会生成）
images = generate_titles_images(title_name="月下打人")
print(f"生成了 {len(images)} 张图片")
for img_path in images:
    print(f"  - {img_path}")


# 示例 2: 批量生成多个称号的图片
print("\n" + "=" * 60)
print("示例 2: 批量生成多个称号的图片")
print("=" * 60)

title_names = [
    "トロいか2000",
]
for title in title_names:
    print(f"\n生成称号: {title}")
    images = generate_titles_images(title_name=title)
    print(f"  生成了 {len(images)} 张图片")


print("\n所有示例执行完成！")
