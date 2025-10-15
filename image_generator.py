import sqlite3
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from typing import List, Tuple, Optional

DB_NAME = "taiko_titles.db"


def query_titles_by_name_and_color(
    title_name: Optional[str] = None, rarity_color: Optional[str] = None
) -> List[Tuple]:
    """
    根据称号名称和/或稀有度颜色查询称号

    参数:
        title_name: 称号名称（可选，使用模糊匹配）
        rarity_color: 稀有度颜色（可选）

    返回:
        符合条件的称号列表
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # 构建动态查询
    query = "SELECT * FROM titles WHERE 1=1"
    params = []

    if title_name:
        # 使用 LIKE 进行模糊搜索
        query += " AND title_name LIKE ?"
        params.append(f"%{title_name}%")

    if rarity_color:
        query += " AND rarity_color = ?"
        params.append(rarity_color)

    query += " ORDER BY id"

    cursor.execute(query, params)
    titles = cursor.fetchall()

    conn.close()
    return titles


def wrap_text(text: str, font, max_width: int) -> List[str]:
    """将文本按指定宽度换行"""
    words = text
    lines = []
    current_line = ""

    for char in words:
        test_line = current_line + char
        bbox = font.getbbox(test_line)
        width = bbox[2] - bbox[0]

        if width <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = char

    if current_line:
        lines.append(current_line)

    return lines


def load_title_frame(rarity_color: str) -> Optional[Image.Image]:
    """
    根据稀有度颜色加载对应的称号框图片

    参数:
        rarity_color: 稀有度颜色（如 #ded523）

    返回:
        称号框图片，如果找不到则返回 None
    """
    # 清理颜色值作为文件名
    color_filename = rarity_color.lower().replace("#", "")
    frame_path = Path("resources") / f"#{color_filename}.png"

    if frame_path.exists():
        try:
            return Image.open(frame_path)
        except Exception as e:
            print(f"加载称号框失败 {frame_path}: {e}")
            return None
    else:
        print(f"未找到称号框: {frame_path}")
        return None


def generate_title_image(
    title_data: Tuple,
    output_path: str,
    width: int = 800,
    font_size_title: int = 32,
    font_size_body: int = 24,
) -> str:
    """
    生成单个称号信息图片

    参数:
        title_data: 数据库查询返回的称号数据元组
        output_path: 输出图片路径
        width: 图片宽度
        font_size_title: 标题字体大小（称号框内文字）
        font_size_body: 正文字体大小

    返回:
        生成的图片路径
    """
    # 解析数据
    # (id, title_name, is_available, rarity_color, obtain_condition, tips, created_at, updated_at)
    (
        title_id,
        title_name,
        is_available,
        rarity_color,
        obtain_condition,
        tips,
        created_at,
        updated_at,
    ) = title_data

    # 设置边距和间距
    padding = 40
    line_spacing = 15
    section_spacing = 30

    # 加载字体（优先使用 resources 文件夹中的字体）
    try:
        # 优先使用项目中的字体
        custom_font_path = Path("resources") / "FOT-大江戸勘亭流 Std E.otf"

        if custom_font_path.exists():
            font_title = ImageFont.truetype(str(custom_font_path), font_size_title)
            font_body = ImageFont.truetype(str(custom_font_path), font_size_body)
            font_small = ImageFont.truetype(str(custom_font_path), 20)
        else:
            # 备用：尝试系统字体
            font_paths = [
                "C:\\Windows\\Fonts\\msgothic.ttc",  # MS Gothic (支持日文)
                "C:\\Windows\\Fonts\\msmincho.ttc",  # MS Mincho
                "C:\\Windows\\Fonts\\yugothm.ttc",  # Yu Gothic Medium
                "C:\\Windows\\Fonts\\YuGothR.ttc",  # Yu Gothic Regular
                "C:\\Windows\\Fonts\\meiryo.ttc",  # Meiryo
            ]

            font_title = None
            font_body = None
            font_small = None

            for font_path in font_paths:
                if Path(font_path).exists():
                    font_title = ImageFont.truetype(font_path, font_size_title)
                    font_body = ImageFont.truetype(font_path, font_size_body)
                    font_small = ImageFont.truetype(font_path, 20)
                    break

            if font_title is None:
                # 如果找不到日文字体，使用默认字体
                font_title = ImageFont.load_default()
                font_body = ImageFont.load_default()
                font_small = ImageFont.load_default()
                print("警告: 未找到日文字体，使用默认字体")

    except Exception as e:
        print(f"加载字体时出错: {e}")
        font_title = ImageFont.load_default()
        font_body = ImageFont.load_default()
        font_small = ImageFont.load_default()

    # 加载称号框
    title_frame = load_title_frame(rarity_color)
    if not title_frame:
        return ""

    # 称号框尺寸（556x90）
    frame_width = title_frame.width
    frame_height = title_frame.height

    # 计算所需高度
    max_text_width = width - 2 * padding

    # 可取得状态
    availability_text = "可取得: " + ("是" if is_available else "否")
    availability_height = font_size_body + line_spacing

    # 取得条件
    condition_lines = wrap_text(obtain_condition, font_body, max_text_width)
    condition_height = (
        font_size_body + line_spacing + len(condition_lines) * (font_size_body + 10)
    )

    # 提示信息
    tips_height = 0
    if tips:
        tips_lines = wrap_text(tips, font_body, max_text_width)
        tips_height = (
            font_size_body + line_spacing + len(tips_lines) * (font_size_body + 10)
        )

    # 总高度（包含称号框 + 信息部分）
    total_height = (
        padding  # 顶部边距
        + frame_height  # 称号框高度
        + section_spacing  # 间距
        + availability_height  # 可获得状态
        + section_spacing
        + condition_height  # 获得条件
        + (section_spacing + tips_height if tips else 0)  # 提示信息
        + padding  # 底部边距
    )

    # 创建图片
    img = Image.new("RGB", (width, int(total_height)), color="white")
    draw = ImageDraw.Draw(img)

    # 绘制边框
    draw.rectangle(
        [(0, 0), (width - 1, total_height - 1)], outline=(200, 200, 200), width=2
    )

    # 当前Y坐标
    current_y = padding

    # 绘制称号框和称号文字
    if title_frame:
        # 将称号框居中放置
        frame_x = (width - frame_width) // 2
        frame_y = current_y

        # 粘贴称号框
        img.paste(
            title_frame,
            (frame_x, frame_y),
            title_frame if title_frame.mode == "RGBA" else None,
        )

        # 在称号框上半部分居中绘制称号文字
        # 计算文字宽度以居中
        bbox = font_title.getbbox(title_name)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # 文字位置：框的水平居中，垂直位置在框的上半部分（约1/4处）
        text_x = frame_x + (frame_width - text_width) // 2
        text_y = frame_y + frame_height - 68 - (text_height // 2)

        # 绘制黑色文字（无描边）
        draw.text((text_x, text_y), title_name, fill=(0, 0, 0), font=font_title)

        current_y += frame_height + section_spacing
    else:
        # 如果没有称号框，用原来的方式显示称号名称
        draw.text((padding, current_y), title_name, fill=(0, 0, 0), font=font_title)
        current_y += font_size_title + section_spacing

    # 绘制可获得状态
    availability_color = (0, 150, 0) if is_available else (150, 0, 0)
    draw.text(
        (padding, current_y), availability_text, fill=availability_color, font=font_body
    )
    current_y += availability_height + section_spacing

    # # 绘制稀有度颜色标签
    # draw.text((padding, current_y), f"稀有度: {rarity_color}", fill=(100, 100, 100), font=font_small)
    # current_y += font_size_body + section_spacing

    # 绘制取得条件
    draw.text((padding, current_y), "取得条件:", fill=(0, 0, 0), font=font_body)
    current_y += font_size_body + 10

    for line in condition_lines:
        line = (
            line.replace("おに", "鬼")
            .replace("ドンダフルコンボ", "全良")
            .replace("フルコンボ", "全連")
        )
        draw.text((padding + 20, current_y), line, fill=(50, 50, 50), font=font_body)
        current_y += font_size_body + 10

    # 绘制提示信息
    if tips:
        current_y += section_spacing
        draw.text((padding, current_y), "提示:", fill=(0, 0, 0), font=font_body)
        current_y += font_size_body + 10

        tips_lines = wrap_text(tips, font_body, max_text_width - 20)
        for line in tips_lines:
            draw.text(
                (padding + 20, current_y), line, fill=(100, 100, 100), font=font_body
            )
            current_y += font_size_body + 10

    # 保存图片
    img.save(output_path)
    print(f"图片已生成: {output_path}")

    return output_path


def generate_titles_images(
    title_name: Optional[str] = None,
    rarity_color: Optional[str] = None,
    output_dir: str = "output",
) -> List[str]:
    """
    根据称号名称和稀有度颜色生成图片

    参数:
        title_name: 称号名称（可选）
        rarity_color: 稀有度颜色（可选）
        output_dir: 输出目录

    返回:
        生成的图片路径列表
    """
    # 创建输出目录
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    # 查询符合条件的称号
    titles = query_titles_by_name_and_color(title_name, rarity_color)

    if not titles:
        print("未找到符合条件的称号")
        return []

    print(f"找到 {len(titles)} 个符合条件的称号")

    # 检查结果数量，只有小于5个时才生成图片
    if len(titles) >= 5:
        print(f"找到的结果数量 ({len(titles)}) 大于等于5个，不生成图片")
        print("请提供更精确的搜索条件以减少结果数量")
        return []

    # 为每个称号生成图片
    generated_images = []
    for idx, title_data in enumerate(titles, 1):
        # 生成文件名
        safe_title_name = "".join(
            c for c in title_data[1] if c.isalnum() or c in (" ", "_", "-")
        ).strip()
        safe_title_name = safe_title_name.replace(" ", "_")
        filename = f"{safe_title_name}_{idx}.png"
        output_file = output_path / filename

        # 生成图片
        image_path = generate_title_image(title_data, str(output_file))
        generated_images.append(image_path)

    return generated_images
