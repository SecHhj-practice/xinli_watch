# emotion_card.py
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from io import BytesIO
import os


def generate_emotion_card(emotion: str, quote: str) -> BytesIO:
    """
    生成一张情绪卡片图片（800x400）

    参数:
        emotion: 情绪名称，如 "快乐"、"悲伤"、"焦虑" 等
        quote: 一句话鼓励/描述，显示在卡片下方

    返回:
        BytesIO 对象，可直接用于 st.image() 或下载按钮
    """
    # 卡片尺寸
    width, height = 800, 400

    # 根据情绪选择背景渐变颜色和 emoji
    emotion_config = {
        "快乐": {"gradient_start": (255, 230, 150), "gradient_end": (255, 200, 100), "emoji": "😊"},
        "平静": {"gradient_start": (180, 220, 200), "gradient_end": (140, 200, 180), "emoji": "😌"},
        "焦虑": {"gradient_start": (240, 200, 180), "gradient_end": (220, 170, 150), "emoji": "😟"},
        "悲伤": {"gradient_start": (180, 200, 230), "gradient_end": (150, 180, 220), "emoji": "😢"},
        "愤怒": {"gradient_start": (240, 180, 170), "gradient_end": (220, 150, 140), "emoji": "😤"}
    }

    # 默认配置（如果情绪不在预设中）
    config = emotion_config.get(emotion,
                                {"gradient_start": (200, 220, 240), "gradient_end": (170, 200, 230), "emoji": "🌸"})

    # 创建渐变背景
    image = Image.new("RGB", (width, height), color=config["gradient_start"])
    draw = ImageDraw.Draw(image)

    # 手动绘制垂直渐变（PIL 没有直接渐变函数）
    for y in range(height):
        ratio = y / height
        r = int(config["gradient_start"][0] * (1 - ratio) + config["gradient_end"][0] * ratio)
        g = int(config["gradient_start"][1] * (1 - ratio) + config["gradient_end"][1] * ratio)
        b = int(config["gradient_start"][2] * (1 - ratio) + config["gradient_end"][2] * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # 添加半透明圆角矩形装饰
    overlay = Image.new("RGBA", (width, height), (255, 255, 255, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    overlay_draw.rounded_rectangle(
        [(40, 40), (width - 40, height - 40)],
        radius=30,
        fill=(255, 255, 255, 30),
        outline=(255, 255, 255, 80),
        width=2
    )
    image = image.convert("RGBA")
    image.paste(overlay, (0, 0), overlay)
    image = image.convert("RGB")
    draw = ImageDraw.Draw(image)

    # ========== 加载中文字体（自动回退） ==========
    font_emoji = None  # emoji 用默认字体即可
    font_quote = None
    font_emotion = None

    # 尝试的字体路径列表（按优先级）
    font_paths = [
        os.path.join(os.path.dirname(__file__), "fonts", "SourceHanSansSC-Regular.otf"),
        "fonts/SourceHanSansSC-Regular.otf",
        "C:/Windows/Fonts/msyh.ttc",  # 微软雅黑
        "C:/Windows/Fonts/simhei.ttf",  # 黑体
        "C:/Windows/Fonts/simsun.ttc",  # 宋体
        "/System/Library/Fonts/PingFang.ttc",  # macOS 苹方
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"  # Linux 备用
    ]

    font_path = None
    for path in font_paths:
        if os.path.exists(path):
            font_path = path
            break

    try:
        if font_path:
            # 主标题字体（情绪名称）
            font_emotion = ImageFont.truetype(font_path, 80)
            # 引用文字字体
            font_quote = ImageFont.truetype(font_path, 32)
        else:
            # 如果找不到中文字体，使用默认字体（可能会显示方框，但至少不会崩溃）
            font_emotion = ImageFont.load_default()
            font_quote = ImageFont.load_default()
    except:
        font_emotion = ImageFont.load_default()
        font_quote = ImageFont.load_default()

    # ========== 绘制内容 ==========

    # 1. 顶部 emoji
    emoji_text = config["emoji"]
    # 用默认字体绘制 emoji（PIL 的默认字体支持 emoji）
    try:
        emoji_font = ImageFont.truetype("seguiemj.ttf", 100) if os.path.exists(
            "C:/Windows/Fonts/seguiemj.ttf") else font_emotion
    except:
        emoji_font = font_emotion

    bbox = draw.textbbox((0, 0), emoji_text, font=emoji_font)
    emoji_width = bbox[2] - bbox[0]
    draw.text(
        ((width - emoji_width) // 2, 50),
        emoji_text,
        fill=(60, 60, 60),
        font=emoji_font
    )

    # 2. 情绪名称（如“今天的心情：快乐”）
    emotion_display = f"「{emotion}」"
    bbox = draw.textbbox((0, 0), emotion_display, font=font_emotion)
    text_width = bbox[2] - bbox[0]
    draw.text(
        ((width - text_width) // 2, 150),
        emotion_display,
        fill=(50, 50, 50),
        font=font_emotion
    )

    # 3. 引用文字（自动换行）
    quote_lines = []
    max_chars_per_line = 20
    if len(quote) > max_chars_per_line:
        # 简单按字符数拆分
        for i in range(0, len(quote), max_chars_per_line):
            quote_lines.append(quote[i:i + max_chars_per_line])
    else:
        quote_lines = [quote]

    y_offset = 250
    for line in quote_lines:
        bbox = draw.textbbox((0, 0), line, font=font_quote)
        line_width = bbox[2] - bbox[0]
        draw.text(
            ((width - line_width) // 2, y_offset),
            line,
            fill=(40, 40, 40),
            font=font_quote
        )
        y_offset += 45

    # 4. 底部装饰文字
    footer_text = "—— 心语 · 你的情绪树洞"
    try:
        font_small = ImageFont.truetype(font_path, 20) if font_path else ImageFont.load_default()
    except:
        font_small = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), footer_text, font=font_small)
    footer_width = bbox[2] - bbox[0]
    draw.text(
        ((width - footer_width) // 2, height - 50),
        footer_text,
        fill=(100, 100, 100),
        font=font_small
    )

    # 保存为 BytesIO
    img_bytes = BytesIO()
    image.save(img_bytes, format="PNG")
    img_bytes.seek(0)
    return img_bytes


# 测试函数
if __name__ == "__main__":
    img = generate_emotion_card("快乐", "今天状态不错，继续保持哦！")
    with open("test_card.png", "wb") as f:
        f.write(img.getbuffer())
    print("测试卡片已保存为 test_card.png")
