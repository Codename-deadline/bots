FROM python:3.13-alpine AS builder

# Build and store all wheels under /wheels
# Copy the source code to /bot
WORKDIR /bot
ARG PLATFORM

# Install depencencies for building wheels
RUN apk add gcc musl-dev zlib-dev

# Build wheels for common dependencies
COPY common common
RUN pip wheel -w wheels -r common/requirements.txt && \
    pip install --no-index --find-links=wheels -r common/requirements.txt

# Generate grpc stubs
RUN chmod +x common/grpc/generate.sh && \
    cd common/grpc && \
    sh generate.sh && \
    cd /bot

# Build wheels for platform specific dependencies
COPY ${PLATFORM}/requirements.txt .
RUN pip wheel -w wheels -r requirements.txt

# Copy the rest of the source code
COPY ${PLATFORM} ${PLATFORM}
COPY translations translations

COPY run.sh .
RUN chmod +x run.sh


FROM python:3.13-alpine

WORKDIR /bot
ARG PLATFORM
ENV PLATFORM=${PLATFORM}

COPY --from=builder /bot .
RUN python3 -m venv .venv && \
    source .venv/bin/activate && \
    pip install --no-index --find-links=wheels --no-cache-dir -r common/requirements.txt -r requirements.txt && \
    rm -rf wheels

ENTRYPOINT [ "./run.sh" ]