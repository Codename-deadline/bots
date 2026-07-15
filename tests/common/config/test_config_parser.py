import pytest
from pydantic import Field

from common.config.config_parser import ConfigParser


class ExampleConfig(ConfigParser):
    value: str
    enabled: bool = Field(default=False)


def test_from_yaml_resolves_required_and_default_placeholders(tmp_path, monkeypatch):
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        "value: ${EXAMPLE_VALUE:default value}\nenabled: ${EXAMPLE_ENABLED:false}\n"
    )
    monkeypatch.setenv("EXAMPLE_VALUE", "configured value")

    config = ExampleConfig.from_yaml(config_path)

    assert config.value == "configured value"
    assert config.enabled is False


def test_from_yaml_uses_default_when_environment_variable_is_missing(
    tmp_path, monkeypatch
):
    config_path = tmp_path / "config.yaml"
    config_path.write_text("value: ${EXAMPLE_VALUE:localhost:9092}\n")
    monkeypatch.delenv("EXAMPLE_VALUE", raising=False)

    config = ExampleConfig.from_yaml(config_path)

    assert config.value == "localhost:9092"


def test_from_yaml_rejects_missing_required_environment_variable(tmp_path, monkeypatch):
    config_path = tmp_path / "config.yaml"
    config_path.write_text("value: ${EXAMPLE_VALUE}\n")
    monkeypatch.delenv("EXAMPLE_VALUE", raising=False)

    with pytest.raises(ValueError, match="EXAMPLE_VALUE.*value"):
        ExampleConfig.from_yaml(config_path)


def test_from_yaml_resolves_environment_values_after_parsing_yaml(
    tmp_path, monkeypatch
):
    config_path = tmp_path / "config.yaml"
    config_path.write_text("value: ${EXAMPLE_VALUE}\n")
    monkeypatch.setenv("EXAMPLE_VALUE", "host: 9092 # still a string")

    config = ExampleConfig.from_yaml(config_path)

    assert config.value == "host: 9092 # still a string"


def test_from_yaml_rejects_malformed_placeholder(tmp_path):
    config_path = tmp_path / "config.yaml"
    config_path.write_text("value: ${EXAMPLE_VALUE\n")

    with pytest.raises(ValueError, match="Invalid placeholder.*value"):
        ExampleConfig.from_yaml(config_path)
