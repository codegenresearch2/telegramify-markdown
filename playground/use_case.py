import os
import telegramify_markdown
from telegramify_markdown.customize import markdown_symbol

# Set the environment variable if not already set
os.environ['TELEGRAM_BOT_TOKEN'] = os.environ.get('TELEGRAM_BOT_TOKEN', 'default_token')

# Customizing the head level 1 symbol
markdown_symbol.head_level_1 = "📌"
# Customizing the link symbol
markdown_symbol.link = "🔗"

# Markdown content with various formatting options
md = """
**Bold text** *Italic text* ~~Strikethrough text~~
"""

# Convert the markdown content
converted = telegramify_markdown.convert(md)
print(converted)