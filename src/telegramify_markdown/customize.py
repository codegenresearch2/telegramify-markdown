import emoji

class Symbol:
    head_level_1 = emoji.emojize(":pushpin:")  # 📌
    head_level_2 = emoji.emojize(":pencil:")  # ✏
    head_level_3 = emoji.emojize(":books:")  # 📚
    head_level_4 = emoji.emojize(":bookmark:")  # 📒
    image = "🖼"
    link = "🔗"
    strict_markdown = True  # Enable strict markdown mode

markdown_symbol = Symbol()