from typing import Union

import mistletoe
from mistletoe.block_token import BlockToken, ThematicBreak
from mistletoe.markdown_renderer import LinkReferenceDefinition
from mistletoe.span_token import SpanToken
from telebot import formatting

from .render import TelegramMarkdownRenderer


def markdownify(text: str):
    return formatting.escape_markdown(text)


def _update_text(token: Union[SpanToken, BlockToken]):
    """Update the text contents of a span token and its children.
    `InlineCode` tokens are left unchanged."""
    if isinstance(token, ThematicBreak):
        token.line = formatting.escape_markdown("————————")
    elif isinstance(token, LinkReferenceDefinition):
        pass
    else:
        assert hasattr(token, "content"), f"Token {token} has no content attribute"
        token.content = markdownify(token.content)


def _update_block(token: BlockToken):
    """Update the text contents of paragraphs and headings within this block,
    and recursively within its children."""
    if hasattr(token, "children"):
        # Unpack all children
        for child in token.children:
            _update_block(child)
    else:
        _update_text(token)


def convert(content: str):
    if 'TELEGRAM_BOT_TOKEN' not in os.environ:
        raise EnvironmentError("The TELEGRAM_BOT_TOKEN environment variable is not set.")
    
    with TelegramMarkdownRenderer() as renderer:
        document = mistletoe.Document(content)
        _update_block(document)
        result = renderer.render(document)
    return result