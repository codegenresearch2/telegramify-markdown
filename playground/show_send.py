import os
from dotenv import load_dotenv
from telebot import TeleBot
import telegramify_markdown

md = """
- [x] This is a completed task
- [ ] This is an incomplete task

In all other places characters '_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!' must be escaped with the preceding character '\\'.

*bold \\*text*
_italic \\*text_
__underline__
~strikethrough~
||spoiler||
*bold _italic bold ~italic bold strikethrough ||italic bold strikethrough spoiler||~ __underline italic bold___ bold*
__underline italic bold___
[inline URL](http://www.example.com/)
[inline mention of a user](tg://user?id=123456789)
![👍](tg://emoji?id=5368324170671202286)
`inline fixed-width code`

# This is a heading
## This is a sub-heading

> Block quotation started
> Block quotation continued
> The last line of the block quotation**

1. This is an ordered list item
2. This is another ordered list item

- This is an unordered list item
- This is another unordered list item

lua
-- This is a code block written in Lua
print("Hello from Lua!")
"""

converted = telegramify_markdown.convert(md)
print(converted)

load_dotenv()
telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "default_token")
chat_id = os.getenv("TELEGRAM_CHAT_ID", "default_chat_id")

bot = TeleBot(telegram_bot_token)
bot.send_message(
    chat_id,
    converted,
    parse_mode="MarkdownV2"
)