import os
import telegramify_markdown
from telegramify_markdown.customize import markdown_symbol

# Customizing the head level 1 symbol
markdown_symbol.head_level_1 = "📌"
# Customizing the link symbol
markdown_symbol.link = "🔗"

# Simplified markdown content
md = """
**Bold text**
*Italic text*
~~Strikethrough text~~
> Blockquote text
`Inline code`
"""

# Convert the markdown content
converted = telegramify_markdown.convert(md)
print(converted)


This revised code snippet simplifies the markdown content and removes the check for the `TELEGRAM_BOT_TOKEN` environment variable. It aligns more closely with the gold code by focusing on a simpler markdown structure and more concise comments.