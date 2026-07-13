from dataclasses import dataclass
from pathlib import Path

from pydantic import model_validator

from common.config.schemas.base_enum_model import BaseEnumModel


@dataclass(frozen=True)
class TlsPaths:
    ca_certificate: Path
    certificate: Path
    private_key: Path


class TlsConfig(BaseEnumModel):
    enabled: bool
    ca_certificate: Path | None
    certificate: Path | None
    private_key: Path | None

    @model_validator(mode="after")
    def validate_credentials(self) -> TlsConfig:
        if not self.enabled:
            return self

        paths = (self.ca_certificate, self.certificate, self.private_key)
        if any(path is None for path in paths):
            raise ValueError(
                "TLS requires ca_certificate, certificate, and private_key"
            )
        credential_paths = tuple(path for path in paths if path is not None)
        relative_paths = [path for path in credential_paths if not path.is_absolute()]
        if relative_paths:
            raise ValueError(
                "TLS credential paths must be absolute: "
                f"{', '.join(map(str, relative_paths))}"
            )
        missing_paths = [path for path in credential_paths if not path.is_file()]
        if missing_paths:
            raise ValueError(
                "TLS credential files do not exist: "
                f"{', '.join(map(str, missing_paths))}"
            )
        return self

    @property
    def credentials_paths(self) -> TlsPaths:
        if (
            self.ca_certificate is None
            or self.certificate is None
            or self.private_key is None
        ):
            raise RuntimeError("TLS credentials are unavailable while TLS is enabled")
        return TlsPaths(
            ca_certificate=self.ca_certificate,
            certificate=self.certificate,
            private_key=self.private_key,
        )
