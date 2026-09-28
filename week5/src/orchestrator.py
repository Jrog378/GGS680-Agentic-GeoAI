from pathlib import Path
from .prompts import load_role, build_packet
from .state import ResearchState

class ManualOrchestrator:
    """Transparent orchestration for classroom use.

    This class does NOT call an LLM. It materializes the exact prompt packet for each role.
    Students can run each packet in separate VS Code/Codex agent conversations and save the
    returned artifact to outputs/. This makes state transitions inspectable.

    A later class can replace `emit_packet` with an API/provider adapter without changing the
    role specifications or state model.
    """

    def __init__(self, root: Path):
        self.root = root
        self.state = ResearchState(root=root)
        self.packet_dir = root / "outputs" / "prompt_packets"
        self.packet_dir.mkdir(parents=True, exist_ok=True)

    def emit_packet(self, filename: str, role_file: str, task: str, context_paths):
        role = load_role(self.root, role_file)
        context_parts = []
        for path in context_paths:
            text = self.state.read(path)
            context_parts.append(f"## FILE: {path}\n\n{text}")
        packet = build_packet(role, task, "\n\n".join(context_parts))
        out = self.packet_dir / filename
        out.write_text(packet, encoding="utf-8")
        return out

    def build_class_sequence(self):
        packets = []
        packets.append(self.emit_packet(
            "01_research_question_agent.md",
            "research_question_agent.md",
            "Generate and rank candidate GeoAI research questions and hypotheses.",
            ["inputs/problem.md"]
        ))
        packets.append(self.emit_packet(
            "02_scientific_critic.md",
            "scientific_critic.md",
            "Critique the candidate research questions. Recommend the strongest question or request revision.",
            ["inputs/problem.md", "outputs/research_questions.md"]
        ))
        packets.append(self.emit_packet(
            "03_writer_abstract.md",
            "writer.md",
            "Write a 200–300 word proposed-study abstract using the approved question and critique.",
            ["inputs/problem.md", "outputs/research_questions.md", "outputs/question_review.md"]
        ))
        packets.append(self.emit_packet(
            "04_methodology_agent.md",
            "methodology_agent.md",
            "Design a GeoAI methodology capable of testing the approved hypothesis.",
            ["inputs/problem.md", "outputs/research_questions.md", "outputs/question_review.md", "outputs/abstract_v1.md"]
        ))
        packets.append(self.emit_packet(
            "05_methodology_critic.md",
            "scientific_critic.md",
            "Critique the methodology as a scientific reviewer, emphasizing spatial validity and falsifiability.",
            ["outputs/methodology_v1.md", "outputs/research_questions.md"]
        ))
        packets.append(self.emit_packet(
            "06_data_tool_agent.md",
            "data_tool_agent.md",
            "Map the revised methodology to plausible datasets and computational tools. Mark anything uncertain TO VERIFY.",
            ["outputs/methodology_v1.md", "outputs/methodology_review.md"]
        ))
        packets.append(self.emit_packet(
            "07_validation_agent.md",
            "validation_agent.md",
            "Design the validation plan and identify what evidence would support or falsify the main scientific claim.",
            ["outputs/research_questions.md", "outputs/methodology_v1.md", "outputs/data_tool_plan.md"]
        ))
        return packets
