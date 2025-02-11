from typing import Iterable
from mistletoe import block_token, span_token
from mistletoe.markdown_renderer import MarkdownRenderer, LinkReferenceDefinition, Fragment
from telebot import formatting
from .customize import markdown_symbol, strict_markdown

class TelegramMarkdownRenderer(MarkdownRenderer):
    """
    A custom Markdown renderer that formats text for Telegram.
    """

    def render_heading(
            self, token: block_token.Heading, max_line_length: int
    ) -> Iterable[str]:
        """
        Render a heading token.
        Note: This method does not include word wrapping because atx headings always fit on a single line.
        """
        line = ""
        if token.level == 1:
            line += markdown_symbol.head_level_1
        elif token.level == 2:
            line += markdown_symbol.head_level_2
        elif token.level == 3:
            line += markdown_symbol.head_level_3
        elif token.level == 4:
            line += markdown_symbol.head_level_4
        fs = super().span_to_lines(token.children, max_line_length=max_line_length)
        text = next(fs, "")
        if text:
            line += " " + text
        if token.closing_sequence:
            line += " " + token.closing_sequence
        return [formatting.mbold(line, escape=False)]

    def render_fenced_code_block(
            self, token: block_token.BlockCode, max_line_length: int
    ) -> Iterable[str]:
        """
        Render a fenced code block.
        """
        indentation = " " * token.indentation
        yield indentation + token.delimiter + token.info_string
        yield from self.prefix_lines(
            token.content[:-1].split("\n"), indentation
        )
        yield indentation + token.delimiter

    def render_inline_code(self, token: span_token.InlineCode) -> Iterable[Fragment]:
        """
        Render inline code.
        """
        if len(token.delimiter) == 3:
            return self.embed_span(
                Fragment(token.delimiter + token.padding + "\n"),
                token.children,
                Fragment(token.padding + token.delimiter)
            )
        return self.embed_span(
            Fragment(token.delimiter + token.padding),
            token.children,
            Fragment(token.padding + token.delimiter)
        )

    def render_block_code(
            self, token: block_token.BlockCode, max_line_length: int
    ) -> Iterable[str]:
        """
        Render a block code.
        """
        return [formatting.mcode(token.content, escape=False)]

    def render_setext_heading(
            self, token: block_token.SetextHeading, max_line_length: int
    ) -> Iterable[str]:
        """
        Render a setext heading.
        """
        yield from self.span_to_lines(token.children, max_line_length=max_line_length)
        yield formatting.escape_markdown("——" * 5)

    def render_emphasis(self, token: span_token.Emphasis) -> Iterable[Fragment]:
        """
        Render emphasis.
        """
        return super().render_emphasis(token)

    def render_strong(self, token: span_token.Strong) -> Iterable[Fragment]:
        """
        Render strong text.
        If strict_markdown is True, render text with double delimiters for strong emphasis.
        Otherwise, render with single delimiter for bold.
        """
        if strict_markdown:
            return self.embed_span(Fragment(token.delimiter * 2), token.children)
        return self.embed_span(Fragment(token.delimiter * 1), token.children)

    def render_strikethrough(
            self, token: span_token.Strikethrough
    ) -> Iterable[Fragment]:
        """
        Render strikethrough text.
        """
        return self.embed_span(Fragment("~"), token.children)

    def render_list_item(
            self, token: block_token.ListItem, max_line_length: int
    ) -> Iterable[str]:
        """
        Render a list item.
        """
        if str(token.leader).strip().endswith("."):
            token.leader = formatting.escape_markdown(token.leader) + " "
        else:
            token.leader = formatting.escape_markdown("⦁")
        return super().render_list_item(token, max_line_length)

    def render_link_reference_definition(
            self, token: LinkReferenceDefinition
    ) -> Iterable[Fragment]:
        """
        Render a link reference definition.
        """
        yield from (
            Fragment(markdown_symbol.link + formatting.mlink(
                content=token.title if token.title else token.label,
                url=token.dest,
                escape=True
            )
                     ),
        )

    def render_image(self, token: span_token.Image) -> Iterable[Fragment]:
        """
        Render an image.
        """
        yield Fragment(markdown_symbol.image)
        yield from self.render_link_or_image(token, token.src)

    def render_link(self, token: span_token.Link) -> Iterable[Fragment]:
        """
        Render a link.
        """
        return self.render_link_or_image(token, token.target)

    def render_link_or_image(
            self, token: span_token.SpanToken, target: str
    ) -> Iterable[Fragment]:
        """
        Render either a link or an image.
        Handle different dest_type cases: uri, angle_uri, full, collapsed.
        """
        title = next(self.span_to_lines(token.children, max_line_length=20), "")
        if token.dest_type == "uri" or token.dest_type == "angle_uri":
            yield Fragment(formatting.mlink(url=target, content=title, escape=True))
        elif token.dest_type == "full":
            yield from (
                Fragment(formatting.escape_markdown("[")),
                Fragment(token.label, wordwrap=True),
                Fragment(formatting.escape_markdown("]")),
            )
        elif token.dest_type == "collapsed":
            yield Fragment(formatting.escape_markdown("[]"))

    def render_auto_link(self, token: span_token.AutoLink) -> Iterable[Fragment]:
        """
        Render an auto link.
        """
        yield Fragment(formatting.escape_markdown("<") + token.children[0].content + formatting.escape_markdown(">"))

    def render_escape_sequence(
            self, token: span_token.EscapeSequence
    ) -> Iterable[Fragment]:
        """
        Render an escape sequence.
        Note: The escape_markdown is already handled in the parser, so we skip it here.
        """
        yield Fragment("\\" + token.children[0].content)

    def render_table(
            self, token: block_token.Table, max_line_length: int
    ) -> Iterable[str]:
        """
        Render a table.
        Note: Column widths are not preserved; they are automatically adjusted to fit the contents.
        """
        fs = super().render_table(token, max_line_length)
        return [formatting.mcode("\n".join(fs))]