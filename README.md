# Voice RAG Bot - AI Customer Support System

**Status**: ✅ **FULLY FUNCTIONAL** | Latest Update: May 30, 2026

## 📋 Quick Overview

Voice RAG Bot is an intelligent AI customer support system that:
- 🎤 **Accepts voice input** via microphone or audio file upload
- 🧠 **Processes with LLM** (Groq) for intent detection and response generation
- 📚 **Retrieves relevant context** from knowledge base and customer history using vector search
- 😊 **Analyzes sentiment** to provide empathetic, sentiment-aware responses
- 🔊 **Generates speech output** via text-to-speech
- 📊 **Orchestrates 9-node workflow** using LangGraph

**Tech Stack**: Faster Whisper (STT) → LangGraph (9 nodes) → Groq LLM → Qdrant (Vector DB) → gTTS (TTS)

---

## 🚀 Quick Start (3 Steps)

### Step 1: Prerequisites
- Docker Desktop running (for Qdrant)
- Python 3.11+
- Git (optional)

### Step 2: Start Qdrant (Vector Database)
```bash
docker run -p 6333:6333 qdrant/qdrant:latest
```
Leave this running in background. ✅ System will auto-create collections.

### Step 3: Start Voice RAG Bot
```bash
cd d:\Voice RAG Bot\voice-rag-bot

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Run startup script (starts backend + Streamlit)
.\START_SYSTEM.ps1
```

**Or start services manually:**

Terminal 1 (Backend):
```bash
.\venv\Scripts\Activate.ps1
python backend/main.py
# Runs on http://localhost:8000
```

Terminal 2 (Frontend):
```bash
.\venv\Scripts\Activate.ps1
streamlit run frontend/streamlit_app.py
# Opens http://localhost:8501
```

---

## 📖 Usage Guide

### Via Streamlit Frontend (Recommended)

1. **Open Browser**: http://localhost:8501
2. **Enter Customer ID**: Unique identifier for customer (enables history tracking)
3. **Choose Input Method**:
   - **Option A**: Click 🎤 **Record** → Speak your message → **Process Audio**
   - **Option B**: Upload audio file (MP3/WAV)
   - **Option C**: Type message directly in text area
4. **View Results** (automatically displayed):
   - 📝 Generated Response
   - 🎯 Detected Intent (+ confidence)
   - 😊 Sentiment Analysis (+ confidence)
   - 🏷️ Extracted Entities
   - 📚 Knowledge Base context (if relevant)
   - 📜 Customer History (if relevant)
   - 🔊 Audio playback of response

### Via REST API (For Integration)

**Process Audio:**
```bash
curl -X POST "http://localhost:8000/process-audio?customer_id=CUST_001" \
  -F "file=@voice_message.wav"
```

**Process Text:**
```bash
curl -X POST "http://localhost:8000/process-text" \
  -d "user_input=I want to return my laptop&customer_id=CUST_001"
```

**Health Check:**
```bash
curl http://localhost:8000/health
```

---

## 📊 System Architecture

```
Input Layer
  ├─ 🎤 Audio Input (Streamlit st.audio_input)
  └─ 📝 Text Input (Streamlit text area)
         ↓
Speech-to-Text
  └─ Faster Whisper (base model, CPU inference)
         ↓
Orchestration Layer (LangGraph - 9 Nodes)
  1. sentiment_analysis (DistilBERT)
  2. entity_extraction (BERT-base-NER)
  3. intent_detection (Groq LLM)
  4. retrieval_router (Qdrant search)
  5. context_builder (Format prompt)
  6. response_generation (Groq LLM)
  7. validation (Hallucination checks)
  8. memory_persistence (Qdrant upsert)
  9. tts_generation (gTTS)
         ↓
Output Layer
  ├─ 📝 Text Response
  ├─ 😊 Sentiment-aware Tone
  ├─ 🔊 Audio File (MP3)
  └─ 🎯 Intent Classification
```

---

## 🔧 Configuration

