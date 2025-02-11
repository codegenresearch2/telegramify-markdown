import os
from typing import Union

import mistletoe
from mistletoe.block_token import BlockToken, ThematicBreak
from mistletoe.markdown_renderer import LinkReferenceDefinition
from mistletoe.span_token import SpanToken
from telebot import formatting

from .render import TelegramMarkdownRenderer


def markdownify(text: str) -> str:
    """
    Escape special markdown characters in the given text.
    Characters being escaped: '_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!'
    """
    return formatting.escape_markdown(text)


def _update_text(token: Union[SpanToken, BlockToken]):
    """
    Update the text contents of a span token and its children.
    InlineCode tokens are left unchanged.
    """
    if isinstance(token, ThematicBreak):
        token.line = formatting.escape_markdown("————————")
    elif isinstance(token, LinkReferenceDefinition):
        pass
    else:
        assert hasattr(token, "content"), f"Token {token} has no content attribute"
        token.content = markdownify(token.content)


def _update_block(token: BlockToken):
    """
    Update the text contents of paragraphs and headings within this block,
    and recursively within its children.
    """
    if hasattr(token, "children"):
        for child in token.children:
            _update_block(child)
    else:
        _update_text(token)


def convert(content: str, test_mode: bool = False) -> str:
    """
    Convert the given markdown content to a format suitable for Telegram.
    
    Args:
        content (str): The markdown content to be converted.
        test_mode (bool): If True, bypasses the environment variable check.
    
    Returns:
        str: The converted markdown content.
    """
    if not test_mode and 'TELEGRAM_BOT_TOKEN' not in os.environ:
        raise EnvironmentError("The TELEGRAM_BOT_TOKEN environment variable is not set. Please set it to proceed.")
    
    with TelegramMarkdownRenderer() as renderer:
        document = mistletoe.Document(content)
        _update_block(document)
        result = renderer.render(document)
    return result