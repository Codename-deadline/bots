from pydantic import BaseModel

from common.logic.enums import Language


class GrpcResponse(BaseModel):
    is_error: bool
    key: str
    language: Language