**Environment Variables** (`.env`):
```
GROQ_API_KEY=your_groq_api_key_here
QDRANT_URL=http://localhost:6333
BACKEND_URL=http://localhost:8000
VECTOR_DIMENSION=1024
EMBEDDING_MODEL=BAAI/bge-m3
GROQ_MODEL=openai/gpt-oss-20b
KB_COLLECTION_NAME=knowledge_base
HISTORY_COLLECTION_NAME=customer_history
WHISPER_MODEL=base
```

---

## 📝 Sample Data

Load sample data (4 KB documents + 4 customer history records):
```bash
.\venv\Scripts\Activate.ps1
python data/load_sample_data.py
```

**Included Data:**
- KB Documents: Return Policy, Shipping Info, Warranty Info, Account Management
- Customer History: 4 interactions (complaints, refunds, inquiries)

---

## 🧪 Testing

### Quick Verification
```bash
# Test complete pipeline (end-to-end)
.\venv\Scripts\Activate.ps1
python tests/test_full_integration.py
```

**Expected Output**: ✅ FULL INTEGRATION TEST PASSED

### Component Status
- ✅ All 9 nodes connected and working
- ✅ FastAPI endpoints operational
- ✅ Qdrant vector search functional
- ✅ LLM integration responding
- ✅ Audio processing working
- ✅ Sample data loadable

---

## 🎯 Intent Types Supported

| Intent | Example | Response |
|--------|---------|----------|
| `refund_request` | "I want to return this" | Empathetic, processing info |
| `order_status` | "Where's my order?" | Tracking info |
| `product_inquiry` | "Tell me about...?" | Product details |
| `billing_issue` | "My charge was wrong" | Empathetic, billing process |
| `warranty_claim` | "Product broke" | Warranty eligibility info |
| `account_management` | "Change my password" | Account instructions |
| `general_support` | "How do I...?" | General assistance |
| `complaint` | "This is unacceptable" | Empathetic, resolution steps |
| `other` | Misc questions | General help |

---

## 📊 Response Quality Factors

1. **Sentiment Detection**: POSITIVE/NEGATIVE/NEUTRAL classification
2. **Confidence Scores**: 0-1 for both intent and sentiment
3. **Context Retrieval**: Up to 3 KB documents + customer history
4. **Tone Matching**: Empathetic for negative, professional for neutral, friendly for positive
5. **Hallucination Prevention**: Validation layer checks for accuracy

---

## 🐛 Troubleshooting

### Issue: "Backend Not Connected"
**Solution**: Ensure FastAPI backend is running
```bash
python backend/main.py
```

### Issue: "Qdrant Connection Error"
**Solution**: Start Qdrant Docker container
```bash
docker run -p 6333:6333 qdrant/qdrant:latest
```

### Issue: "Groq API Error"
**Solution**: Check GROQ_API_KEY in `.env` file
```bash
# Verify key is set
echo $env:GROQ_API_KEY
```

### Issue: "Audio Processing Timeout"
**Solution**: Processing may take 30-60 seconds for audio
- First run downloads models (Whisper, BGE-M3, DistilBERT)
- Subsequent runs are faster
- Ensure sufficient disk space (~5GB)

