import dataclasses
import re
from abc import ABCMeta
from enum import Enum
from typing import Union, List, Tuple, Any, Callable

import mistletoe
from mistletoe.block_token import BlockToken, ThematicBreak  # noqa
from mistletoe.markdown_renderer import LinkReferenceDefinition, BlankLine
from mistletoe.span_token import SpanToken  # noqa

from . import customize
from .latex_escape.const import LATEX_SYMBOLS, NOT_MAP, LATEX_STYLES
from .latex_escape.helper import LatexToUnicodeHelper
from .logger import logger
from .mermaid import render_mermaid
from .mime import get_filename
from .render import TelegramMarkdownRenderer, escape_markdown

__all__ = [
    "escape_markdown",
    "customize",
    "markdownify",
    "telegramify",
    "ContentTypes",
]
TaskType = Tuple[str, List[Tuple[Any, Any]]]
SentType = List[Union["Text", "File", "Photo"]]
latex_escape_helper = LatexToUnicodeHelper()


def escape_latex(text):
    # Patterns to match block and inline math
    math_p = re.compile(r'\\\[(.*?)\\\]', re.DOTALL)
    inline_math_p = re.compile(r'\\\((.*?)\\\)', re.DOTALL)

    def contains_latex_symbols(content):
        # Check for common LaTeX symbols
        if len(content) < 5:
            return False
        latex_symbols = (r"\frac",
                         r"\sqrt",
                         r"\begin",
                         ) + tuple(LATEX_SYMBOLS.keys()) + tuple(NOT_MAP.keys()) + tuple(LATEX_STYLES.keys())
        return any(symbol in content for symbol in latex_symbols)

    def latex2unicode(match, is_block):
        # Extract the content of the match
        content = match.group(1)
        if not contains_latex_symbols(content):
            return match.group(0)  # Return the original match if no LaTeX symbols are found
        content = latex_escape_helper.convert(content)
        if is_block:
            return f"```{content.strip()}```"
        else:
            pre_process = content.strip().strip('\n')
            return f"`{pre_process}`"

    lines = text.split("\n\n")
    processed_lines = []
    for line in lines:
        # Process block-level math
        processed_line = math_p.sub(lambda match: latex2unicode(match, is_block=True), line)
        # Process inline math
        processed_line = inline_math_p.sub(lambda match: latex2unicode(match, is_block=False), processed_line)
        processed_lines.append(processed_line)
    return "\n\n".join(processed_lines)


def _update_text(token: Union[SpanToken, BlockToken]):
    """
    Update the text contents of a span token and its children.
    `InlineCode` tokens are left unchanged.
    """
    if isinstance(token, ThematicBreak):
        token.line = escape_markdown("————————")
        pass
    elif isinstance(token, LinkReferenceDefinition):
        pass
    elif isinstance(token, BlankLine):
        pass
    else:
        if hasattr(token, "content"):
            token.content = escape_markdown(token.content, unescape_html=customize.unescape_html)


def _update_block(token: BlockToken):
    """
    Update the text contents of paragraphs and headings within this block,
    and recursively within its children.
    """
    if hasattr(token, "children") and token.children:
        # Dispatch all children
        for child in token.children:
            _update_block(child)
    else:
        _update_text(token)


class ContentTypes(Enum):
    TEXT = "text"
    FILE = "file"
    PHOTO = "photo"


class RenderedContent(object, metaclass=ABCMeta):
    """
    The rendered content.

    - content: str
    - content_type: ContentTypes
    """
    content_type: ContentTypes


@dataclasses.dataclass
class Text(RenderedContent):
    content: str
    content_type: ContentTypes = ContentTypes.TEXT


@dataclasses.dataclass
class File(RenderedContent):
    file_name: str
    file_data: bytes
    caption: str = ""
    content_type: ContentTypes = ContentTypes.FILE


@dataclasses.dataclass
class Photo(RenderedContent):
    file_name: str
    file_data: bytes
    caption: str = ""
    content_type: ContentTypes = ContentTypes.PHOTO


