import os
import telegramify_markdown
from telegramify_markdown.customize import markdown_symbol

# Check if the TELEGRAM_BOT_TOKEN environment variable is set
if 'TELEGRAM_BOT_TOKEN' not in os.environ:
    raise EnvironmentError("The TELEGRAM_BOT_TOKEN environment variable is not set. Please set it to proceed.")

markdown_symbol.head_level_1 = "📌"  # Customizing the head level 1 symbol
markdown_symbol.link = "🔗"  # Customizing the link symbol
md = """
**Bold text**
*Italic text*
~~Strikethrough text~~
"""
converted = telegramify_markdown.convert(md)
print(converted)