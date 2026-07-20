from dataclasses import dataclass

from pydantic import HttpUrl


@dataclass(frozen=True)
class AppRedirect:
    path: str
    display_text: str

    def to_url(self, public_url: str) -> HttpUrl:
        return HttpUrl(f"{public_url}{self.path}")
