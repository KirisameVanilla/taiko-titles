"""
称号图片生成 API 接口

这是一个简单易用的接口，用于根据称号名称和稀有度颜色生成图片。
如果找到多条记录，会为每条记录都生成图片。
"""

from image_generator import generate_titles_images
from typing import List, Optional


def generate_title_images(
    title_name: Optional[str] = None,
    rarity_color: Optional[str] = None,
    output_dir: str = "output"
) -> dict:
    """
    生成称号图片的主接口
    
    参数:
        title_name: 称号名称（可选）
        rarity_color: 稀有度颜色，如 "#FFD700" 或 "gold"（可选）
        output_dir: 输出目录（默认为 "output"）
    
    返回:
        包含生成结果的字典:
        {
            "success": bool,           # 是否成功
            "count": int,              # 生成的图片数量
            "images": List[str],       # 图片路径列表
            "message": str             # 消息说明
        }
    
    示例:
        # 生成名为 "太鼓の達人" 的所有称号图片
        result = generate_title_images(title_name="太鼓の達人")
        
        # 生成金色稀有度的所有称号图片
        result = generate_title_images(rarity_color="#FFD700")
        
        # 同时指定名称和颜色
        result = generate_title_images(
            title_name="太鼓の達人", 
            rarity_color="#FFD700"
        )
    """
    try:
        # 调用图片生成函数
        images = generate_titles_images(
            title_name=title_name,
            rarity_color=rarity_color,
            output_dir=output_dir
        )
        
        if not images:
            return {
                "success": False,
                "count": 0,
                "images": [],
                "message": "未找到符合条件的称号"
            }
        
        return {
            "success": True,
            "count": len(images),
            "images": images,
            "message": f"成功生成 {len(images)} 张图片"
        }
        
    except Exception as e:
        return {
            "success": False,
            "count": 0,
            "images": [],
            "message": f"生成图片时出错: {str(e)}"
        }


# 命令行接口
if __name__ == "__main__":
    import sys
    
    print("=" * 70)
    print("太鼓之达人称号图片生成器")
    print("=" * 70)
    
    # 检查命令行参数
    if len(sys.argv) > 1:
        # 从命令行参数获取
        title_name = None
        rarity_color = None
        output_dir = "output"
        
        i = 1
        while i < len(sys.argv):
            if sys.argv[i] == "--title" and i + 1 < len(sys.argv):
                title_name = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == "--color" and i + 1 < len(sys.argv):
                rarity_color = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == "--output" and i + 1 < len(sys.argv):
                output_dir = sys.argv[i + 1]
                i += 2
            else:
                i += 1
        
        result = generate_title_images(title_name, rarity_color, output_dir)
    else:
        # 交互式输入
        print("\n请输入查询条件（留空表示不限制该条件）:")
        title_name = input("称号名称: ").strip() or None
        rarity_color = input("稀有度颜色 (如 #FFD700): ").strip() or None
        output_dir = input("输出目录 (默认 output): ").strip() or "output"
        
        print("\n正在生成图片...")
        result = generate_title_images(title_name, rarity_color, output_dir)
    
    # 显示结果
    print("\n" + "=" * 70)
    print("生成结果:")
    print("=" * 70)
    print(f"状态: {'✅ 成功' if result['success'] else '❌ 失败'}")
    print(f"消息: {result['message']}")
    
    if result['success'] and result['images']:
        print(f"\n生成的图片 ({result['count']} 张):")
        for i, img_path in enumerate(result['images'], 1):
            print(f"  {i}. {img_path}")
    
    print("=" * 70)
