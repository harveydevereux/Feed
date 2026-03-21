from dataclasses import dataclass

@dataclass(kw_only=True)
class Source():
    title: str
    url: str
    preview_image_url: str = ""