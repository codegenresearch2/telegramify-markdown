import emoji

class Symbol(object):
    head_level_1 = emoji.emojize(":pushpin:")  # 📌
    head_level_2 = emoji.emojize(":pencil:")  # ✏
    head_level_3 = emoji.emojize(":books:")  # 📚
    head_level_4 = emoji.emojize(":bookmark:")  # 📒
    image = "🖼"
    link = "🔗"

# Define the strict_markdown variable outside of the class
markdown_symbol = Symbol()
strict_markdown = True