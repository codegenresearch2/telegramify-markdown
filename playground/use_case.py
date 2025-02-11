import os
import telegramify_markdown
from telegramify_markdown.customize import markdown_symbol

# Check if the TELEGRAM_BOT_TOKEN environment variable is set
if 'TELEGRAM_BOT_TOKEN' not in os.environ:
    print("Warning: The TELEGRAM_BOT_TOKEN environment variable is not set. Some functionalities may be limited.")
    # Optionally, you can set a default value or skip the execution of relevant parts of the code
    # For example, you could set os.environ['TELEGRAM_BOT_TOKEN'] = 'default_token'
    # or simply pass without executing the rest of the code that depends on this variable
    # continue  # Uncomment this line if you want to skip the rest of the code
else:
    markdown_symbol.head_level_1 = "📌"  # Customizing the head level 1 symbol
    markdown_symbol.link = "🔗"  # Customizing the link symbol
    md = """
    **Bold text**
    *Italic text*
    ~~Strikethrough text~~
    """
    converted = telegramify_markdown.convert(md)
    print(converted)