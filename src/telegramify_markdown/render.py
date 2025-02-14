from typing import Iterable

from mistletoe import block_token, span_token
from mistletoe.markdown_renderer import MarkdownRenderer, LinkReferenceDefinition, Fragment
from telebot import formatting
from .customize import markdown_symbol

class TelegramMarkdownRenderer(MarkdownRenderer):

    def render_heading(self, token: block_token.Heading, max_line_length: int) -> Iterable[str]:
        line = ""
        line += markdown_symbol.get_heading_symbol(token.level)
        text = next(self.span_to_lines(token.children, max_line_length=max_line_length), "")
        if text:
            line += " " + text
        if token.closing_sequence:
            line += " " + token.closing_sequence
        return [formatting.mbold(formatting.escape_markdown(line))]

    def render_fenced_code_block(self, token: block_token.BlockCode, max_line_length: int) -> Iterable[str]:
        indentation = " " * token.indentation
        yield indentation + formatting.escape_markdown(token.delimiter + token.info_string)
        yield from self.prefix_lines(token.content[:-1].split("\n"), indentation)
        yield indentation + formatting.escape_markdown(token.delimiter)

    def render_inline_code(self, token: span_token.InlineCode) -> Iterable[Fragment]:
        delimiter = '' if len(token.delimiter) == 3 else '`'
        return self.embed_span(
            Fragment(formatting.escape_markdown(delimiter + token.padding)),
            token.children,
            Fragment(formatting.escape_markdown(token.padding + delimiter))
        )

    def render_block_code(self, token: block_token.BlockCode, max_line_length: int) -> Iterable[str]:
        return [formatting.mcode(formatting.escape_markdown(token.content))]

    def render_setext_heading(self, token: block_token.SetextHeading, max_line_length: int) -> Iterable[str]:
        yield from self.span_to_lines(token.children, max_line_length=max_line_length)
        yield formatting.escape_markdown("——" * 5)

    def render_emphasis(self, token: span_token.Emphasis) -> Iterable[Fragment]:
        return self.embed_span(Fragment(formatting.escape_markdown("_")), token.children)

    def render_strong(self, token: span_token.Strong) -> Iterable[Fragment]:
        return self.embed_span(Fragment(formatting.escape_markdown("*")), token.children)

    def render_strikethrough(self, token: span_token.Strikethrough) -> Iterable[Fragment]:
        return self.embed_span(Fragment(formatting.escape_markdown("~")), token.children)

    def render_list_item(self, token: block_token.ListItem, max_line_length: int) -> Iterable[str]:
        token.leader = formatting.escape_markdown("⦁") + " "
        return super().render_list_item(token, max_line_length)

    def render_link_reference_definition(self, token: LinkReferenceDefinition) -> Iterable[Fragment]:
        yield from (Fragment(markdown_symbol.link + formatting.mlink(content=token.title if token.title else token.label, url=token.dest, escape=True)),)

    def render_image(self, token: span_token.Image) -> Iterable[Fragment]:
        yield Fragment(markdown_symbol.image)
        yield from self.render_link_or_image(token, token.src)

    def render_link(self, token: span_token.Link) -> Iterable[Fragment]:
        return self.render_link_or_image(token, token.target)

    def render_link_or_image(self, token: span_token.SpanToken, target: str) -> Iterable[Fragment]:
        title = next(self.span_to_lines(token.children, max_line_length=20), "")
        if token.dest_type == "uri" or token.dest_type == "angle_uri":
            yield Fragment(formatting.mlink(url=target, content=title, escape=True))
        elif token.dest_type == "full":
            yield from (Fragment(formatting.escape_markdown("[")), Fragment(token.label, wordwrap=True), Fragment(formatting.escape_markdown("]")))
        elif token.dest_type == "collapsed":
            yield Fragment(formatting.escape_markdown("[]"))

    def render_auto_link(self, token: span_token.AutoLink) -> Iterable[Fragment]:
        yield Fragment(formatting.escape_markdown("<") + token.children[0].content + formatting.escape_markdown(">"))

    def render_table(self, token: block_token.Table, max_line_length: int) -> Iterable[str]:
        fs = super().render_table(token, max_line_length)
        return [formatting.mcode(formatting.escape_markdown("\n".join(fs)))]