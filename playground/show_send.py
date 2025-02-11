import os
from dotenv import load_dotenv
from telebot import TeleBot

import telegramify_markdown

# Load environment variables from .env file
load_dotenv()

# Define the markdown content
md = """
# Heading 1
## Heading 2
### Heading 3
- [x] Task 1
- [ ] Task 2
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

# Inline code block
print("Hello, world!")



pre-formatted fixed-width code block


> Block quotation started
> Block quotation continued
> The last line of the block quotation

"""

# Convert the markdown content
converted = telegramify_markdown.convert(md)
print(converted)

# Retrieve the Telegram bot token and chat ID from the environment variables
telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
chat_id = os.getenv("TELEGRAM_CHAT_ID")

# Initialize the Telegram bot and send the message
bot = TeleBot(telegram_bot_token)
bot.send_message(
    chat_id,
    converted,
    parse_mode="MarkdownV2"
)