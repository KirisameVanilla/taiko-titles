import requests
from bs4 import BeautifulSoup
import re

# 导入数据库操作模块
from taiko_titles_db import (
    init_database,
    save_title_to_db,
    query_all_titles,
    query_available_titles,
    query_duplicate_title_names,
    query_titles_by_name,
)


def fetch_and_store_titles():
    """抓取并存储称号数据"""
    url = r"https://wikiwiki.jp/taiko-fumen/%E4%BD%9C%E5%93%81/%E6%96%B0AC/%E6%AE%B5%E4%BD%8D%E3%83%BB%E7%A7%B0%E5%8F%B7%E3%81%AE%E4%B8%80%E8%A6%A7"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

    # 发送请求
    print("正在抓取数据...")
    resp = requests.get(url, headers=headers)
    resp.encoding = resp.apparent_encoding  # 处理日文乱码
    soup = BeautifulSoup(resp.text, "lxml")

    # 按层级查找
    tbody = (
        soup.find("div", class_="container-wrapper")
        .find("div", id="contents")
        .find("div", class_="column-center clearfix")
        .find("div", id="body")
        .find("div", id="content")
        .find("div", class_="h-scrollable")
        .find("table")
        .find("tbody")
    )

    # 检查找到的内容
    if not tbody:
        print("未找到目标内容")
        return

    rows = tbody.find_all("tr")
    print(f"找到 {len(rows)} 条称号数据")

    # 遍历所有行并保存到数据库
    for idx, row in enumerate(rows, 1):
        try:
            # 获取所有单元格
            cells = row.find_all("td")
            if len(cells) < 3:
                continue

            # 0: 看颜色是否是grey表示称号是否可获得
            # 1: 用于看颜色,表示称号的颜色(稀有度)
            # 2: 称号名称
            # 3: 称号获得条件
            # 4: 关于称号的提示,可能没有

            # 检查是否可获得
            availability_style = cells[0].attrs.get("style", "")
            is_available = 0 if "grey" in availability_style else 1

            # 获取稀有度颜色
            rarity_style = cells[1].attrs.get("style", "")
            rarity_color = ""
            match = re.search(r"background-color:\s*([^;]+)", rarity_style)
            if match:
                rarity_color = match.group(1).strip()

            # 获取称号名称
            title_name = cells[2].get_text(strip=True)

            # 获取获得条件
            obtain_condition = cells[3].get_text(strip=True) if len(cells) > 3 else ""

            # 获取提示信息
            tips = cells[4].get_text(strip=True) if len(cells) > 4 else ""

            # 保存到数据库
            save_title_to_db(
                title_name, is_available, rarity_color, obtain_condition, tips
            )

        except Exception as e:
            print(f"处理第 {idx} 行时出错: {e}")
            continue

    print("数据抓取并存储完成!")


# 主程序
if __name__ == "__main__":
    # 初始化数据库
    init_database()

    # 抓取并存储数据
    fetch_and_store_titles()

    # 示例查询
    print("\n" + "=" * 50)
    print("数据库统计:")
    all_titles = query_all_titles()
    print(f"总称号数: {len(all_titles)}")

    available_titles = query_available_titles()
    print(f"可获得称号数: {len(available_titles)}")

    print("\n前5个称号示例:")
    for title in all_titles[:5]:
        print(
            f"ID: {title[0]}, 名称: {title[1]}, 可获得: {'是' if title[2] else '否'}, 颜色: {title[3]}"
        )

    # 查询有多个版本的称号
    print("\n有多个版本（不同稀有度或达成条件）的称号:")
    duplicates = query_duplicate_title_names()
    if duplicates:
        print(f"找到 {len(duplicates)} 个有多个版本的称号")
        for dup in duplicates[:5]:  # 只显示前5个
            print(f"  称号名称: {dup[0]}")
            print(f"  版本数量: {dup[1]}")
            # 显示该称号的所有版本详情
            versions = query_titles_by_name(dup[0])
            for v in versions:
                condition_preview = v[4][:30] + "..." if len(v[4]) > 30 else v[4]
                print(
                    f"    - ID: {v[0]}, 颜色: {v[3]}, 可获得: {'是' if v[2] else '否'}, 条件: {condition_preview}"
                )
            print()
    else:
        print("  没有找到同名不同版本的称号")

    print("=" * 50)
