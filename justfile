# Generates gRPC based on the current proto submodule version
[group('setup')]
generate-grpc:
    cd common/infrastructure/grpc && uv run sh ./generate.sh

# Updates proto submodule to the latest commit and regenerates gRPC
[group('setup')]
update-proto:
    git submodule update --remote --merge
    just generate-grpc
