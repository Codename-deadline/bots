from pathlib import Path

import pytest
from pydantic import ValidationError

from common.config.schemas.tls_config import TlsConfig


def test_tls_config_allows_disabled_tls_without_credentials():
    config = TlsConfig(
        enabled=False,
        ca_certificate=None,
        certificate=None,
        private_key=None,
    )

    assert config.enabled is False


def test_tls_config_requires_all_credentials_when_enabled(tmp_path):
    ca_certificate = tmp_path / "ca.crt"
    ca_certificate.write_text("ca")

    with pytest.raises(
        ValidationError, match="ca_certificate, certificate, and private_key"
    ):
        TlsConfig(
            enabled=True,
            ca_certificate=ca_certificate,
            certificate=None,
            private_key=None,
        )


def test_tls_config_accepts_existing_absolute_credential_files(tmp_path):
    ca_certificate = tmp_path / "ca.crt"
    certificate = tmp_path / "client.crt"
    private_key = tmp_path / "client.key"
    for path in (ca_certificate, certificate, private_key):
        path.write_text(path.name)

    config = TlsConfig(
        enabled=True,
        ca_certificate=ca_certificate,
        certificate=certificate,
        private_key=private_key,
    )

    assert config.credentials_paths.certificate == certificate


def test_tls_config_rejects_relative_credential_paths():
    with pytest.raises(ValidationError, match="must be absolute"):
        TlsConfig(
            enabled=True,
            ca_certificate=Path("ca.crt"),
            certificate=Path("client.crt"),
            private_key=Path("client.key"),
        )
