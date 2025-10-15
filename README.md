# 太鼓之达人称号管理系统

这个项目用于抓取、存储和可视化太鼓之达人游戏的称号信息。

## 功能特性

- 📊 从官方 Wiki 抓取称号数据
- 💾 使用 SQLite 数据库存储称号信息
- 🎨 生成精美的称号信息图片
- 🔍 支持按名称和稀有度颜色查询

## 安装依赖

```bash
pip install -e .
```

或者手动安装依赖：

```bash
pip install beautifulsoup4 lxml requests pillow
```

## 使用方法

### 1. 抓取并存储称号数据

首先运行 `main.py` 来抓取称号数据并存储到数据库：

```bash
python main.py
```

这将：
- 从 Wiki 抓取所有称号数据
- 创建/更新 SQLite 数据库 `taiko_titles.db`
- 显示数据统计信息

### 2. 生成称号图片

使用 `image_generator.py` 中的接口来生成称号信息图片。

#### 接口说明

```python
from image_generator import generate_titles_images

# 函数签名
generate_titles_images(
    title_name: Optional[str] = None,     # 称号名称（可选）
    rarity_color: Optional[str] = None,   # 稀有度颜色（可选）
    output_dir: str = "output"            # 输出目录（默认为 "output"）
) -> List[str]                             # 返回生成的图片路径列表
```

#### 使用示例

**示例 1：根据称号名称生成图片**

```python
from image_generator import generate_titles_images

# 生成所有名为 "太鼓の達人" 的称号图片（包括所有稀有度版本）
images = generate_titles_images(title_name="太鼓の達人")
print(f"生成了 {len(images)} 张图片")
```

**示例 2：根据稀有度颜色生成图片**

```python
# 生成所有金色稀有度的称号图片
images = generate_titles_images(rarity_color="#FFD700")
```

**示例 3：同时指定称号名称和稀有度颜色**

```python
# 生成名为 "太鼓の達人" 且稀有度为金色的称号图片
images = generate_titles_images(
    title_name="太鼓の達人", 
    rarity_color="#FFD700"
)
```

**示例 4：指定输出目录**

```python
# 将图片输出到自定义目录
images = generate_titles_images(
    title_name="初心者",
    output_dir="my_images"
)
```

### 3. 运行示例代码

查看 `example_usage.py` 获取更多使用示例：

```bash
python example_usage.py
```

## 生成的图片信息

每张图片都会包含以下信息：

- **称号名称**：称号的完整名称（大字体显示）
- **是否可获得**：显示该称号当前是否可以获得
  - ✅ 绿色 "可获得: 是"
  - ❌ 红色 "可获得: 否"
- **稀有度颜色**：显示稀有度颜色的色块和颜色值
- **获得条件**：详细的获取条件说明
- **提示信息**：额外的提示说明（如果有）

## 图片输出

- 默认输出到 `output/` 目录
- 图片格式：PNG
- 文件名格式：`{称号名称}_{序号}.png`
- 如果同一个称号有多个版本（不同稀有度或获取条件），会生成多张图片

## 数据库结构

`taiko_titles.db` 包含一个 `titles` 表：

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| title_name | TEXT | 称号名称 |
| is_available | INTEGER | 是否可获得 (1: 是, 0: 否) |
| rarity_color | TEXT | 稀有度颜色 |
| obtain_condition | TEXT | 获得条件 |
| tips | TEXT | 提示信息 |
| created_at | TEXT | 创建时间 |
| updated_at | TEXT | 更新时间 |

## 常见稀有度颜色

- `#FFFFFF` 或 `white` - 白色（普通）
- `#C0C0C0` 或 `silver` - 银色
- `#FFD700` 或 `gold` - 金色
- `#ADD8E6` 或 `lightblue` - 浅蓝色
- `#EE82EE` 或 `violet` - 紫色

## 注意事项

1. 首次使用前必须先运行 `main.py` 抓取数据
2. 生成图片需要日文字体支持，程序会自动查找 Windows 系统中的日文字体
3. 如果找不到合适的字体，会使用默认字体（可能无法正确显示日文）
4. 输出目录会自动创建

## 项目文件说明

- `main.py` - 数据抓取和数据库管理
- `image_generator.py` - 图片生成接口
- `example_usage.py` - 使用示例
- `taiko_titles.db` - SQLite 数据库（运行后生成）
- `output/` - 默认图片输出目录（运行后生成）

## 许可证

MIT License