class PackHelper(object):
    @staticmethod
    def process_long_pack(__token1_l: list, __token2_l: list, render_func: callable):
        """
        Process the long pack.
        :param __token1_l: Escaped tokens
        :param __token2_l: Unescaped tokens
        :param render_func: The render function
        :return:
        """
        # 如果超过最大字数限制
        if all(isinstance(_per_token1, mistletoe.block_token.CodeFence) for _per_token1 in __token1_l) and len(
                __token1_l) == 1 and len(__token2_l) == 1:
            # 如果这个 pack 是完全的 code block，那么采用文件形式发送。否则采用文本形式发送。
            _escaped_code = __token1_l[0]
            _unescaped_code_child = list(__token2_l[0].children)
            file_content = render_func(__token2_l)
            if _unescaped_code_child:
                _code_text = _unescaped_code_child[0]
                if isinstance(_code_text, mistletoe.span_token.RawText):
                    file_content = _code_text.content
            lang = "txt"
            if isinstance(_escaped_code, mistletoe.block_token.CodeFence):
                lang = _escaped_code.language
            if lang.lower() == "mermaid":
                try:
                    image_io, caption = render_mermaid(file_content.replace("```mermaid", "").replace("```", ""))
                    return [Photo(file_name="mermaid.png", file_data=image_io.getvalue(), caption=caption)]
                except Exception as e:
                    pass
            file_name = get_filename(line=render_func(__token1_l), language=lang)
            return [File(file_name=file_name, file_data=file_content.encode(), caption="")]
        # 如果超过最大字数限制
        return [File(file_name="letter.txt", file_data=render_func(__token2_l).encode(), caption="")]

    @staticmethod
    def process_short_pack(__token1_l, __token2_l, render_func):
        """
        Process the short pack.
        :param __token1_l: Escaped tokens
        :param __token2_l: Unescaped tokens
        :param render_func: The render function
        :return:
        """
        _processed = []
        escaped_cell = render_func(__token1_l)
        # 没有超过最大字数限制
        _processed.append(Text(content=escaped_cell))
        return _processed


class BaseInterpreter(object):
    name = "base"

    def merge(self, tasks: List[TaskType]) -> List[TaskType]:
        """
        Merge the tasks.
        :param tasks:  [(base, [(token1,token2),(token1,token2)]), (base, [(token1,token2),(token1,token2)])]
        :return:
        """
        return tasks

    def split(self, task: TaskType) -> List[TaskType]:
        """
        Split the task.
        :param task: (base, [(token1,token2),(token1,token2)])
        :return: [(base, [(token1,token2),(token1,token2)]),....newTask]
        """
        return [task]

    def render_task(self,
                    task: TaskType,
                    render_block_func: Callable[[List[Any]], str],
                    render_lines_func: Callable[[str], str],
                    max_word_count: int = 4090
                    ) -> SentType:
        """
        Render the task.
        :param render_block_func: The render block function
        :param render_lines_func: The render lines function
        :param task: (base, [(token1,token2),(token1,token2)])
        :param max_word_count: The maximum number of words in a single message.
        :return: SentType
        """
        task_type, token_pairs = task
        if task_type != "base":
            logger.warn("Invalid task type for BaseInterpreter.")
        token1_l = list(__token1 for __token1, __token2 in token_pairs)
        token2_l = list(__token2 for __token1, __token2 in token_pairs)
        # 处理超过最大字数限制的情况
        if len(render_block_func(token1_l)) > max_word_count:
            # 如果超过最大字数限制
            if all(isinstance(_per_token1, mistletoe.block_token.CodeFence) for _per_token1 in token1_l) and len(
                    token1_l) == 1 and len(token2_l) == 1:
                # 如果这个 pack 是完全的 code block，那么采用文件形式发送。否则采用文本形式发送。
                _escaped_code = token1_l[0]
                _unescaped_code_child = list(token1_l[0].children)
                file_content = render_block_func(token2_l)
                if _unescaped_code_child:
                    _code_text = _unescaped_code_child[0]
                    if isinstance(_code_text, mistletoe.span_token.RawText):
                        file_content = _code_text.content
                lang = "txt"
                if isinstance(_escaped_code, mistletoe.block_token.CodeFence):
                    lang = _escaped_code.language
                """
                if lang.lower() == "mermaid":
                    try:
                        image_io, caption = render_mermaid(file_content.replace("```mermaid", "").replace("```", ""))
                        return [Photo(file_name="mermaid.png", file_data=image_io.getvalue(), caption=caption)]
                    except Exception as e:
                        pass
                """
                file_name = get_filename(line=render_block_func(token1_l), language=lang)
                return [File(file_name=file_name, file_data=file_content.encode(), caption="")]
            # 如果超过最大字数限制
            return [File(file_name="letter.txt", file_data=render_block_func(token2_l).encode(), caption="")]
        # 没有超过最大字数限制
        return [Text(content=render_block_func(token1_l))]


