# Bots for codename-deadline

## Configuration

The image includes `config.template.yaml` as `/bot/config.yaml`. Local runs can copy
that file to `config.yaml`. Every supported environment variable is listed there.

Placeholders use `${ENV}` for required values and `${ENV:default}` for values with a
default. They must occupy a complete YAML scalar. A local `.env` file next to the
configuration file is loaded without overriding variables already provided by the
process.

When either TLS block is enabled, `ca_certificate`, `certificate`, and `private_key`
must be absolute paths to PEM files. The supplied container defaults point to the
mounted production secrets.
