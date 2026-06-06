#!/usr/bin/env python3
"""Export LangGraph workflow diagram as PNG"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from orchestration.langgraph_workflow import compiled_workflow

def save_png_diagram():
    """Save PNG diagram to file"""
    try:
        png_bytes = compiled_workflow.get_graph().draw_mermaid_png()
        
        output_path = Path("WORKFLOW_DIAGRAM.png")
        with open(output_path, "wb") as f:
            f.write(png_bytes)
        
        print(f"✓ Workflow PNG diagram saved: {output_path} ({len(png_bytes)} bytes)")
        return output_path
    except Exception as e:
        print(f"Error: PNG diagram generation failed - {e}")
        print("(Requires 'playwright' package: pip install playwright)")
        return None

if __name__ == "__main__":
    print("Exporting workflow diagram...\n")
    png_path = save_png_diagram()
    
    if png_path:
        print(f"\n✓ Successfully exported: {png_path}")