class MermaidInterpreter(BaseInterpreter):
    name = "mermaid"

    def merge(self, tasks: List[TaskType]) -> List[TaskType]:
        """
        Merge the tasks.
        :param tasks:  [(base, [(token1,token2),(token1,token2)]), (base, [(token1,token2),(token1,token2)])]
        :return:
        """
        return tasks

    def split(self, task: TaskType) -> List[TaskType]:
        """
        Split the task.
        :param task: (base, [(token1,token2),(token1,token2)])
        :return: [(mermaid, [(token1,token2),(token1,token2)]),....newTask]
        """
        task_type, token_pairs = task
        # 只处理 base 块
        if task_type != "base":
            return [task]
        # 用于存放生成的新任务
        tasks = []
        # 临时缓存非 Mermaid 块
        current_base_tokens = []
        for token_pair in token_pairs:
            token1, _ = token_pair
            # 检查是否为 Mermaid 块
            if isinstance(token1, mistletoe.block_token.CodeFence) and token1.language.lower() == "mermaid":
                if current_base_tokens:
                    # 将缓存的非 Mermaid 块生成新的 base 任务
                    tasks.append(("base", current_base_tokens))
                    current_base_tokens = []
                # 单独添加 Mermaid 块任务
                tasks.append(("mermaid", [token_pair]))
            else:
                # 累积 base 块
                current_base_tokens.append(token_pair)
        # 处理剩余的 base 块
        if current_base_tokens:
            tasks.append(("base", current_base_tokens))
        return tasks

    def render_task(self,
                    task: TaskType,
                    render_block_func: Callable[[List[Any]], str],
                    render_lines_func: Callable[[str], str],
                    max_word_count: int = 4090
                    ) -> SentType:
        """
        Render the task.#
        :param task: (base, [(token1,token2),(token1,token2)])  of [(base, [(token1,token2),(token1,token2)]), (base, [(token1,token2),(token1,token2)])]
        :param render_block_func: The render block function
        :param render_lines_func: The render lines function
        :param max_word_count: The maximum number of words in a single message.
        :return: SentType
        """
        task_type, token_pairs = task
        if task_type != "mermaid":
            raise ValueError("Invalid task type for MermaidInterpreter.")
        # 仅处理 Mermaid 块
        if len(token_pairs) != 1:
            raise ValueError("Invalid token length for MermaidInterpreter.")
        token1_l = list(__token1 for __token1, __token2 in token_pairs)
        token2_l = list(__token2 for __token1, __token2 in token_pairs)
        if not all(isinstance(_per_token, mistletoe.block_token.CodeFence) for _per_token in token1_l):
            raise ValueError("Invalid token type for MermaidInterpreter.")
        _escaped_code = token2_l[0]
        if (isinstance(
                _escaped_code,
                mistletoe.block_token.CodeFence
        ) and _escaped_code.language.lower() == "mermaid"):
            file_content = render_block_func(token1_l)
            _unescaped_code_child = list(_escaped_code.children)
            if _unescaped_code_child:
                _raw_text = _unescaped_code_child[0]
                if isinstance(_raw_text, mistletoe.span_token.RawText):
                    file_content = _raw_text.content
            try:
                img_io, url = render_mermaid(file_content.replace("```mermaid", "").replace("```", ""))
                message = f"[edit in mermaid.live]({url})"
            except Exception as e:
                return [
                    File(
                        file_name="mermaid_code.txt",
                        file_data=render_block_func(token2_l).encode(),
                        caption=""
                    )
                ]
            else:
                return [
                    Photo(
                        file_name="mermaid.png",
                        file_data=img_io.getvalue(),
                        caption=render_lines_func(message)
                    )
                ]
        return [
            File(file_name="mermaid_code.txt", file_data=render_block_func(token2_l).encode(), caption="")
        ]


