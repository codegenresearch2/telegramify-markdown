import os
from dotenv import load_dotenv
from telebot import TeleBot

import telegramify_markdown

md = """
- [x] Ensure all special characters are escaped properly.
- [ ] Add support for task lists with checkboxes.
- [ ] Include ordered and unordered lists.
- [ ] Format block quotes and code blocks correctly.
- [ ] Ensure inline code is presented properly.

In all other places, characters '_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!' must be escaped with the preceding character '\\'.

*bold *text*
_italic *text_
__underline__
~strikethrough~
||spoiler||
*bold _italic bold ~italic bold strikethrough ||italic bold strikethrough spoiler||~ __underline italic bold___ bold*
__underline italic bold___
[inline URL](http://www.example.com/)
[inline mention of a user](tg://user?id=123456789)
![👍](tg://emoji?id=5368324170671202286)
`inline fixed-width code`


pre-formatted fixed-width code block


lua
pre-formatted fixed-width code block written in the Python programming language


>Block quotation started
>Block quotation continued
>The last line of the block quotation**
>The second block quotation started right after the previous\r
>The third block quotation started right after the previous
"""

converted = telegramify_markdown.convert(md)
print(converted)

# Ensure the environment variable is set
load_dotenv()
telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN", None)
chat_id = os.getenv("TELEGRAM_CHAT_ID", None)

if telegram_bot_token is None:
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable is not set. Please set it to run the bot.")

if chat_id is None:
    raise ValueError("TELEGRAM_CHAT_ID environment variable is not set. Please set it to send messages.")

bot = TeleBot(telegram_bot_token)
bot.send_message(
    chat_id,
    converted,
    parse_mode="MarkdownV2"
)