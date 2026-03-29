from __future__ import annotations

"""
Compile the ActorScope-AI LangGraph and export a visual representation.

Outputs:
- artifacts/langgraph_graph.png     (preferred, when PNG rendering is available)
- artifacts/langgraph_graph.mmd     (Mermaid source, always attempted)
- artifacts/langgraph_graph.txt     (status / fallback notes)

Usage:
    poetry run python export_langgraph_figure.py
"""

from pathlib import Path

from graph.builder import build_graph


ARTIFACTS_DIR = Path("artifacts")
PNG_PATH = ARTIFACTS_DIR / "langgraph_graph.png"
MERMAID_PATH = ARTIFACTS_DIR / "langgraph_graph.mmd"
STATUS_PATH = ARTIFACTS_DIR / "langgraph_graph.txt"


def main() -> None:
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

    app = build_graph()
    graph = app.get_graph()

    notes: list[str] = []

    mermaid_text = None
    try:
        if hasattr(graph, "draw_mermaid"):
            mermaid_text = graph.draw_mermaid()
            MERMAID_PATH.write_text(mermaid_text, encoding="utf-8")
            notes.append(f"Saved Mermaid source to: {MERMAID_PATH}")
        else:
            notes.append("Graph object does not expose draw_mermaid().")
    except Exception as exc:
        notes.append(f"Failed to export Mermaid source: {exc!r}")

    try:
        if hasattr(graph, "draw_mermaid_png"):
            png_bytes = graph.draw_mermaid_png()
            PNG_PATH.write_bytes(png_bytes)
            notes.append(f"Saved PNG figure to: {PNG_PATH}")
        else:
            notes.append("Graph object does not expose draw_mermaid_png().")
    except Exception as exc:
        notes.append(
            "Failed to export PNG figure. This can happen when the Mermaid PNG "
            f"renderer is unavailable in the current environment: {exc!r}"
        )

    if mermaid_text is not None:
        notes.append("")
        notes.append("Mermaid preview:")
        notes.append(mermaid_text)

    STATUS_PATH.write_text("\n".join(notes), encoding="utf-8")
    print("\n".join(notes))


if __name__ == "__main__":
    main()
