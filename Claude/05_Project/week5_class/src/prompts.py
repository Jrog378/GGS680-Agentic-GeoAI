from pathlib import Path

def load_role(root: Path, role_filename: str) -> str:
    return (root / "agents" / role_filename).read_text(encoding="utf-8")

def build_packet(role_text: str, task: str, context: str) -> str:
    return f"""# AGENT ROLE

{role_text}

# CURRENT TASK

{task}

# CURRENT RESEARCH STATE / EVIDENCE

{context}

# EXECUTION REQUIREMENT

Work only from the supplied state and clearly label missing evidence.
Return the requested structured artifact. Do not silently change the research question.
"""