### Issue: "Module Not Found"
**Solution**: Reinstall dependencies
```bash
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

---

## 📁 Project Structure

```
d:\Voice RAG Bot\voice-rag-bot\
├── backend/
│   ├── main.py                 FastAPI server
│   └── config.py               Configuration
├── frontend/
│   └── streamlit_app.py        Web UI
├── orchestration/
│   ├── langgraph_workflow.py   9-node workflow
│   ├── state.py                State management
│   └── nodes/                  Individual nodes
│       ├── sentiment_analysis.py
│       ├── entity_extraction.py
│       ├── intent_detection.py
│       ├── retrieval_router.py
│       ├── context_builder.py
│       ├── response_generation.py
│       ├── validation.py
│       ├── memory_persistence.py
│       └── tts_generation.py
├── rag/
│   ├── qdrant_manager.py       Vector DB client
│   └── embedding_manager.py    BGE-M3 embeddings
├── data/
│   ├── load_sample_data.py     Sample data loader
│   └── audio_output/           Generated audio files
├── tests/
│   └── test_full_integration.py End-to-end test
├── .env                        Configuration
├── requirements.txt            Dependencies
├── START_SYSTEM.ps1           Quick start script
└── venv/                       Python environment
```

---

## 🔄 Workflow Execution (Behind the Scenes)

1. **sentiment_analysis**: Input → DistilBERT → POSITIVE/NEGATIVE/NEUTRAL
2. **entity_extraction**: Input → BERT-NER → Extract names, locations, etc.
3. **intent_detection**: Input → Groq LLM → 9-intent classification
4. **retrieval_router**: Intent → Qdrant search → 3 KB docs + customer history
5. **context_builder**: Format contexts → Unified prompt
6. **response_generation**: Prompt → Groq LLM → Response text
7. **validation**: Check hallucinations → Retry if needed
8. **memory_persistence**: Embed response → Upsert to Qdrant
9. **tts_generation**: Response text → gTTS → MP3 audio file

---

## 📊 Performance Metrics (Approximate)

| Component | Time | Notes |
|-----------|------|-------|
| STT (Audio → Text) | 5-15s | Depends on audio length |
| Sentiment Analysis | 0.5s | DistilBERT inference |
| Entity Extraction | 0.5s | BERT-NER inference |
| Intent Detection | 1-2s | Groq API call |
| KB Search | 0.2s | Qdrant vector search |
| Response Generation | 2-5s | Groq streaming |
| Validation | 0.5s | Local checks |
| TTS Generation | 2-5s | gTTS processing |
| **Total End-to-End** | **12-35s** | First run slower (model loading) |

---

## 💡 Tips & Tricks

### Faster Processing
- Use text input instead of audio (skips STT)
- System caches models after first run
- Keep audio messages under 30 seconds

### Better Responses
- Use clear, grammatically correct input
- Provide context ("purchased last week" vs "bought before")
- Specify what you need (return, refund, replacement)

### Debugging
- Check `backend/main.py` logs for errors
- View Qdrant collections: http://localhost:6333/api/swagger/index.html
- Monitor Streamlit server in terminal for issues

---

## 🚀 Next Steps

1. **Load Sample Data**: `python data/load_sample_data.py`
2. **Test with Demo Scenarios**: Use Streamlit to test various intents
3. **Customize KB Documents**: Add your own documents to Qdrant
4. **Fine-tune Prompts**: Edit prompts in `prompts/` directory
5. **Production Deployment**: Add authentication, rate limiting, monitoring

---

## 📞 Support & References

**Documentation Files:**
- `data/DATA_REQUIREMENTS.md` - Data schema documentation
- `.env` - Environment configuration

**API Endpoints:**
- `POST /process-audio` - Audio input endpoint
- `POST /process-text` - Text input endpoint
- `GET /health` - Health check

**Backend Logs:**
- Location: Console output when running `python backend/main.py`
- Check for errors, model loading, API calls

---

## 📝 License & Attribution

**Components**:
- **Groq LLM**: Free tier, gpt-oss-20b model
- **Faster Whisper**: OpenAI (MIT License)
- **LangGraph**: LangChain (Open Source)
- **Qdrant**: Open source vector database
- **BGE-M3**: BAAI embeddings model
- **DistilBERT**: Hugging Face transformers
- **gTTS**: Google Text-to-Speech

---

## ✅ Verification Checklist

Before considering system "ready for production":

- [ ] Backend running on http://localhost:8000
- [ ] Qdrant running on http://localhost:6333
- [ ] Streamlit frontend accessible at http://localhost:8501
- [ ] Sample data loaded (`python data/load_sample_data.py`)
- [ ] Integration test passing (`python tests/test_full_integration.py`)
- [ ] Audio input working (record or upload)
- [ ] All 9 nodes executing (check logs)
- [ ] Response generation working
- [ ] Audio playback working
- [ ] History tracking working (multiple messages same customer)

---

**Built with ❤️ | Last Updated: May 30, 2026**
