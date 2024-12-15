import asyncio
import base64
import dataclasses
import json
import zlib
from io import BytesIO
from typing import Union, Tuple

from PIL import Image
from aiohttp_client_cache import CachedSession
from aiohttp_client_cache.backends import CacheBackend

from telegramify_markdown.logger import logger


@dataclasses.dataclass
class MermaidConfig:
    theme: str = "neutral"


async def download_image(url: str) -> BytesIO:
    """
    Download the image from the URL asynchronously.
    :param url: Image URL
    :raises: aiohttp.ClientError, asyncio.TimeoutError
    """
    logger.debug(f"telegramify_markdown: Downloading mermaid image from {url}")
    headers = {
        "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                       "(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")
    }
    async with CachedSession(cache=CacheBackend(expire_after=60 * 60)) as session:
        try:
            async with session.get(url, headers=headers, timeout=10) as response:
                response.raise_for_status()
                content = await response.read()
        except Exception as e:
            raise ValueError(f"telegramify_markdown: Render failed on the mermaid graph from {url}") from e
    return BytesIO(content)


def is_image(data: BytesIO) -> bool:
    """
    Check if the data is an image
    :param data: BytesIO Stream
    :return: If the data is an image, return True; otherwise, return False
    """
    try:
        # 使用 Pillow 验证是否是合法图片
        with Image.open(data) as img:
            img.verify()  # 验证图片
        return True
    except Exception as e:
        logger.debug(f"telegramify_markdown: Image verification failed: {e}")
        return False


def compress_to_deflate(data: Union[bytes]) -> bytes:
    """
    Compress the data using the DEFLATE algorithm.
    :param data: The data to compress
    :return: The compressed data
    """
    compressor = zlib.compressobj(
        level=9,  # Maximum compression level
        method=zlib.DEFLATED,  # Use the DEFLATE algorithm
        wbits=15,  # Window size
        memLevel=8,  # Memory usage level
        strategy=zlib.Z_DEFAULT_STRATEGY  # Default compression strategy
    )
    compressed_data = compressor.compress(data)
    compressed_data += compressor.flush()
    return compressed_data


def safe_base64_encode(data):
    """
    URL-safe base64 encoding
    :param data: waiting for encoding
    :return: Encoded data
    """
    return base64.urlsafe_b64encode(data)


def generate_pako(graph_markdown: str, mermaid_config: MermaidConfig = None) -> str:
    """
    Generate the pako URL for the Mermaid graph.
    :param graph_markdown: Input Mermaid graph markdown
    :param mermaid_config: Mermaid configuration
    :return: The pako URL
    """
    if mermaid_config is None:
        mermaid_config = MermaidConfig()
    graph_data = {
        "code": graph_markdown,
        "mermaid": mermaid_config.__dict__
    }
    json_bytes = json.dumps(graph_data).encode('ascii')
    compressed_data = compress_to_deflate(json_bytes)
    base64_encoded = safe_base64_encode(compressed_data)
    return f"pako:{base64_encoded.decode('ascii')}"


def b64_mermaid_url(diagram: str) -> str:
    """
    ***NOT USED***

    Get the Mermaid Ink URL for the graph.
    :param diagram: The Mermaid graph Markdown
    :return: Link
    """
    diagram_encoded = safe_base64_encode(diagram.encode('utf8')).decode('ascii')
    return f'https://mermaid.ink/img/{diagram_encoded}?theme=neutral&width=500&scale=2'


def get_mermaid_live_url(graph_markdown: str) -> str:
    """
    Get the Mermaid Live URL for the graph.
    Can be used to edit the graph in the browser.
    :param graph_markdown:
    :return:
    """
    return f'https://mermaid.live/edit/#{generate_pako(graph_markdown)}'


def get_mermaid_ink_url(graph_markdown: str) -> str:
    """
    Get the Mermaid Ink URL for the graph.
    Can be used to download the image.
    :param graph_markdown: The Mermaid graph Markdown
    :return: Link
    """
    return f'https://mermaid.ink/img/{generate_pako(graph_markdown)}?theme=neutral&width=500&scale=2&type=webp'


async def render_mermaid(diagram: str) -> Tuple[BytesIO, str]:
    # render picture
    img_url = get_mermaid_ink_url(diagram)
    caption = get_mermaid_live_url(diagram)
    # Download the image
    img_data = await download_image(img_url)
    if not is_image(img_data):
        raise ValueError("The URL does not return an image.")
    img_data.seek(0)  # Reset the file pointer to the beginning
    return img_data, caption


if __name__ == '__main__':
    mermaid_md = """
    sequenceDiagram
        Alice ->> Bob: Hello Bob, how are you?
        Bob-->>John: How about you John?
        Bob--x Alice: I am good thanks!
        Bob-x John: I am good thanks!
        Note right of John: Bob thinks a long<br/>long time, so long<br/>that the text does<br/>not fit on a row.
    """


    async def run():
        t1 = await render_mermaid(mermaid_md)
        print(t1)
        # 展示图片
        Image.open(t1[0]).show()


    asyncio.run(run())
