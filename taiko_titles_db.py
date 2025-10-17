import sqlite3
from datetime import datetime

# 数据库设置
DB_NAME = "taiko_titles.db"


def init_database():
    """初始化数据库，创建表结构"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # 创建称号表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS titles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title_name TEXT NOT NULL,
            is_available INTEGER NOT NULL,  -- 1: 可获得, 0: 不可获得
            rarity_color TEXT NOT NULL,  -- 稀有度颜色
            obtain_condition TEXT NOT NULL,  -- 获得条件
            tips TEXT,  -- 提示信息
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            UNIQUE(title_name, rarity_color, obtain_condition)  -- 称号文本+稀有度+达成条件组合唯一
        )
    """)

    conn.commit()
    conn.close()
    print(f"数据库 {DB_NAME} 初始化完成")


def save_title_to_db(title_name, is_available, rarity_color, obtain_condition, tips=""):
    """保存称号数据到数据库"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    now = datetime.now().isoformat()

    # 检查是否已存在相同称号（称号文本+稀有度颜色+达成条件组合）
    cursor.execute(
        "SELECT id FROM titles WHERE title_name = ? AND rarity_color = ? AND obtain_condition = ?",
        (title_name, rarity_color, obtain_condition),
    )
    existing = cursor.fetchone()

    if existing:
        # 更新现有记录
        cursor.execute(
            """
            UPDATE titles 
            SET is_available = ?, tips = ?, updated_at = ?
            WHERE title_name = ? AND rarity_color = ? AND obtain_condition = ?
        """,
            (is_available, tips, now, title_name, rarity_color, obtain_condition),
        )
        print(
            f"更新称号: {title_name} (颜色: {rarity_color}, 条件: {obtain_condition[:20]}...)"
        )
    else:
        # 插入新记录
        cursor.execute(
            """
            INSERT INTO titles (title_name, is_available, rarity_color, 
                              obtain_condition, tips, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (title_name, is_available, rarity_color, obtain_condition, tips, now, now),
        )
        print(
            f"新增称号: {title_name} (颜色: {rarity_color}, 条件: {obtain_condition[:20]}...)"
        )

    conn.commit()
    conn.close()


def query_all_titles():
    """查询所有称号"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM titles ORDER BY id")
    titles = cursor.fetchall()

    conn.close()
    return titles


def query_available_titles():
    """查询可获得的称号"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM titles WHERE is_available = 1 ORDER BY id")
    titles = cursor.fetchall()

    conn.close()
    return titles


def query_titles_by_color(color):
    """根据稀有度颜色查询称号"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM titles WHERE rarity_color = ? ORDER BY id", (color,))
    titles = cursor.fetchall()

    conn.close()
    return titles


def query_duplicate_title_names():
    """查询有多个版本（不同稀有度或达成条件）的称号名称"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT title_name, COUNT(*) as count, 
               GROUP_CONCAT(rarity_color || '|' || substr(obtain_condition, 1, 20)) as variants
        FROM titles
        GROUP BY title_name
        HAVING COUNT(*) > 1
        ORDER BY count DESC
    """)
    duplicates = cursor.fetchall()

    conn.close()
    return duplicates


def query_titles_by_name(title_name):
    """根据称号名称查询所有版本（不同稀有度或达成条件）"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM titles WHERE title_name = ? ORDER BY rarity_color, obtain_condition",
        (title_name,),
    )
    titles = cursor.fetchall()

    conn.close()
    return titles
