import os
from typing import Union

import mistletoe
from mistletoe.block_token import BlockToken, ThematicBreak
from mistletoe.markdown_renderer import LinkReferenceDefinition
from mistletoe.span_token import SpanToken
from telebot import formatting

from .render import TelegramMarkdownRenderer


def _update_text(token: Union[SpanToken, BlockToken]):\n    """Update the text contents of a span token and its children.\n    `InlineCode` tokens are left unchanged."""\n    if isinstance(token, ThematicBreak):\n        token.line = formatting.escape_markdown("————————") \n    elif isinstance(token, LinkReferenceDefinition):\n        pass\n    else:\n        assert hasattr(token, 'content'), f"Token {token} has no content attribute"\n        token.content = formatting.escape_markdown(token.content)\n

def _update_block(token: BlockToken):\n    """Update the text contents of paragraphs and headings within this block,\n    and recursively within its children."""\n    if hasattr(token, 'children'):\n        # 解包所有的子节点\n        for child in token.children:\n            _update_block(child)\n    else:\n        _update_text(token)\n

def convert(content: str):\n    with TelegramMarkdownRenderer() as renderer:\n        document = mistletoe.Document(content)\n        _update_block(document)\n        result = renderer.render(document)\n    return result