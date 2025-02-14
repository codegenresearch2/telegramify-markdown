from typing import Iterable

from mistletoe import block_token, span_token
from mistletoe.markdown_renderer import MarkdownRenderer, LinkReferenceDefinition, Fragment
from telebot import formatting
from .customize import markdown_symbol

class TelegramMarkdownRenderer(MarkdownRenderer):

    def render_heading(self, token: block_token.Heading, max_line_length: int) -> Iterable[str]:
        line = "#" * token.level + " "
        text = ''.join(self.span_to_lines(token.children, max_line_length=max_line_length))
        line += formatting.escape_markdown(text)
        return [line]

    def render_fenced_code_block(self, token: block_token.BlockCode, max_line_length: int) -> Iterable[str]:
        indentation = " " * token.indentation
        yield indentation + "" + token.info_string
        yield from self.prefix_lines(token.content.split("\n"), indentation)
        yield indentation + ""

    def render_inline_code(self, token: span_token.InlineCode) -> Iterable[Fragment]:
        return self.embed_span(Fragment("`"), token.children, Fragment("`"))

    def render_block_code(self, token: block_token.BlockCode, max_line_length: int) -> Iterable[str]:
        return [formatting.mcode(token.content, escape=False)]

    def render_setext_heading(self, token: block_token.SetextHeading, max_line_length: int) -> Iterable[str]:
        yield from self.span_to_lines(token.children, max_line_length=max_line_length)
        yield "---"

    def render_emphasis(self, token: span_token.Emphasis) -> Iterable[Fragment]:
        return self.embed_span(Fragment("*"), token.children)

    def render_strong(self, token: span_token.Strong) -> Iterable[Fragment]:
        return self.embed_span(Fragment("**"), token.children)

    def render_strikethrough(self, token: span_token.Strikethrough) -> Iterable[Fragment]:
        return self.embed_span(Fragment("~~"), token.children)

    def render_list_item(self, token: block_token.ListItem, max_line_length: int) -> Iterable[str]:
        token.leader = "- "
        return super().render_list_item(token, max_line_length)

    def render_link_reference_definition(self, token: LinkReferenceDefinition) -> Iterable[Fragment]:
        yield from (Fragment(f"[{token.label}]: {token.dest} \"{token.title}\""),)

    def render_image(self, token: span_token.Image) -> Iterable[Fragment]:
        yield Fragment(f"![{token.title}]({token.src})")

    def render_link(self, token: span_token.Link) -> Iterable[Fragment]:
        return self.render_link_or_image(token, token.target)

    def render_link_or_image(self, token: span_token.SpanToken, target: str) -> Iterable[Fragment]:
        title = next(self.span_to_lines(token.children, max_line_length=20), "")
        yield Fragment(f"[{title}]({target})")

    def render_auto_link(self, token: span_token.AutoLink) -> Iterable[Fragment]:
        yield Fragment(f"<{token.children[0].content}>")

    def render_table(self, token: block_token.Table, max_line_length: int) -> Iterable[str]:
        fs = super().render_table(token, max_line_length)
        return ["\n".join(fs)]