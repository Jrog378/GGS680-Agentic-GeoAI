from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

@dataclass
class ResearchState:
    root: Path
    stage: str = "problem"
    artifacts: Dict[str, str] = field(default_factory=dict)
    history: List[str] = field(default_factory=list)

    def read(self, relative_path: str) -> str:
        p = self.root / relative_path
        return p.read_text(encoding="utf-8") if p.exists() else ""

    def write_output(self, filename: str, content: str) -> Path:
        out = self.root / "outputs" / filename
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(content, encoding="utf-8")
        self.artifacts[filename] = str(out)
        self.history.append(f"{self.stage}: wrote {filename}")
        return out
