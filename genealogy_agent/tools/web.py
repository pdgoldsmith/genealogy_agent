from __future__ import annotations

from dataclasses import dataclass
from html.parser import HTMLParser
from urllib.request import Request, urlopen


class _TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.chunks: list[str] = []

    def handle_data(self, data: str) -> None:
        if data.strip():
            self.chunks.append(data.strip())


@dataclass(slots=True)
class WebPageSnapshot:
    url: str
    title: str
    text_excerpt: str


class WebBrowserTool:
    def fetch(self, url: str, max_chars: int = 4000) -> WebPageSnapshot:
        req = Request(url, headers={"User-Agent": "genealogy-agent/0.2"})
        with urlopen(req, timeout=15) as resp:  # nosec - caller controls targets
            html = resp.read().decode("utf-8", errors="ignore")

        parser = _TextExtractor()
        parser.feed(html)
        text = "\n".join(parser.chunks)
        title = next((line for line in parser.chunks if len(line) < 140), "Untitled")
        return WebPageSnapshot(url=url, title=title, text_excerpt=text[:max_chars])
