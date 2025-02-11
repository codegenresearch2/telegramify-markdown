import emoji
import os

class Symbol:
    head_level_1 = emoji.emojize(":pushpin:")
    head_level_2 = emoji.emojize(":pencil:")
    head_level_3 = emoji.emojize(":books:")
    head_level_4 = emoji.emojize(":bookmark:")
    image = "🖼"
    link = "🔗"

markdown_symbol = Symbol()

# Set the TELEGRAM_BOT_TOKEN environment variable for the tests
os.environ['TELEGRAM_BOT_TOKEN'] = 'your_token_here'