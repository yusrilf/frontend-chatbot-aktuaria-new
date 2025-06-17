import streamlit as st
import requests
import json
from datetime import datetime
import uuid
import re

# Konfigurasi halaman
st.set_page_config(
    page_title="Konsultan Dana Pensiun",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS untuk styling
st.markdown("""
<style>
    .main-title {
        text-align: center;
        color: #ffffff;
        font-size: 2.5rem;
        margin-bottom: 2rem;
        background: linear-gradient(135deg, #1a5490, #2196f3);
        padding: 1.5rem;
        border-radius: 15px;
        font-weight: bold;
        box-shadow: 0 4px 20px rgba(26, 84, 144, 0.3);
    }
    
    .chat-container {
        max-width: 800px;
        margin: 0 auto;
        padding: 1rem;
    }
    
    .user-message {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        padding: 1rem;
        border-radius: 18px 18px 6px 18px;
        margin: 1rem 0 1rem auto;
        max-width: 70%;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    .assistant-message {
        background: white;
        color: #374151;
        padding: 1rem;
        border-radius: 18px 18px 18px 6px;
        margin: 1rem auto 1rem 0;
        max-width: 70%;
        border: 1px solid #e5e7eb;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    .message-time {
        font-size: 0.8rem;
        opacity: 0.7;
        margin-top: 0.5rem;
    }
    
    .confidence-badge {
        background: linear-gradient(135deg, #10b981, #059669);
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: bold;
        display: inline-block;
        margin: 0.5rem 0;
    }
    
    .error-message {
        background: linear-gradient(135deg, #ef4444, #dc2626);
        color: white;
        padding: 1rem;
        border-radius: 12px;
        margin: 1rem 0;
        font-weight: 500;
    }
    
    .thinking-indicator {
        background: #f3f4f6;
        color: #6b7280;
        padding: 1rem;
        border-radius: 18px;
        margin: 1rem auto 1rem 0;
        max-width: 200px;
        font-style: italic;
        text-align: center;
    }
    
    .sidebar-metric {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        padding: 1rem;
        border-radius: 12px;
        text-align: center;
        margin: 0.5rem 0;
    }
    
    .status-connected {
        background: linear-gradient(135deg, #10b981, #059669);
        color: white;
        padding: 1rem;
        border-radius: 12px;
        text-align: center;
        font-weight: bold;
    }
    
    .status-disconnected {
        background: linear-gradient(135deg, #ef4444, #dc2626);
        color: white;
        padding: 1rem;
        border-radius: 12px;
        text-align: center;
        font-weight: bold;
    }
    
    .math-display {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        text-align: center;
    }
    
    .info-card {
        background-color: #ffc107;
        color: #000000;
        padding: 1rem;
        border-radius: 8px;
        border: 2px solid #000000;
        margin: 1rem 0;
        font-weight: 600;
    }
</style>

<script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
<script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
<script>
    window.MathJax = {
        tex: {
            inlineMath: [['$', '$'], ['\\(', '\\)']],
            displayMath: [['$$', '$$'], ['\\[', '\\]']],
            processEscapes: true
        }
    };
</script>
""", unsafe_allow_html=True)

# Fungsi untuk memproses LaTeX
def process_latex(text):
    if not text:
        return text
    text = re.sub(r'\$\$(.*?)\$\$', r'<div class="math-display">$$\1$$</div>', text, flags=re.DOTALL)
    text = re.sub(r'\$([^$]+?)\$', r'$\1$', text)
    return text

# Judul aplikasi
st.markdown('<h1 class="main-title">💰 Konsultan Dana Pensiun Aktuaria</h1>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Konfigurasi")
    
    # API URL
    api_url = st.text_input(
        "URL API:",
        value="https://chatbot-app-service.azurewebsites.net/ask",
        help="Masukkan URL endpoint API"
    )
    
    # Session ID
    if 'session_id' not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())[:8]
    
    session_id = st.text_input(
        "Session ID:",
        value=st.session_state.session_id,
        help="ID sesi untuk melacak percakapan"
    )
    
    # Reset session
    if st.button("🔄 Reset Session", use_container_width=True):
        st.session_state.session_id = str(uuid.uuid4())[:8]
        if 'chat_history' in st.session_state:
            st.session_state.chat_history = []
        st.rerun()
    
    st.divider()
    
    # File upload
    st.subheader("📁 Upload Dokumen")
    uploaded_files = st.file_uploader(
        "Upload file PDF/Word/Excel/MD:",
        type=['pdf', 'docx', 'doc', 'xlsx', 'xls','md'],
        accept_multiple_files=True,
        help="Upload dokumen untuk dianalisis"
    )
    
    if uploaded_files:
        st.success(f"📄 {len(uploaded_files)} file berhasil diupload")
        for file in uploaded_files:
            st.write(f"• {file.name}")
    
    st.divider()
    
    # Info API
    st.subheader("📋 Info API")
    st.markdown("""
    <div class="info-card">
        <strong>Method:</strong> POST<br>
        <strong>Format:</strong><br>
        {<br>
        &nbsp;&nbsp;"question": "...",<br>
        &nbsp;&nbsp;"session_id": "..."<br>
        }
    </div>
    """, unsafe_allow_html=True)
    
    # Status koneksi
    st.subheader("🔗 Status Koneksi")
    try:
        test_response = requests.get(api_url.replace('/ask', '/'), timeout=5)
        st.markdown('<div class="status-connected">✅ Server Terhubung</div>', unsafe_allow_html=True)
    except:
        st.markdown('<div class="status-disconnected">❌ Server Tidak Terhubung</div>', unsafe_allow_html=True)
    
    # Statistik
    if 'chat_history' in st.session_state and st.session_state.chat_history:
        st.subheader("📊 Statistik Chat")
        
        user_messages = len([chat for chat in st.session_state.chat_history if chat["type"] == "user"])
        ai_messages = len([chat for chat in st.session_state.chat_history if chat["type"] == "assistant"])
        errors = len([chat for chat in st.session_state.chat_history if chat["type"] == "error"])
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div class="sidebar-metric">
                <div style="font-size: 1.5rem; font-weight: bold;">{user_messages}</div>
                <div>Pertanyaan</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="sidebar-metric">
                <div style="font-size: 1.5rem; font-weight: bold;">{ai_messages}</div>
                <div>Jawaban AI</div>
            </div>
            """, unsafe_allow_html=True)
        
        if errors > 0:
            st.error(f"⚠️ {errors} Error")
    
    # Clear chat
    if st.button("🗑️ Hapus Riwayat Chat", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()
    
    # Contoh pertanyaan
    st.subheader("💡 Contoh Pertanyaan")
    examples = [
        "Bagaimana cara menghitung dana pensiun untuk 100 karyawan?",
        "Apa itu iuran normal dalam perhitungan pensiun?",
        "Bagaimana formula menghitung premi asuransi jiwa?",
        "Jelaskan tentang liability aktuaria",
        "Bagaimana cara menghitung nilai sekarang anuitas?"
    ]
    
    for i, example in enumerate(examples):
        if st.button(f"📌 {example[:40]}...", key=f"example_{i}", use_container_width=True):
            st.session_state.selected_example = example

# Inisialisasi chat history
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Fungsi API
def call_api(question, session_id, api_url):
    try:
        payload = {
            "question": question,
            "session_id": session_id
        }
        
        response = requests.post(
            api_url,
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json(), None
        else:
            return None, f"Error {response.status_code}: {response.text}"
            
    except requests.exceptions.ConnectionError:
        return None, "❌ Tidak dapat terhubung ke API"
    except requests.exceptions.Timeout:
        return None, "⏱️ Request timeout"
    except Exception as e:
        return None, f"❌ Error: {str(e)}"

# Area chat
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

# Display chat history
if st.session_state.chat_history:
    for chat in st.session_state.chat_history:
        if chat["type"] == "user":
            st.markdown(f"""
            <div class="user-message">
                <strong>👤 Anda:</strong><br>
                {chat['content']}
                <div class="message-time">{chat['timestamp']}</div>
            </div>
            """, unsafe_allow_html=True)
            
        elif chat["type"] == "assistant":
            processed_content = process_latex(chat['content'])
            st.markdown(f"""
            <div class="assistant-message">
                <strong>🤖 AI Aktuaria:</strong><br>
                {processed_content}
                <div class="message-time">{chat['timestamp']}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Confidence
            if 'confidence' in chat:
                confidence_pct = int(chat['confidence'] * 100)
                st.markdown(f"""
                <div class="confidence-badge">
                    📊 Keyakinan: {confidence_pct}%
                </div>
                """, unsafe_allow_html=True)
            
            # Sources
            if 'sources' in chat and chat['sources']:
                with st.expander(f"📚 Lihat {len(chat['sources'])} sumber referensi"):
                    for j, source in enumerate(chat['sources'], 1):
                        st.markdown(f"""
                        **📁 Sumber {j}:** {source.get('filename', 'N/A')}  
                        **📑 Header:** {' > '.join(source.get('headers', {}).values())}  
                        **👁️ Preview:** {source.get('preview', 'N/A')[:200]}...
                        """)
                        
        elif chat["type"] == "error":
            st.markdown(f"""
            <div class="error-message">
                <strong>⚠️ Error ({chat['timestamp']}):</strong><br>
                {chat['content']}
            </div>
            """, unsafe_allow_html=True)

# Thinking indicator
if 'is_thinking' in st.session_state and st.session_state.is_thinking:
    st.markdown("""
    <div class="thinking-indicator">
        🤖 AI sedang berpikir...
    </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Input area
st.subheader("💬 Chat dengan AI Aktuaria")

# Handle selected example
if 'selected_example' in st.session_state:
    st.session_state.current_question = st.session_state.selected_example
    del st.session_state.selected_example

# Form input
with st.form("question_form", clear_on_submit=True):
    default_question = st.session_state.get('current_question', '')
    if 'current_question' in st.session_state:
        del st.session_state.current_question
    
    question = st.text_area(
        "Masukkan pertanyaan Anda:",
        value=default_question,
        placeholder="Contoh: Bagaimana cara menghitung dana pensiun untuk 100 karyawan?",
        height=100,
        help="Ketik pertanyaan tentang perhitungan aktuaria, dana pensiun, atau topik terkait"
    )
    
    col_submit, col_example = st.columns([1, 2])
    
    with col_submit:
        submit_button = st.form_submit_button("🚀 Kirim", use_container_width=True)
    
    with col_example:
        if st.form_submit_button("💡 Contoh Pertanyaan", use_container_width=True):
            st.session_state.example_clicked = True

# Contoh pertanyaan
if st.session_state.get('example_clicked', False):
    st.subheader("💡 Contoh Pertanyaan")
    for i, example in enumerate(examples):
        if st.button(f"📌 {example}", key=f"main_example_{i}"):
            question = example
            submit_button = True
            break
    st.session_state.example_clicked = False

# Process submission
if submit_button and question.strip():
    # Add user message
    st.session_state.chat_history.append({
        "type": "user",
        "content": question,
        "timestamp": datetime.now().strftime("%H:%M:%S")
    })
    
    # Set thinking state
    st.session_state.is_thinking = True
    st.rerun()

# Handle API call
if 'is_thinking' in st.session_state and st.session_state.is_thinking:
    # Get last user question
    last_question = None
    for chat in reversed(st.session_state.chat_history):
        if chat["type"] == "user":
            last_question = chat["content"]
            break
    
    if last_question:
        # Call API
        with st.spinner('🤔 AI sedang berpikir...'):
            result, error = call_api(last_question, session_id, api_url)
        
        # Remove thinking state
        st.session_state.is_thinking = False
        
        if error:
            st.session_state.chat_history.append({
                "type": "error",
                "content": error,
                "timestamp": datetime.now().strftime("%H:%M:%S")
            })
        else:
            if result and result.get('success'):
                answer = result.get('data', {}).get('answer', 'Tidak ada jawaban tersedia.')
                confidence = result.get('data', {}).get('confidence', 0)
                sources = result.get('data', {}).get('sources', [])
                
                st.session_state.chat_history.append({
                    "type": "assistant",
                    "content": answer,
                    "confidence": confidence,
                    "sources": sources,
                    "timestamp": datetime.now().strftime("%H:%M:%S")
                })
            else:
                error_msg = result.get('message', 'Response tidak valid dari API') if result else 'Response kosong dari API'
                st.session_state.chat_history.append({
                    "type": "error",
                    "content": f"❌ {error_msg}",
                    "timestamp": datetime.now().strftime("%H:%M:%S")
                })
        
        st.rerun()

# Footer
st.divider()
st.markdown(f"""
<div style='text-align: center; background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 1.5rem; border-radius: 15px; font-weight: 500; margin-top: 2rem;'>
    💼 <strong>Aplikasi Konsultan Dana Pensiun Aktuaria</strong><br>
    Dikembangkan dengan ❤️ menggunakan Streamlit | Session ID: {session_id}
</div>
""", unsafe_allow_html=True)

# Auto-scroll and MathJax render
if st.session_state.chat_history:
    st.markdown("""
    <script>
        setTimeout(function() {
            window.scrollTo(0, document.body.scrollHeight);
            if (window.MathJax) {
                MathJax.typesetPromise();
            }
        }, 100);
    </script>
    """, unsafe_allow_html=True)