"""
Streamlit Frontend - Voice RAG Bot
Interactive UI for audio input, processing, and response playback
"""

import streamlit as st
import requests
import json
import os
import time
import base64
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

# Page configuration
st.set_page_config(
    page_title="Voice RAG Bot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Styling
st.markdown("""
<style>
    .main {
        padding: 0rem 1rem;
    }
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 1.1rem;
        font-weight: 500;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    .error-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
    }
    .info-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# CONFIGURATION
# ============================================================================
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
DATA_DIR = Path("data/audio_output")
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Session state initialization
if "customer_id" not in st.session_state:
    st.session_state.customer_id = "CUST_001"
if "processing" not in st.session_state:
    st.session_state.processing = False
if "last_response" not in st.session_state:
    st.session_state.last_response = None
if "history" not in st.session_state:
    st.session_state.history = []
if "voice_bot_mode" not in st.session_state:
    st.session_state.voice_bot_mode = False
if "voice_bot_session" not in st.session_state:
    st.session_state.voice_bot_session = None
if "voice_bot_active" not in st.session_state:
    st.session_state.voice_bot_active = False
if "voice_bot_messages" not in st.session_state:
    st.session_state.voice_bot_messages = []
if "pending_audio" not in st.session_state:
    st.session_state.pending_audio = None
if "processing_audio" not in st.session_state:
    st.session_state.processing_audio = False
if "last_processed_audio_id" not in st.session_state:
    st.session_state.last_processed_audio_id = None

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def check_backend_health() -> bool:
    """Check if FastAPI backend is running"""
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        return False
    except requests.exceptions.Timeout:
        return False
    except Exception as e:
        return False


def process_audio_file(audio_bytes: bytes, customer_id: str) -> Optional[Dict[str, Any]]:
    """Send audio to backend for processing"""
    try:
        from io import BytesIO
        
        # Send audio bytes directly as file to backend
        with st.spinner("Processing audio... (may take 30-60 seconds)"):
            # Create file-like object from bytes
            audio_file = BytesIO(audio_bytes)
            audio_file.name = f"audio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
            
            files = {"file": (audio_file.name, audio_file, "audio/wav")}
            response = requests.post(
                f"{BACKEND_URL}/process-audio",
                files=files,
                params={"customer_id": customer_id},
                timeout=120
            )
        
        if response.status_code == 200:
            result = response.json()
            return result
        else:
            st.error(f"Backend error: {response.status_code}")
            st.error(response.text)
            return None
            
    except requests.exceptions.Timeout:
        st.error("Request timeout. Processing took too long.")
        return None
    except Exception as e:
        st.error(f"Error processing audio: {str(e)}")
        import traceback
        st.error(traceback.format_exc())
        return None


def process_text_input(user_input: str, customer_id: str) -> Optional[Dict[str, Any]]:
    """Send text to backend for processing"""
    try:
        with st.spinner("Processing text... (may take 20-30 seconds)"):
            response = requests.post(
                f"{BACKEND_URL}/process-text",
                params={
                    "user_input": user_input,
                    "customer_id": customer_id
                },
                timeout=120
            )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Backend error: {response.status_code}")
            st.error(response.text)
            return None
            
    except requests.exceptions.Timeout:
        st.error("Request timeout. Processing took too long.")
        return None
    except Exception as e:
        st.error(f"Error processing text: {str(e)}")
        return None




def voice_bot_start(customer_id: str) -> Optional[Dict[str, Any]]:
    """Start voice bot session"""
    try:
        response = requests.post(
            f"{BACKEND_URL}/voice-bot/start",
            params={"customer_id": customer_id},
            timeout=60
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error starting voice bot: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error starting voice bot: {str(e)}")
        return None


def voice_bot_process_message(user_message: str) -> Optional[Dict[str, Any]]:
    """Process message in voice bot session"""
    try:
        response = requests.post(
            f"{BACKEND_URL}/voice-bot/message",
            params={"user_message": user_message},
            timeout=120
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Backend error {response.status_code}: {response.text}")
            return None
    except Exception as e:
        st.error(f"Backend connection error: {str(e)}")
        return None


def voice_bot_end() -> Optional[Dict[str, Any]]:
    """End voice bot session"""
    try:
        response = requests.post(
            f"{BACKEND_URL}/voice-bot/end",
            timeout=10
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        return None


def display_response_results(response: Dict[str, Any]):
    """Display formatted response from backend"""
    
    # Display latency metrics first if available
    latency_metrics = response.get("latency_metrics")
    if latency_metrics:
        st.markdown("### ⏱️ Performance Metrics")
        
        total_time = latency_metrics.get("total_time_ms", 0)
        modules = latency_metrics.get("modules", {})
        breakdown = latency_metrics.get("breakdown_percent", {})
        
        # Display total time prominently
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Processing Time", f"{total_time:.0f} ms", f"{total_time/1000:.2f}s")
        with col2:
            fastest = min(modules.items(), key=lambda x: x[1]) if modules else ("N/A", 0)
            st.metric("Fastest Module", fastest[0].replace("_", " ").title(), f"{fastest[1]:.0f} ms")
        with col3:
            slowest = max(modules.items(), key=lambda x: x[1]) if modules else ("N/A", 0)
            st.metric("Slowest Module", slowest[0].replace("_", " ").title(), f"{slowest[1]:.0f} ms")
        
        # Module breakdown with progress bars
        with st.expander("📊 Detailed Module Breakdown", expanded=True):
            st.markdown("#### Time per Module")
            
            # Sort modules by time
            sorted_modules = sorted(modules.items(), key=lambda x: x[1], reverse=True)
            
            for module_name, time_ms in sorted_modules:
                percent = breakdown.get(module_name, 0)
                display_name = module_name.replace("_", " ").title()
                
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.write(f"**{display_name}**")
                with col2:
                    st.write(f"{time_ms:.2f} ms")
                with col3:
                    st.write(f"{percent:.1f}%")
                
                # Progress bar
                st.progress(percent / 100)
        
        st.markdown("---")
    
    # Create tabs for different result sections
    tabs = st.tabs([
        "📝 Response",
        "🎯 Intent",
        "😊 Sentiment",
        "🏷️ Entities",
        "📚 Knowledge Base",
        "📜 History",
        "🔊 Audio"
    ])
    
    # Tab 1: Main Response
    with tabs[0]:
        st.markdown("### Generated Response")
        st.info(response.get("response_text", "No response generated"))
        
        # Save to history
        st.session_state.history.append({
            "timestamp": datetime.now().isoformat(),
            "customer_id": st.session_state.customer_id,
            "response": response.get("response_text", ""),
            "intent": response.get("intent", ""),
            "sentiment": response.get("sentiment", "")
        })
    
    # Tab 2: Intent Detection
    with tabs[1]:
        intent = response.get("intent", "")
        st.metric("Detected Intent", intent if intent else "N/A")
        
        intent_types = {
            "refund_request": "Customer wants to return/refund a product",
            "order_status": "Customer inquiring about order tracking",
            "inquiry": "Customer asking product details",
            "billing": "Customer has billing/payment problems",
            "complaint": "Customer complaint",
            "account_issue": "Account settings/updates",
            "escalation": "Escalation needed",
            "product_question": "Product inquiry",
            "other": "Other inquiry"
        }
        
        if intent in intent_types:
            st.write(f"**Category**: {intent_types[intent]}")
    
    # Tab 3: Sentiment Analysis
    with tabs[2]:
        sentiment = response.get("sentiment", "NEUTRAL")
        
        if sentiment == "POSITIVE":
            color = "🟢"
            tone = "Positive"
        elif sentiment == "NEGATIVE":
            color = "🔴"
            tone = "Negative"
        else:
            color = "🟡"
            tone = "Neutral"
        
        st.metric("Sentiment", f"{color} {tone}")
        st.write(f"**Interpretation**: Response was generated with {tone.lower()} tone")
    
    # Tab 4: Entities
    with tabs[3]:
        entities = response.get("entities", {})
        if entities:
            for entity_type, values in entities.items():
                if values:
                    st.write(f"**{entity_type.upper()}**")
                    for entity in values:
                        st.write(f"  • {entity}")
        else:
            st.info("No entities extracted from input")
    
    # Tab 5: Knowledge Base Context
    with tabs[4]:
        kb_context = response.get("kb_context", "")
        if kb_context and isinstance(kb_context, str) and kb_context.strip() != "No relevant policies found.":
            st.write("**Retrieved Documents:**")
            st.write(kb_context)
        else:
            st.info("No KB documents retrieved")
    
    # Tab 6: Customer History
    with tabs[5]:
        history_context = response.get("history_context", "")
        if history_context and isinstance(history_context, str) and history_context.strip() != "No customer history available.":
            st.write("**Customer History:**")
            st.write(history_context)
        else:
            st.info("No customer history found")
    
    # Tab 7: Audio Output
    with tabs[6]:
        audio_path = response.get("audio_path", "")
        if audio_path and audio_path.strip():
            try:
                # Normalize path
                audio_file_path = Path(audio_path.replace("\\", "/"))
                if not audio_file_path.is_absolute():
                    project_root = Path(__file__).parent.parent
                    audio_file_path = project_root / audio_file_path
                
                if audio_file_path.exists():
                    st.write(f"**Audio file**: {audio_path}")
                    with open(audio_file_path, "rb") as audio_file:
                        st.audio(audio_file, format="audio/mp3")
                else:
                    st.warning(f"Audio file not found: {audio_file_path}")
            except Exception as e:
                st.error(f"Could not load audio file: {str(e)}")
        else:
            st.warning("No audio file generated")


# ============================================================================
# MAIN UI LAYOUT
# ============================================================================

# Header
st.title("🤖 Voice RAG Bot")
st.markdown("AI Customer Support with Voice Recognition and Retrieval-Augmented Generation")

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Backend status with refresh
    col1, col2 = st.columns([3, 1])
    with col1:
        st.write("**Backend Status**")
    with col2:
        if st.button("🔄", help="Refresh status", key="refresh_health"):
            st.rerun()
    
    backend_healthy = check_backend_health()
    if backend_healthy:
        st.success("✅ Backend Connected")
        st.caption(f"URL: {BACKEND_URL}")
    else:
        st.error("❌ Backend Not Connected")
        st.error(f"Cannot reach {BACKEND_URL}")
        st.info("**To fix:**")
        st.code("python -m uvicorn backend.main:app --reload --port 8000", language="bash")
        st.info("**Or use startup script:**")
        st.code(".\\START_SYSTEM.ps1", language="bash")
    
    # Customer ID input
    st.subheader("Customer Information")
    customer_id = st.text_input(
        "Customer ID",
        value=st.session_state.customer_id,
        help="Unique identifier for customer (used for history)"
    )
    st.session_state.customer_id = customer_id
    
    st.divider()
    
    # Model information
    st.subheader("System Components")
    st.write("**LLM**: Groq (gpt-oss-20b)")
    st.write("**STT**: Faster Whisper (base)")
    st.write("**Vector DB**: Qdrant")
    st.write("**Embeddings**: BGE-M3 (1024-dim)")
    st.write("**Sentiment**: DistilBERT")
    st.write("**NER**: BERT-base-NER")

# Main content
st.divider()

# Voice Bot Mode Toggle
col1, col2, col3 = st.columns([1, 3, 1])
with col1:
    voice_bot_enabled = st.toggle("🤖 Voice Bot Mode", value=st.session_state.voice_bot_mode, key="voice_bot_toggle")
    st.session_state.voice_bot_mode = voice_bot_enabled

if voice_bot_enabled:
    # Voice Bot Interface
    st.markdown("### 🎙️ Voice Bot Assistant")
    
    if not st.session_state.voice_bot_active:
        # Start button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🎙️ Start Conversation", use_container_width=True, key="start_voice_bot"):
                with st.spinner("Starting voice bot..."):
                    result = voice_bot_start(st.session_state.customer_id)
                    if result:
                        st.session_state.voice_bot_session = result.get("session_id")
                        st.session_state.voice_bot_active = True
                        greeting_audio = result.get("audio_path", "")
                        st.session_state.voice_bot_messages = [
                            {
                                "role": "assistant",
                                "content": result.get("greeting"),
                                "audio_path": greeting_audio
                            }
                        ]
                        st.rerun()
    
    else:
        # Conversation display
        st.markdown("#### Conversation")
        
        # Display conversation history
        for msg in st.session_state.voice_bot_messages:
            if msg["role"] == "assistant":
                with st.chat_message("assistant", avatar="🤖"):
                    st.write(msg["content"])
                    # Play audio if available
                    audio_path = msg.get("audio_path", "")
                    if audio_path and audio_path.strip():
                        try:
                            # Normalize path and check in project root
                            audio_file_path = Path(audio_path.replace("\\", "/"))
                            if not audio_file_path.is_absolute():
                                project_root = Path(__file__).parent.parent
                                audio_file_path = project_root / audio_file_path
                            
                            if audio_file_path.exists():
                                with open(audio_file_path, "rb") as audio_file:
                                    audio_bytes = audio_file.read()
                                    audio_b64 = base64.b64encode(audio_bytes).decode()
                                    st.markdown(f"""
                                    <audio autoplay controls style="width: 100%;">
                                        <source src="data:audio/mpeg;base64,{audio_b64}" type="audio/mpeg">
                                    </audio>
                                    """, unsafe_allow_html=True)
                            else:
                                st.caption(f"⚠️ Audio file not found: {audio_file_path}")
                        except Exception as e:
                            st.caption(f"⚠️ Error loading audio: {str(e)}")
            else:
                with st.chat_message("user", avatar="👤"):
                    st.write(msg["content"])
        
        # Voice conversation section
        st.markdown("---")
        st.markdown("#### 🎤 Record your message:")
        
        # Voice input - Store audio in session state
        audio_bytes = st.audio_input(
            "Record your message",
            label_visibility="collapsed",
            key="voice_bot_audio_input"
        )
        
        # If new audio recorded, store it with unique ID
        if audio_bytes:
            audio_id = id(audio_bytes)
            if audio_id != st.session_state.last_processed_audio_id:
                st.session_state.pending_audio = audio_bytes
                st.session_state.last_processed_audio_id = audio_id
                st.session_state.processing_audio = True
        
        # Process pending audio (happens on next render after audio is saved)
        if st.session_state.pending_audio and st.session_state.processing_audio:
            # Immediately mark as processing to prevent duplicate processing
            st.session_state.processing_audio = False
            
            st.info("🎤 Processing audio...")
            try:
                from io import BytesIO
                from faster_whisper import WhisperModel
                
                # Convert UploadedFile to bytes if needed
                audio_data = st.session_state.pending_audio
                if hasattr(audio_data, 'read'):
                    audio_data = audio_data.read()
                
                st.info("Loading Whisper model...")
                @st.cache_resource
                def load_whisper():
                    return WhisperModel("base", device="cpu", compute_type="int8")
                
                whisper = load_whisper()
                st.success("✅ Whisper model loaded")
                
                st.info("Transcribing audio...")
                audio_file = BytesIO(audio_data)
                segments, info = whisper.transcribe(audio_file, language="en")
                transcribed_text = " ".join([segment.text for segment in segments])
                
                if transcribed_text.strip():
                    st.success(f"✅ Transcribed: {transcribed_text}")
                    
                    # Add user message
                    st.session_state.voice_bot_messages.append({
                        "role": "user",
                        "content": f"🎤 {transcribed_text}"
                    })
                    
                    st.info("🤖 Sending to bot...")
                    result = voice_bot_process_message(transcribed_text)
                    
                    if result:
                        response = result.get("response", "")
                        audio_path = result.get("audio_path", "")
                        
                        if response:
                            st.success("✅ Bot responded")
                            # Add ONLY ONE bot response
                            st.session_state.voice_bot_messages.append({
                                "role": "assistant",
                                "content": response,
                                "audio_path": audio_path
                            })
                            
                            # Clear pending audio immediately
                            st.session_state.pending_audio = None
                            st.session_state.processing_audio = False
                        else:
                            st.error("❌ Bot response is empty")
                            st.session_state.pending_audio = None
                            st.session_state.processing_audio = False
                    else:
                        st.error("❌ Backend returned None")
                        st.session_state.pending_audio = None
                        st.session_state.processing_audio = False
                else:
                    st.warning("⚠️ No speech detected in audio")
                    st.session_state.pending_audio = None
                    st.session_state.processing_audio = False
                    
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.session_state.pending_audio = None
                st.session_state.processing_audio = False
                import traceback
                st.write(traceback.format_exc())
        
        # End conversation button
        st.markdown("---")
        if st.button("🛑 End Conversation", use_container_width=True, key="end_voice_bot"):
            with st.spinner("Ending session..."):
                result = voice_bot_end()
                st.session_state.voice_bot_active = False
                st.session_state.voice_bot_messages = []
                st.success("✅ Session ended. Thank you!")
                st.rerun()

else:
    # Regular Input Tabs
    st.markdown("### 💬 Manual Input Mode")
    
    # Tabs for input methods
    input_tab1, input_tab2 = st.tabs(["🎤 Audio Input", "📝 Text Input"])

    with input_tab1:
        st.subheader("Upload or Record Audio")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Option 1: Record Audio**")
            audio_data = st.audio_input(
                "Record your message",
                label_visibility="collapsed",
                key="audio_input"
            )
            
            if audio_data:
                st.success("Audio recorded successfully!")
                if st.button("🔄 Process Audio", key="process_audio_btn"):
                    response = process_audio_file(audio_data.getvalue(), st.session_state.customer_id)
                    if response:
                        st.session_state.last_response = response
                        st.success("✅ Processing complete!")
                        st.rerun()
        
        with col2:
            st.write("**Option 2: Upload Audio File**")
            uploaded_file = st.file_uploader(
                "Upload an MP3 or WAV file",
                type=["mp3", "wav"],
                label_visibility="collapsed"
            )
            
            if uploaded_file:
                st.success(f"File uploaded: {uploaded_file.name}")
                if st.button("🔄 Process Uploaded Audio", key="process_uploaded_btn"):
                    response = process_audio_file(uploaded_file.getvalue(), st.session_state.customer_id)
                    if response:
                        st.session_state.last_response = response
                        st.success("✅ Processing complete!")
                        st.rerun()

    with input_tab2:
        st.subheader("Enter Text Directly")
        
        # Text area for input
        user_input = st.text_area(
            "Enter your message",
            placeholder="E.g., 'I want to return my defective laptop purchased last week'",
            height=100,
            label_visibility="collapsed"
        )
        
        if user_input:
            col1, col2, col3 = st.columns([1, 1, 2])
            
            with col1:
                if st.button("🚀 Process Text", use_container_width=True):
                    response = process_text_input(user_input, st.session_state.customer_id)
                    if response:
                        st.session_state.last_response = response
                        st.success("✅ Processing complete!")
                        st.rerun()
            
            with col2:
                if st.button("🔄 Clear", use_container_width=True):
                    st.rerun()
            
            with col3:
                st.caption("ℹ️ Processing may take 20-30 seconds")

# Display last response if available
st.divider()

if st.session_state.last_response:
    st.subheader("📊 Latest Results")
    display_response_results(st.session_state.last_response)

# Conversation history
st.divider()

with st.expander("📜 Conversation History"):
    if st.session_state.history:
        for i, record in enumerate(st.session_state.history, 1):
            with st.container(border=True):
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.caption(f"Time: {record['timestamp'][:16]}")
                with col2:
                    st.caption(f"Customer: {record['customer_id']}")
                with col3:
                    st.caption(f"Intent: {record['intent']}")
                with col4:
                    st.caption(f"Sentiment: {record['sentiment']}")
                st.write(record['response'][:150] + "..." if len(record['response']) > 150 else record['response'])
    else:
        st.info("No conversation history yet")

# Footer
st.divider()
st.markdown("""
---
**Voice RAG Bot** | Powered by Groq LLM, Qdrant Vector DB, and LangGraph Orchestration  
For technical support, refer to the backend logs at `backend/main.py`
""")
