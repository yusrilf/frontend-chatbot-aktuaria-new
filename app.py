import streamlit as st
import requests
import json
from datetime import datetime
import uuid

# Konfigurasi halaman
st.set_page_config(
    page_title="Konsultan Dana Pensiun",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS untuk styling dengan kontras tinggi
st.markdown("""
<style>
    .main-title {
        text-align: center;
        color: #ffffff;
        font-size: 2.5rem;
        margin-bottom: 2rem;
        background-color: #1a5490;
        padding: 1rem;
        border-radius: 10px;
        font-weight: bold;
    }
    
    .chat-container {
        background-color: #f0f0f0;
        color: #000000;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border: 2px solid #333333;
    }
    
    .user-message {
        background-color: #2196f3;
        color: #ffffff;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #ffffff;
        margin: 0.5rem 0;
        font-weight: 500;
    }
    
    .assistant-message {
        background-color: #4caf50;
        color: #ffffff;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #ffffff;
        margin: 0.5rem 0;
        font-weight: 500;
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
    
    .error-message {
        background-color: #dc3545;
        color: #ffffff;
        padding: 1rem;
        border-radius: 8px;
        border: 2px solid #ffffff;
        margin: 1rem 0;
        font-weight: 600;
    }
    
    .success-message {
        background-color: #28a745;
        color: #ffffff;
        padding: 1rem;
        border-radius: 8px;
        border: 2px solid #ffffff;
        margin: 1rem 0;
        font-weight: 600;
    }
    
    /* Styling untuk sidebar */
    .css-1d391kg {
        background-color: #f8f9fa;
    }
    
    /* Styling untuk metrics */
    .metric-container {
        background-color: #343a40;
        color: #ffffff;
        padding: 0.5rem;
        border-radius: 8px;
        margin: 0.25rem 0;
        text-align: center;
        font-weight: bold;
    }
    
    /* Styling untuk expander */
    .streamlit-expanderHeader {
        background-color: #6c757d !important;
        color: #ffffff !important;
        font-weight: bold;
    }
    
    /* High contrast button styling */
    .stButton > button {
        background-color: #212529;
        color: #ffffff;
        border: 2px solid #ffffff;
        font-weight: bold;
    }
    
    .stButton > button:hover {
        background-color: #ffffff;
        color: #212529;
        border: 2px solid #212529;
    }
</style>
""", unsafe_allow_html=True)

# Judul aplikasi
st.markdown('<h1 class="main-title">💰 Konsultan Dana Pensiun Aktuaria</h1>', unsafe_allow_html=True)

# Sidebar untuk konfigurasi
with st.sidebar:
    st.header("⚙️ Konfigurasi")
    
    # URL API
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
    
    # Tombol reset session
    if st.button("🔄 Reset Session"):
        st.session_state.session_id = str(uuid.uuid4())[:8]
        if 'chat_history' in st.session_state:
            st.session_state.chat_history = []
        st.rerun()
    
    st.divider()
    
    # Informasi API dengan kontras tinggi
    st.subheader("📋 Info API")
    st.markdown("""
    <div style="background-color: #17a2b8; color: #ffffff; padding: 1rem; border-radius: 8px; font-weight: 500; border: 2px solid #ffffff;">
        <strong>Method:</strong> POST<br><br>
        <strong>Format Request:</strong><br>
        <code style="background-color: #000000; color: #00ff00; padding: 0.5rem; border-radius: 4px; display: block; margin-top: 0.5rem;">
{<br>
&nbsp;&nbsp;"question": "pertanyaan",<br>
&nbsp;&nbsp;"session_id": "user123"<br>
}
        </code>
    </div>
    """, unsafe_allow_html=True)

# Inisialisasi chat history
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Area chat utama
col1, col2 = st.columns([3, 1])

with col1:
    st.subheader("💬 Chat dengan AI Aktuaria")
    
    # Form input pertanyaan
    with st.form("question_form", clear_on_submit=True):
        question = st.text_area(
            "Masukkan pertanyaan Anda:",
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
    examples = [
        "Bagaimana cara menghitung dana pensiun untuk 100 karyawan?",
        "Apa itu iuran normal dalam perhitungan pensiun?",
        "Bagaimana formula menghitung premi asuransi jiwa?",
        "Jelaskan tentang liability aktuaria",
        "Bagaimana cara menghitung nilai sekarang anuitas?"
    ]
    
    for i, example in enumerate(examples):
        if st.button(f"📌 {example}", key=f"example_{i}"):
            question = example
            submit_button = True
            break
    
    st.session_state.example_clicked = False

# Fungsi untuk memanggil API
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
        return None, "❌ Tidak dapat terhubung ke API. Pastikan server berjalan di URL yang benar."
    except requests.exceptions.Timeout:
        return None, "⏱️ Request timeout. Server mungkin sedang sibuk."
    except requests.exceptions.RequestException as e:
        return None, f"❌ Error dalam request: {str(e)}"
    except Exception as e:
        return None, f"❌ Error tidak terduga: {str(e)}"

# Proses submit pertanyaan
if submit_button and question.strip():
    # Tambahkan pertanyaan user ke history
    st.session_state.chat_history.append({
        "type": "user",
        "content": question,
        "timestamp": datetime.now().strftime("%H:%M:%S")
    })
    
    # Loading indicator
    with st.spinner('🤔 AI sedang berpikir...'):
        # Panggil API
        result, error = call_api(question, session_id, api_url)
    
    if error:
        st.session_state.chat_history.append({
            "type": "error",
            "content": error,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        })
    else:
        # Tambahkan response ke history
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

# Tampilkan chat history
if st.session_state.chat_history:
    st.subheader("📜 Riwayat Percakapan")
    
    for i, chat in enumerate(reversed(st.session_state.chat_history)):
        if chat["type"] == "user":
            st.markdown(f"""
            <div class="user-message">
                <strong>🧑 Anda ({chat['timestamp']}):</strong><br>
                {chat['content']}
            </div>
            """, unsafe_allow_html=True)
            
        elif chat["type"] == "assistant":
            st.markdown(f"""
            <div class="assistant-message">
                <strong>🤖 AI Aktuaria ({chat['timestamp']}):</strong><br>
                {chat['content']}
            </div>
            """, unsafe_allow_html=True)
            
            # Tampilkan confidence dan sources jika ada dengan kontras tinggi
            if 'confidence' in chat:
                confidence_pct = int(chat['confidence'] * 100)
                st.markdown(f"""
                <div style="background-color: #28a745; color: #ffffff; padding: 1rem; border-radius: 8px; border: 2px solid #ffffff; margin: 1rem 0; font-weight: bold;">
                    📊 <strong>Tingkat Keyakinan:</strong> {confidence_pct}%
                </div>
                """, unsafe_allow_html=True)
            
            if 'sources' in chat and chat['sources']:
                with st.expander(f"📚 **Sumber Referensi ({len(chat['sources'])} dokumen)**", expanded=False):
                    for j, source in enumerate(chat['sources'], 1):
                        st.markdown(f"""
                        <div style="background-color: #6c757d; color: #ffffff; padding: 1rem; border-radius: 8px; margin: 0.5rem 0; border: 2px solid #ffffff;">
                            <strong style="color: #ffc107;">Sumber {j}:</strong><br>
                            <strong>📁 File:</strong> <span style="color: #ffffff;">{source.get('filename', 'N/A')}</span><br>
                            <strong>📑 Header:</strong> <span style="color: #ffffff;">{' > '.join(source.get('headers', {}).values())}</span><br>
                            <strong>👁️ Preview:</strong> <span style="color: #ffffff;">{source.get('preview', 'N/A')[:200]}...</span>
                        </div>
                        """, unsafe_allow_html=True)
                        
        elif chat["type"] == "error":
            st.markdown(f"""
            <div class="error-message">
                <strong>⚠️ Error ({chat['timestamp']}):</strong><br>
                {chat['content']}
            </div>
            """, unsafe_allow_html=True)

# Sidebar informasi tambahan
with col2:
    st.subheader("ℹ️ Informasi")
    
    # Status koneksi dengan kontras tinggi
    st.markdown("**🔗 Status Koneksi:**")
    try:
        test_response = requests.get(api_url.replace('/ask', '/'), timeout=5)
        st.markdown("""
        <div style="background-color: #28a745; color: #ffffff; padding: 1rem; border-radius: 8px; text-align: center; font-weight: bold; border: 2px solid #ffffff;">
            ✅ SERVER TERHUBUNG
        </div>
        """, unsafe_allow_html=True)
    except:
        st.markdown("""
        <div style="background-color: #dc3545; color: #ffffff; padding: 1rem; border-radius: 8px; text-align: center; font-weight: bold; border: 2px solid #ffffff;">
            ❌ SERVER TIDAK TERHUBUNG
        </div>
        """, unsafe_allow_html=True)
    
    # Statistik chat dengan styling kontras
    if st.session_state.chat_history:
        user_messages = len([chat for chat in st.session_state.chat_history if chat["type"] == "user"])
        ai_messages = len([chat for chat in st.session_state.chat_history if chat["type"] == "assistant"])
        errors = len([chat for chat in st.session_state.chat_history if chat["type"] == "error"])
        
        st.markdown("**📈 Statistik Chat:**")
        
        # Custom metrics dengan kontras tinggi
        st.markdown(f"""
        <div class="metric-container">
            <div style="font-size: 1.2rem;">📝 Pertanyaan</div>
            <div style="font-size: 2rem; font-weight: bold;">{user_messages}</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="metric-container">
            <div style="font-size: 1.2rem;">🤖 Jawaban AI</div>
            <div style="font-size: 2rem; font-weight: bold;">{ai_messages}</div>
        </div>
        """, unsafe_allow_html=True)
        
        if errors > 0:
            st.markdown(f"""
            <div style="background-color: #dc3545; color: #ffffff; padding: 0.5rem; border-radius: 8px; margin: 0.25rem 0; text-align: center; font-weight: bold;">
                <div style="font-size: 1.2rem;">⚠️ Error</div>
                <div style="font-size: 2rem; font-weight: bold;">{errors}</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Tombol clear chat
    if st.button("🗑️ Hapus Riwayat Chat", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()

# Footer dengan kontras tinggi
st.divider()
st.markdown(f"""
<div style='text-align: center; background-color: #343a40; color: #ffffff; padding: 1rem; border-radius: 10px; font-weight: bold; border: 2px solid #ffffff; margin-top: 2rem;'>
    💼 <span style="color: #ffc107;">Aplikasi Konsultan Dana Pensiun Aktuaria</span><br>
    Dikembangkan dengan <span style="color: #ff6b6b;">❤️</span> menggunakan Streamlit<br>
    <span style="color: #28a745;">Session ID:</span> {session_id}
</div>
""", unsafe_allow_html=True)