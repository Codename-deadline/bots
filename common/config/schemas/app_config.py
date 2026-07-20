from pydantic import Field, HttpUrl, field_validator

from common.config.schemas.base_enum_model import BaseEnumModel


class AppConfig(BaseEnumModel):
    name: str = Field(min_length=1)
    public_url: str

    @field_validator("public_url")
    @classmethod
    def validate_public_url(cls, value: str) -> str:
        url = HttpUrl(value)
        if url.scheme != "https":
            raise ValueError("App public URL must use HTTPS")
        return str(url).rstrip("/")
