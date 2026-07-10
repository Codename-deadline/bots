#!/bin/sh

# Generate the python impl
mkdir -p generated
python3 -m grpc_tools.protoc -I proto \
  --python_out=generated \
  --pyi_out=generated \
  --grpc_python_out=generated \
  proto/integration.proto

# Import patch
python3 absolute_path_patch.py
