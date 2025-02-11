import os
import telegramify_markdown
from telegramify_markdown.customize import markdown_symbol

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