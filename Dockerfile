FROM python:3.14-alpine AS builder

WORKDIR /bot
ARG PLATFORM
COPY --from=ghcr.io/astral-sh/uv:0.11.28 /uv /uvx /bin/

RUN apk add --no-cache gcc musl-dev zlib-dev

COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev --extra "${PLATFORM}"

# Generate grpc stubs
COPY common common
RUN uv run --no-sync common/infrastructure/grpc/generate.py

# Copy the rest of the source code
COPY ${PLATFORM} translations run.sh ./
RUN chmod +x run.sh

COPY config.template.yaml config.yaml


FROM python:3.14-alpine

WORKDIR /bot
ARG PLATFORM
ENV PLATFORM=${PLATFORM}

COPY --from=builder /bot .

ENTRYPOINT [ "./run.sh" ]
