import emoji

class Symbol(object):
    head_level_1 = emoji.emojize(":pushpin:")
    head_level_2 = emoji.emojize(":pencil:")
    head_level_3 = emoji.emojize(":books:")
    head_level_4 = emoji.emojize(":bookmark:")
    image = "🖼"
    link = "🔗"

def markdownify(text, symbol):
    strong_text = f"*{symbol.head_level_1}*strong text*{symbol.head_level_1}*"
    formatted_text = text.replace("**", strong_text)
    return formatted_text

markdown_symbol = Symbol()

In this rewritten code, the `markdownify` function is introduced to simplify the markdown conversion process. The function takes a text and symbol object as inputs and replaces `**` with the strict markdown handling for strong text, as specified by the user's preference. This ensures consistent formatting across render methods. The symbol object is created as before to maintain the same symbols used in the original code.