#!/usr/bin/env python3
"""Export LangGraph workflow diagram"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from orchestration.langgraph_workflow import get_workflow_graph, compiled_workflow

def save_mermaid_diagram():
    """Save Mermaid diagram to file"""
    diagram = get_workflow_graph()
    
    output_path = Path("WORKFLOW_DIAGRAM.md")
    with open(output_path, "w") as f:
        f.write("# Voice RAG Bot - LangGraph Workflow Diagram\n\n")
        f.write("```mermaid\n")
        f.write(diagram)
        f.write("\n```\n")
    
    print(f"✓ Mermaid diagram saved to {output_path}")
    return diagram

def save_ascii_diagram():
    """Save ASCII diagram to file"""
    ascii_graph = compiled_workflow.get_graph().draw_ascii()
    
    output_path = Path("WORKFLOW_ASCII.txt")
    with open(output_path, "w") as f:
        f.write(ascii_graph)
    
    print(f"✓ ASCII diagram saved to {output_path}")
    return ascii_graph

def save_png_diagram():
    """Save PNG diagram to file"""
    try:
        png_bytes = compiled_workflow.get_graph().draw_mermaid_png()
        
        output_path = Path("WORKFLOW_DIAGRAM.png")
        with open(output_path, "wb") as f:
            f.write(png_bytes)
        
        print(f"✓ PNG diagram saved to {output_path} ({len(png_bytes)} bytes)")
        return output_path
    except Exception as e:
        print(f"⚠ PNG diagram generation failed: {e}")
        print("  (Requires 'playwright' package: pip install playwright)")
        return None

if __name__ == "__main__":
    print("Exporting workflow diagrams...\n")
    
    mermaid = save_mermaid_diagram()
    print("\nMermaid Output:")
    print("-" * 60)
    print(mermaid[:500] + "..." if len(mermaid) > 500 else mermaid)
    
    try:
        ascii_diag = save_ascii_diagram()
        print("\nASCII Output:")
        print("-" * 60)
        print(ascii_diag[:500] + "..." if len(ascii_diag) > 500 else ascii_diag)
    except Exception as e:
        print(f"\n⚠ ASCII diagram not available: {e}")
    
    png_path = save_png_diagram()
    
    print("\n✓ Workflow diagrams exported successfully!")
