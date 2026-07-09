import re
from pathlib import Path

GEN = Path("generated")
pattern_as = re.compile(r"^import (\w+_pb2) as (\w+__pb2)$", flags=re.M)
pattern_simple = re.compile(r"^import (\w+_pb2)$", flags=re.M)

for p in GEN.glob("*.py"):
    text = p.read_text(encoding="utf-8")
    # import X_pb2 as Y  -> from . import X_pb2 as Y
    text = pattern_as.sub(r"from . import \1 as \2", text)
    # import X_pb2 -> from . import X_pb2
    text = pattern_simple.sub(r"from . import \1", text)
    p.write_text(text, encoding="utf-8")
    print("patched", p)
