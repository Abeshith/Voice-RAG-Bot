"""Streamlit page for workflow visualization"""

import streamlit as st
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from orchestration.langgraph_workflow import compiled_workflow

st.set_page_config(page_title="Workflow Diagram", layout="wide")

st.title("🔄 LangGraph Workflow Diagram")

st.markdown("""
This page displays the 9-node orchestration pipeline for the Voice RAG Bot:
- **Nodes**: Sentiment Analysis → Entity Extraction → Intent Detection → Retrieval → Context → Response → Validation → Memory → TTS
- **Parallel Execution**: Sentiment & Entity steps run in parallel
- **Conditional Logic**: Validation node can retry response generation if quality checks fail
""")

try:
    # Generate PNG diagram
    png_bytes = compiled_workflow.get_graph().draw_mermaid_png()
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.image(png_bytes, caption="Voice RAG Bot - 9-Node Workflow", use_column_width=True)
    
    with col2:
        st.subheader("Workflow Details")
        
        details = """
        **9 Nodes:**
        1. Sentiment Analysis
        2. Entity Extraction
        3. Intent Detection
        4. Retrieval Router
        5. Context Builder
        6. Response Generation
        7. Validation
        8. Memory Persistence
        9. TTS Generation
        
        **Features:**
        - Parallel execution
        - Conditional retries
        - Latency tracking
        - Audio generation
        """
        st.markdown(details)
        
        if st.button("📥 Download Diagram as PNG"):
            st.download_button(
                label="Download PNG",
                data=png_bytes,
                file_name="workflow_diagram.png",
                mime="image/png"
            )
            st.success("✓ PNG ready for download!")
    
except Exception as e:
    st.error(f"❌ Error generating diagram: {e}")
    st.info("💡 Make sure playwright is installed: `pip install playwright`")

st.divider()

try:
    # Display Mermaid text version as fallback
    mermaid_text = compiled_workflow.get_graph().draw_mermaid()
    
    with st.expander("📄 View Mermaid Source"):
        st.code(mermaid_text, language="mermaid")
        
except Exception as e:
    st.warning(f"Could not generate Mermaid source: {e}")
