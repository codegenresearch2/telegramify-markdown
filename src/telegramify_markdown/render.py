from typing import Iterable

from mistletoe import block_token, span_token
from mistletoe.markdown_renderer import MarkdownRenderer, LinkReferenceDefinition, Fragment
from telebot import formatting

from .customize import markdown_symbol


class TelegramMarkdownRenderer(MarkdownRenderer):

    def render_heading(self, token: block_token.Heading, max_line_length: int) -> Iterable[str]:
        line = '' if token.level == 1 else ' ' if token.level == 2 else '  ' if token.level == 3 else '   '
        line += ''.join(self.span_to_lines(token.children, max_line_length=max_line_length))
        return [formatting.mbold(line, escape=False)]

    def render_fenced_code_block(self, token: block_token.BlockCode, max_line_length: int) -> Iterable[str]:
        indentation = ' ' * token.indentation
        yield indentation + token.delimiter + token.info_string
        yield from self.prefix_lines(token.content[:-1].split('\n'), indentation)
        yield indentation + token.delimiter

    def render_inline_code(self, token: span_token.InlineCode) -> Iterable[Fragment]:
        delimiter = token.delimiter * (3 if len(token.delimiter) == 1 else 1)
        return self.embed_span(Fragment(delimiter + token.padding + '\n'), token.children, Fragment(token.padding + delimiter))

    def render_block_code(self, token: block_token.BlockCode, max_line_length: int) -> Iterable[str]:
        return [formatting.mcode(token.content, escape=False)]

    def render_setext_heading(self, token: block_token.SetextHeading, max_line_length: int) -> Iterable[str]:
        yield from self.span_to_lines(token.children, max_line_length=max_line_length)
        yield formatting.escape_markdown('——' * 5)

    def render_emphasis(self, token: span_token.Emphasis) -> Iterable[Fragment]:
        return super().render_emphasis(token)

    def render_strong(self, token: span_token.Strong) -> Iterable[Fragment]:
        delimiter = '*' if token.delimiter == '*' else ''
        return self.embed_span(Fragment(delimiter * (1 if delimiter else 2)), token.children)

    def render_strikethrough(self, token: span_token.Strikethrough) -> Iterable[Fragment]:
        return self.embed_span(Fragment('~'), token.children)

    def render_list_item(self, token: block_token.ListItem, max_line_length: int) -> Iterable[str]:
        token.leader = formatting.escape_markdown(token.leader) + ' ' if str(token.leader).strip().endswith('.') else formatting.escape_markdown('⦁')
        return super().render_list_item(token, max_line_length)

    def render_link_reference_definition(self, token: LinkReferenceDefinition) -> Iterable[Fragment]:
        yield from (Fragment(markdown_symbol.link + formatting.mlink(content=token.title if token.title else token.label, url=token.dest, escape=True)))

    def render_image(self, token: span_token.Image) -> Iterable[Fragment]:
        yield Fragment(markdown_symbol.image)
        yield from self.render_link_or_image(token, token.src)

    def render_link(self, token: span_token.Link) -> Iterable[Fragment]:
        return self.render_link_or_image(token, token.target)

    def render_link_or_image(self, token: span_token.SpanToken, target: str) -> Iterable[Fragment]:
        title = ''.join(self.span_to_lines(token.children, max_line_length=20))
        if token.dest_type in ['uri', 'angle_uri']: yield Fragment(formatting.mlink(url=target, content=title, escape=True))
        elif token.dest_type == 'full': yield from (Fragment(formatting.escape_markdown('[')), Fragment(token.label, wordwrap=True), Fragment(formatting.escape_markdown(']')))
        elif token.dest_type == 'collapsed': yield Fragment(formatting.escape_markdown('[]'))

    def render_auto_link(self, token: span_token.AutoLink) -> Iterable[Fragment]:
        yield Fragment(formatting.escape_markdown('<') + token.children[0].content + formatting.escape_markdown('>'))

    def render_escape_sequence(self, token: span_token.EscapeSequence) -> Iterable[Fragment]:
        yield Fragment(token.children[0].content)

    def render_table(self, token: block_token.Table, max_line_length: int) -> Iterable[str]:
        fs = super().render_table(token, max_line_length)
        return [formatting.mcode('\n'.join(fs))]
