from pathlib import Path
from src.orchestrator import ManualOrchestrator

if __name__ == "__main__":
    root = Path(__file__).resolve().parent
    orchestrator = ManualOrchestrator(root)
    packets = orchestrator.build_class_sequence()
    print("Generated prompt packets:")
    for p in packets:
        print(" -", p.relative_to(root))
    print("\nOpen a packet, run it in a dedicated VS Code/Codex agent conversation,")
    print("then save the returned artifact using the filename requested in the packet sequence.")
