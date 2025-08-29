from pydantic import BaseModel, ConfigDict


class BaseEnumModel(BaseModel):
    model_config = ConfigDict(
        validate_default=True,
        use_enum_values=False,
    )
