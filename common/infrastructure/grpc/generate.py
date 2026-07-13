import re
from pathlib import Path

from grpc_tools import protoc


class GrpcGenerator:
    _import_as_pattern = re.compile(r"^import (\w+_pb2) as (\w+__pb2)$", flags=re.M)
    _import_pattern = re.compile(r"^import (\w+_pb2)$", flags=re.M)

    def __init__(self) -> None:
        self._directory = Path(__file__).resolve().parent
        self._generated_directory = self._directory / "generated"
        self._proto_path = self._directory / "proto" / "integration.proto"

    def run(self) -> None:
        self._generate()
        self._patch_generated_imports()

    def _generate(self) -> None:
        self._generated_directory.mkdir(exist_ok=True)
        exit_code = protoc.main(
            [
                "protoc",
                f"-I{self._proto_path.parent}",
                f"--python_out={self._generated_directory}",
                f"--grpc_python_out={self._generated_directory}",
                str(self._proto_path),
            ]
        )
        if exit_code != 0:
            raise RuntimeError(
                f"gRPC stub generation failed with exit code {exit_code}"
            )

    def _patch_generated_imports(self) -> None:
        for path in self._generated_directory.glob("*.py"):
            content = path.read_text(encoding="utf-8")
            content = self._import_as_pattern.sub(r"from . import \1 as \2", content)
            content = self._import_pattern.sub(r"from . import \1", content)
            path.write_text(content, encoding="utf-8")
            print("patched", path)


if __name__ == "__main__":
    GrpcGenerator().run()
