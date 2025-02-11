import os
import emoji

class Symbol:
    head_level_1 = emoji.emojize(":pushpin:")
    head_level_2 = emoji.emojize(":pencil:")
    head_level_3 = emoji.emojize(":books:")
    head_level_4 = emoji.emojize(":bookmark:")
    image = "🖼"
    link = "🔗"

markdown_symbol = Symbol()

# Check for the presence of the TELEGRAM_BOT_TOKEN environment variable
if 'TELEGRAM_BOT_TOKEN' not in os.environ:
    raise ValueError("The TELEGRAM_BOT_TOKEN environment variable is not set. Please set it to run the tests.")