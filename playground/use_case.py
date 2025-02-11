import os
import telegramify_markdown
from telegramify_markdown.customize import markdown_symbol

# Ensure the bot token is set
if 'TELEGRAM_BOT_TOKEN' not in os.environ:
    raise ValueError("The TELEGRAM_BOT_TOKEN environment variable is not set. Please set it to run this script.")

# Set custom symbols
markdown_symbol.head_level_1 = "📌"
markdown_symbol.link = "🔗"

# Define the markdown content
md = """
# Heading Level 1
## Heading Level 2
### Heading Level 3
**Bold text**
*Italic text*
~~Strikethrough text~~
"""

# Convert the markdown content
converted = telegramify_markdown.convert(md)
print(converted)