def telegramify(
        content: str,
        max_line_length: int = None,
        normalize_whitespace=False,
        latex_escape=None,
        max_word_count: int = 4090
) -> List[Union[Text, File, Photo]]:
    """
    Convert markdown content to Telegram Markdown format.

    **Showcase** https://github.com/sudoskys/telegramify-markdown/blob/main/playground/telegramify_case.py

    :param content: The markdown content to convert.
    :param max_line_length: The maximum length of a line.
    :param normalize_whitespace: Whether to normalize whitespace.
    :param latex_escape: Whether to make LaTeX content readable in Telegram.
    :param max_word_count: The maximum number of words in a single message.
    :return: The Telegram markdown formatted content. **Need Send in MarkdownV2 Mode.**
    :raises ValueError: If the token length mismatch.
    :raises Exception: Some other exceptions.
    """
    _rendered: List[Union[Text, File, Photo]] = []
    with TelegramMarkdownRenderer(
            max_line_length=max_line_length,
            normalize_whitespace=normalize_whitespace
    ) as renderer:
        if latex_escape is None:
            latex_escape = customize.latex_escape
        if latex_escape:
            content = escape_latex(content)
        document = mistletoe.Document(content)
        document2 = mistletoe.Document(content)
        # 只更新第一个文档，因为我们要倒查第二个文档的内容
        _update_block(document)
        # 解离 Token
        tokens = list(document.children)
        tokens2 = list(document2.children)
        if len(tokens) != len(tokens2):
            raise ValueError("Token length mismatch")

        # 对内容进行分块渲染
        def is_over_max_word_count(doc_t: List[Tuple[Any, Any]]):
            doc = mistletoe.Document(lines=[])
            doc.children = [___token for ___token, ___token2 in doc_t]
            return len(renderer.render(doc)) > max_word_count

        def render_block(doc_t: List[Any]):
            doc = mistletoe.Document(lines=[])
            doc.children = doc_t.copy()
            return renderer.render(doc)

        def render_lines(lines: str):
            doc = mistletoe.Document(lines=lines)
            return renderer.render(doc)

        _stack = []
        _packed = []

        # 步进推送
        for _token, _token2 in zip(tokens, tokens2):
            # 计算如果推送当前 Token 是否会超过最大字数限制
            if is_over_max_word_count(_stack + [(_token, _token2)]):
                _packed.append(_stack)
                _stack = [(_token, _token2)]
            else:
                _stack.append((_token, _token2))
        if _stack:
            _packed.append(_stack)
        _task = [("base", cell) for cell in _packed]
        # [(base, [(token1,token2),(token1,token2)]), (base, [(token1,token2),(token1,token2)])]
        interpreters = [BaseInterpreter(), MermaidInterpreter()]
        interpreters_map = {interpreter.name: interpreter for interpreter in interpreters}
        for interpreter in interpreters:
            _task = interpreter.merge(_task)
        for interpreter in interpreters:
            _new_task = []
            for _per_task in _task:
                _new_task.extend(interpreter.split(_per_task))
            _task = _new_task

        for _per_task in _task:
            task_type, token_pairs = _per_task
            if task_type not in interpreters_map:
                raise ValueError("Invalid task type.")
            interpreter = interpreters_map[task_type]
            _rendered.extend(interpreter.render_task(
                task=_per_task,
                render_lines_func=render_lines,
                render_block_func=render_block,
                max_word_count=max_word_count
            ))
    return _rendered


def markdownify(
        content: str,
        max_line_length: int = None,
        normalize_whitespace=False,
        latex_escape=None,
) -> str:
    """
    Convert markdown str to Telegram Markdown format.

     **Showcase** https://github.com/sudoskys/telegramify-markdown/blob/main/playground/markdownify_case.py

    :param content: The markdown content to convert.
    :param max_line_length: The maximum length of a line.
    :param normalize_whitespace: Whether to normalize whitespace.
    :param latex_escape: Whether to make LaTeX content readable in Telegram.
    :return: The Telegram markdown formatted content. **Need Send in MarkdownV2 Mode.**
    """
    _rendered = []
    with TelegramMarkdownRenderer(
            max_line_length=max_line_length,
            normalize_whitespace=normalize_whitespace
    ) as renderer:
        if latex_escape is None:
            latex_escape = customize.latex_escape
        if latex_escape:
            content = escape_latex(content)
        document = mistletoe.Document(content)
        _update_block(document)
        result = renderer.render(document)
    return result
