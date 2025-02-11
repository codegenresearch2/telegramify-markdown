import emoji

class Symbol(object):
    head_level_1 = emoji.emojize(":pushpin:")  # 📌
    head_level_2 = emoji.emojize(":pencil:")  # ✏
    head_level_3 = emoji.emojize(":books:")  # 📚
    head_level_4 = emoji.emojize(":bookmark:")  # 📒
    image = "🖼"
    link = "🔗"

# Ensure the TELEGRAM_BOT_TOKEN environment variable is set
if 'TELEGRAM_BOT_TOKEN' not in os.environ:
    raise ValueError("The TELEGRAM_BOT_TOKEN environment variable is not set. Please set it to run the tests.")

# Define the markdown_symbol variable outside of the class
markdown_symbol = Symbol()
strict_markdown = True