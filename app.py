import streamlit as st
import os
import fitz
import google.generativeai as genai
from PIL import Image
import chromadb
from datetime import datetime

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Smart Research Assistant",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS WITH FULL RESPONSIVE DESIGN ---
st.markdown("""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Main container styling */
    .main {
        padding: 1rem;
    }
    
    @media (min-width: 768px) {
        .main {
            padding: 2rem;
        }
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Header styling with glassmorphism effect */
    .header-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 20px;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .header-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(45deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0) 100%);
        pointer-events: none;
    }
    
    @media (min-width: 768px) {
        .header-container {
            padding: 2.5rem;
            border-radius: 25px;
        }
    }
    
    .header-title {
        color: white;
        font-size: 1.8rem;
        font-weight: 700;
        margin: 0;
        text-align: center;
        position: relative;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    
    @media (min-width: 768px) {
        .header-title {
            font-size: 2.8rem;
        }
    }
    
    .header-subtitle {
        color: rgba(255, 255, 255, 0.95);
        font-size: 0.9rem;
        text-align: center;
        margin-top: 0.5rem;
        position: relative;
    }
    
    @media (min-width: 768px) {
        .header-subtitle {
            font-size: 1.2rem;
            margin-top: 0.8rem;
        }
    }
    
    /* Animated background pattern */
    .header-container::after {
        content: '';
        position: absolute;
        width: 200%;
        height: 200%;
        top: -50%;
        left: -50%;
        background: repeating-linear-gradient(
            45deg,
            transparent,
            transparent 10px,
            rgba(255,255,255,0.03) 10px,
            rgba(255,255,255,0.03) 20px
        );
        animation: slide 20s linear infinite;
        pointer-events: none;
    }
    
    @keyframes slide {
        0% { transform: translate(0, 0); }
        100% { transform: translate(50px, 50px); }
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 1rem;
    }
    
    [data-testid="stSidebar"] > div {
        padding-top: 2rem;
    }
    
    /* Status cards with modern design */
    .status-card {
        background: white;
        padding: 1.2rem;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
        margin-bottom: 1rem;
        transition: all 0.3s ease;
        border: 1px solid rgba(0,0,0,0.05);
    }
    
    @media (min-width: 768px) {
        .status-card {
            padding: 1.5rem;
        }
    }
    
    .status-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.12);
    }
    
    .status-card-success {
        border-left: 5px solid #28a745;
        background: linear-gradient(135deg, #ffffff 0%, #f0fff4 100%);
    }
    
    .status-card-info {
        border-left: 5px solid #17a2b8;
        background: linear-gradient(135deg, #ffffff 0%, #e7f6f8 100%);
    }
    
    .status-card-warning {
        border-left: 5px solid #ffc107;
        background: linear-gradient(135deg, #ffffff 0%, #fff9e6 100%);
    }
    
    /* Chat messages with better mobile support */
    .stChatMessage {
        background: white;
        border-radius: 15px;
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
        word-wrap: break-word;
    }
    
    @media (min-width: 768px) {
        .stChatMessage {
            padding: 1.5rem;
        }
    }
    
    /* Metrics styling */
    [data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    @media (min-width: 768px) {
        [data-testid="stMetricValue"] {
            font-size: 2.5rem;
        }
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 0.85rem;
        color: #666;
        font-weight: 500;
    }
    
    /* Button styling with improved touch targets */
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        font-weight: 600;
        padding: 0.8rem 1.2rem;
        transition: all 0.3s ease;
        border: none;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-size: 0.95rem;
        min-height: 48px; /* Better touch target for mobile */
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    
    .stButton>button:active {
        transform: translateY(0);
    }
    
    /* File uploader with better mobile UX */
    [data-testid="stFileUploader"] {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        border: 3px dashed #667eea;
        transition: all 0.3s ease;
    }
    
    @media (min-width: 768px) {
        [data-testid="stFileUploader"] {
            padding: 2.5rem;
        }
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: #764ba2;
        background: #f8f9ff;
    }
    
    /* Progress bar */
    .stProgress > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }
    
    /* Info boxes */
    .info-box {
        background: linear-gradient(135deg, #e7f3ff 0%, #f0f7ff 100%);
        border-left: 5px solid #2196F3;
        padding: 1.2rem;
        border-radius: 12px;
        margin: 1rem 0;
        box-shadow: 0 2px 10px rgba(33, 150, 243, 0.1);
    }
    
    @media (min-width: 768px) {
        .info-box {
            padding: 1.5rem;
        }
    }
    
    /* Feature cards with responsive grid */
    .feature-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        height: 100%;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        border: 1px solid rgba(0,0,0,0.05);
        text-align: center;
    }
    
    @media (min-width: 768px) {
        .feature-card {
            padding: 2rem;
        }
    }
    
    .feature-card:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 8px 30px rgba(102, 126, 234, 0.2);
        border-color: #667eea;
    }
    
    .feature-icon {
        font-size: 2.5rem;
        margin-bottom: 1rem;
        filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1));
    }
    
    @media (min-width: 768px) {
        .feature-icon {
            font-size: 3.5rem;
        }
    }
    
    .feature-title {
        font-size: 1.1rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        color: #333;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    @media (min-width: 768px) {
        .feature-title {
            font-size: 1.3rem;
        }
    }
    
    .feature-desc {
        color: #666;
        font-size: 0.85rem;
        line-height: 1.6;
    }
    
    @media (min-width: 768px) {
        .feature-desc {
            font-size: 0.95rem;
        }
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #f8f9ff 0%, #ffffff 100%);
        border-radius: 10px;
        font-weight: 600;
        border: 1px solid rgba(102, 126, 234, 0.2);
    }
    
    .streamlit-expanderHeader:hover {
        background: linear-gradient(135deg, #eef0ff 0%, #f8f9ff 100%);
        border-color: #667eea;
    }
    
    /* Input fields with better mobile UX */
    .stTextInput>div>div>input {
        border-radius: 10px;
        border: 2px solid #e0e0e0;
        padding: 0.8rem;
        font-size: 1rem;
        transition: all 0.3s ease;
        min-height: 48px; /* Better touch target */
    }
    
    .stTextInput>div>div>input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Chat input with improved mobile styling */
    .stChatInputContainer {
        border-top: 2px solid #e0e0e0;
        padding: 1rem;
        background: white;
        position: sticky;
        bottom: 0;
        z-index: 100;
    }
    
    @media (min-width: 768px) {
        .stChatInputContainer {
            padding: 1.5rem;
        }
    }
    
    /* Divider styling */
    hr {
        margin: 2rem 0;
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent 0%, #667eea 50%, transparent 100%);
    }
    
    /* Success/Error/Warning messages */
    .stSuccess, .stError, .stWarning, .stInfo {
        border-radius: 12px;
        padding: 1rem;
        font-weight: 500;
    }
    
    @media (min-width: 768px) {
        .stSuccess, .stError, .stWarning, .stInfo {
            padding: 1.2rem;
        }
    }
    
    /* Spinner customization */
    .stSpinner > div {
        border-top-color: #667eea !important;
    }
    
    /* Image containers - responsive */
    .stImage {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    }
    
    /* Badge styling */
    .badge {
        display: inline-block;
        padding: 0.4rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        margin: 0.2rem;
    }
    
    @media (min-width: 768px) {
        .badge {
            padding: 0.5rem 1rem;
            font-size: 0.85rem;
        }
    }
    
    .badge-success {
        background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
        color: white;
    }
    
    .badge-info {
        background: linear-gradient(135deg, #17a2b8 0%, #138496 100%);
        color: white;
    }
    
    .badge-primary {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    /* Animated gradient background for sections */
    .gradient-section {
        background: linear-gradient(-45deg, #667eea, #764ba2, #f093fb, #4facfe);
        background-size: 400% 400%;
        animation: gradientShift 15s ease infinite;
        padding: 2rem;
        border-radius: 20px;
        color: white;
        margin: 1rem 0;
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Example button styling */
    .example-btn {
        background: white;
        border: 2px solid #667eea;
        color: #667eea;
        padding: 0.8rem 1.5rem;
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.3s ease;
        cursor: pointer;
        text-align: center;
        margin: 0.5rem 0;
        min-height: 48px; /* Touch target */
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .example-btn:hover {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    /* Footer styling */
    .custom-footer {
        text-align: center;
        color: #666;
        padding: 2rem 1rem;
        background: linear-gradient(180deg, transparent 0%, #f8f9fa 100%);
        border-radius: 20px 20px 0 0;
        margin-top: 3rem;
    }
    
    /* Loading animation */
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    .loading-pulse {
        animation: pulse 1.5s ease-in-out infinite;
    }
    
    /* Smooth scroll */
    html {
        scroll-behavior: smooth;
    }
    
    /* Tablet specific adjustments */
    @media (min-width: 768px) and (max-width: 1024px) {
        .header-title {
            font-size: 2.2rem;
        }
        
        .feature-card {
            padding: 1.8rem;
        }
    }
    
    /* Mobile specific adjustments */
    @media (max-width: 767px) {
        .header-container {
            margin-bottom: 1rem;
        }
        
        .stButton>button {
            font-size: 0.9rem;
            padding: 0.7rem 1rem;
        }
        
        [data-testid="stMetricValue"] {
            font-size: 1.5rem;
        }
    }
    </style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.markdown("""
    <div class="header-container">
        <h1 class="header-title">🔬 Smart Research Assistant</h1>
        <p class="header-subtitle">AI-Powered Analysis • Text, Tables & Charts • Powered by Gemini</p>
    </div>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### ⚙️ Configuration")
    
    # API Key Input
    api_key = st.text_input(
        "Google AI Studio API Key",
        type="password",
        help="Enter your API key from Google AI Studio",
        placeholder="Enter API key..."
    )
    
    if api_key:
        genai.configure(api_key=api_key)
        indexing_model = genai.GenerativeModel('gemini-2.5-flash')
        reasoning_model = genai.GenerativeModel('gemini-2.5-flash')
        st.markdown('<span class="badge badge-success">✅ Connected</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="badge badge-info">⚠️ Not Connected</span>', unsafe_allow_html=True)
    
    st.divider()
    
    # Model Information
    st.markdown("### 🤖 Active Models")
    if api_key:
        st.markdown("""
            <div class="status-card status-card-info">
                <strong>⚡ Indexing:</strong><br>Gemini 2.5 Flash
            </div>
            <div class="status-card status-card-info">
                <strong>🧠 Reasoning:</strong><br>Gemini 2.5 Flash
            </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("⚠️ Configure API key to activate")
    
    st.divider()
    
    # Session Info with better layout
    st.markdown("### 📊 Session Stats")
    if 'vector_db' in st.session_state:
        col1, col2 = st.columns(2)
        with col1:
            st.metric("📄 Pages", st.session_state.vector_db.count())
        with col2:
            st.metric("💬 Queries", st.session_state.get('query_count', 0))
        
        if st.session_state.get('last_file'):
            st.info(f"📁 **File:** {st.session_state.last_file[:20]}...")
    else:
        st.markdown("""
            <div class="status-card status-card-warning">
                <strong>📭 No document loaded</strong><br>
                <small>Upload a PDF to get started</small>
            </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # Action buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Clear", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    
    with col2:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()
    
    # Help section
    with st.expander("📖 How to Use"):
        st.markdown("""
        **Quick Start:**
        1. 🔑 Enter API Key above
        2. 📤 Upload your PDF document
        3. ⏳ Wait for processing
        4. 💬 Ask questions about your document
        5. 📊 Get AI-powered insights
        """)
    
    with st.expander("💡 Tips & Tricks"):
        st.markdown("""
        **Best Practices:**
        - Be specific in questions
        - Ask about charts & tables
        - Request data comparisons
        - Reference page numbers
        - Use example queries
        """)
    
    with st.expander("🎯 Example Queries"):
        st.markdown("""
        - *"What are the Q3 revenue figures?"*
        - *"Summarize the executive summary"*
        - *"Extract data from the financial table"*
        - *"What trends are shown in the chart?"*
        - *"Compare year-over-year growth"*
        """)

# --- MAIN CONTENT ---
if not api_key:
    # Welcome screen with animated gradient
    st.markdown("""
        <div class="gradient-section">
            <h2 style="margin:0; font-size: 1.8rem;">👋 Welcome to Smart Research Assistant!</h2>
            <p style="margin-top: 1rem; font-size: 1.1rem; opacity: 0.95;">
                Get started by entering your Google AI Studio API key in the sidebar.
            </p>
            <p style="margin-top: 0.5rem;">
                <a href="https://makersuite.google.com/app/apikey" target="_blank" 
                   style="color: white; text-decoration: underline; font-weight: 600;">
                    🔗 Get your free API key here
                </a>
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Feature showcase with responsive grid
    st.markdown("### ✨ Powerful Features")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        st.markdown("""
            <div class="feature-card">
                <div class="feature-icon">📊</div>
                <div class="feature-title">Chart Analysis</div>
                <div class="feature-desc">Extract insights from complex graphs and visualizations with AI precision</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class="feature-card">
                <div class="feature-icon">📋</div>
                <div class="feature-title">Table Extraction</div>
                <div class="feature-desc">Parse and analyze tabular data accurately from any document format</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
            <div class="feature-card">
                <div class="feature-icon">🔍</div>
                <div class="feature-title">Smart Search</div>
                <div class="feature-desc">Find relevant information instantly across entire documents</div>
            </div>
        """, unsafe_allow_html=True)
    
    # Additional features
    st.markdown("### 🚀 Why Choose Us?")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("""
            <div class="status-card status-card-success">
                <h4 style="margin:0;">⚡ Lightning Fast</h4>
                <p style="margin-top:0.5rem; color: #666;">Process documents in seconds with advanced AI</p>
            </div>
            <div class="status-card status-card-info">
                <h4 style="margin:0;">🎯 Highly Accurate</h4>
                <p style="margin-top:0.5rem; color: #666;">Powered by Google's Gemini 1.5 Pro model</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class="status-card status-card-success">
                <h4 style="margin:0;">📱 Fully Responsive</h4>
                <p style="margin-top:0.5rem; color: #666;">Works seamlessly on phone, tablet & desktop</p>
            </div>
            <div class="status-card status-card-info">
                <h4 style="margin:0;">🔒 Secure & Private</h4>
                <p style="margin-top:0.5rem; color: #666;">Your documents are processed securely</p>
            </div>
        """, unsafe_allow_html=True)

else:
    # --- HELPER FUNCTIONS ---
    def get_pdf_images(uploaded_file):
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        image_paths = []
        if not os.path.exists("temp_images"):
            os.makedirs("temp_images")
        
        for i in range(len(doc)):
            page = doc.load_page(i)
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
            path = f"temp_images/page_{i}.png"
            pix.save(path)
            image_paths.append(path)
        return image_paths
    
    # File upload section with enhanced UI
    st.markdown("### 📤 Upload Your Document")
    
    # Create two columns for upload area
    col1, col2 = st.columns([3, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "Drag and drop or click to browse",
            type="pdf",
            help="Upload PDFs like financial reports, research papers, or technical documents",
            label_visibility="collapsed"
        )
    
    with col2:
        if uploaded_file:
            st.markdown(f"""
                <div class="status-card status-card-success">
                    <strong>📄 {uploaded_file.name[:15]}...</strong><br>
                    <small>📊 {uploaded_file.size / 1024:.1f} KB</small>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
                <div class="status-card status-card-warning">
                    <strong>📭 No file</strong><br>
                    <small>Upload PDF</small>
                </div>
            """, unsafe_allow_html=True)
    
    # Document processing with enhanced progress UI
    if uploaded_file and api_key:
        if 'vector_db' not in st.session_state or st.session_state.get('last_file') != uploaded_file.name:
            
            # Processing animation
            st.markdown("""
                <div class="status-card status-card-info loading-pulse">
                    <h3 style="margin:0;">🔄 Processing Your Document</h3>
                    <p style="margin-top:0.5rem; color:#666;">This may take a moment depending on document size...</p>
                </div>
            """, unsafe_allow_html=True)
            
            with st.status("🚀 Processing Pipeline Active", expanded=True) as status:
                # Step 1
                st.write("📄 **Step 1/3:** Converting PDF pages to high-quality images...")
                progress_bar = st.progress(0)
                img_paths = get_pdf_images(uploaded_file)
                progress_bar.progress(33)
                st.success(f"✅ Converted {len(img_paths)} pages successfully!")
                
                # Step 2
                st.write("🤖 **Step 2/3:** AI is analyzing each page and generating summaries...")
                summaries = []
                for idx, path in enumerate(img_paths):
                    try:
                        img = Image.open(path)
                        res = indexing_model.generate_content([
                            "Summarize this page accurately for search.",
                            img
                        ])
                        summaries.append(res.text)
                        progress_bar.progress(33 + int((idx + 1) / len(img_paths) * 34))
                    except Exception as e:
                        st.error(f"Error processing page {idx + 1}: {str(e)}")
                        summaries.append(f"Page {idx + 1} - Processing error")
                st.success(f"✅ Generated {len(summaries)} AI summaries!")
                
                # Step 3
                st.write("💾 **Step 3/3:** Building searchable vector database...")
                client = chromadb.Client()
                collection = client.create_collection(
                    name=f"col_{uploaded_file.name[:5]}_{int(datetime.now().timestamp())}"
                )
                for i, s in enumerate(summaries):
                    collection.add(
                        documents=[s],
                        metadatas=[{"path": img_paths[i], "page": i+1}],
                        ids=[str(i)]
                    )
                progress_bar.progress(100)
                st.success("✅ Vector database created and optimized!")
                
                st.session_state.vector_db = collection
                st.session_state.last_file = uploaded_file.name
                st.session_state.query_count = 0
                st.session_state.img_paths = img_paths
                
                status.update(label="✅ Processing Complete!", state="complete", expanded=False)
            
            # Success message with confetti effect
            st.balloons()
            st.markdown(f"""
                <div class="status-card status-card-success">
                    <h3 style="margin:0;">🎉 Document Ready for Analysis!</h3>
                    <p style="margin-top:0.5rem; color:#666;">
                        Successfully indexed <strong>{len(img_paths)} pages</strong> from <strong>{uploaded_file.name}</strong>
                    </p>
                    <p style="margin-top:0.5rem; font-size:0.9rem; color:#28a745;">
                        💬 You can now ask questions below!
                    </p>
                </div>
            """, unsafe_allow_html=True)
        
        st.divider()
        
        # --- CHAT INTERFACE ---
        st.markdown("### 💬 Ask Questions About Your Document")
        
        # Initialize chat history
        if "messages" not in st.session_state:
            st.session_state.messages = []
        
        # Display chat history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])
                if "image" in message and "page" in message:
                    with st.expander(f"📄 View Source - Page {message['page']}", expanded=False):
                        st.image(message["image"], use_container_width=True)
        
        # Chat input
        query = st.chat_input("💭 Ask about charts, tables, or specific data in the document...")
        
        if query:
            # Update query count
            st.session_state.query_count = st.session_state.get('query_count', 0) + 1
            
            # Display user message
            with st.chat_message("user"):
                st.write(query)
            
            st.session_state.messages.append({"role": "user", "content": query})
            
            # Display assistant response
            with st.chat_message("assistant"):
                with st.spinner("🔍 Searching document and analyzing..."):
                    try:
                        # Retrieval
                        results = st.session_state.vector_db.query(query_texts=[query], n_results=1)
                        best_page_path = results['metadatas'][0][0]['path']
                        page_num = results['metadatas'][0][0]['page']
                        
                        # Generation
                        img_to_analyze = Image.open(best_page_path)
                        prompt = f"Using the provided document image, answer this question in detail: {query}\n\nProvide specific information, numbers, and insights from the image."
                        response = reasoning_model.generate_content([prompt, img_to_analyze])
                        
                        # Display result
                        st.write(response.text)
                        
                        # Reference section
                        with st.expander(f"📄 View Source - Page {page_num}", expanded=False):
                            st.image(img_to_analyze, use_container_width=True)
                            st.caption(f"📍 Reference: Page {page_num} of {uploaded_file.name}")
                        
                        # Save to history
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": response.text,
                            "image": img_to_analyze,
                            "page": page_num
                        })
                    
                    except Exception as e:
                        st.error(f"❌ Error processing query: {str(e)}")
                        st.info("💡 Try rephrasing your question or check your API key.")
        
        # Example queries section
        if len(st.session_state.messages) == 0:
            st.markdown("### 💡 Example Questions to Get Started")
            
            st.markdown("""
                <p style="color: #666; margin-bottom: 1rem;">
                    Click any example below or type your own question:
                </p>
            """, unsafe_allow_html=True)
            
            # Create responsive grid for example buttons
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("📊 What are the key metrics?", use_container_width=True):
                    st.session_state.example_query = "What are the key financial metrics or important numbers shown in this document?"
                    st.rerun()
                
                if st.button("📈 Analyze trends", use_container_width=True):
                    st.session_state.example_query = "What trends or patterns can you identify from the charts and data?"
                    st.rerun()
                
                if st.button("📋 Extract table data", use_container_width=True):
                    st.session_state.example_query = "Can you extract and summarize the data from any tables in the document?"
                    st.rerun()
            
            with col2:
                if st.button("📝 Summarize findings", use_container_width=True):
                    st.session_state.example_query = "What are the main findings or conclusions in this document?"
                    st.rerun()
                
                if st.button("🔍 Key insights", use_container_width=True):
                    st.session_state.example_query = "What are the most important insights I should know from this document?"
                    st.rerun()
                
                if st.button("💰 Financial data", use_container_width=True):
                    st.session_state.example_query = "What financial data or monetary figures are mentioned?"
                    st.rerun()
        
        # Handle example query
        if 'example_query' in st.session_state:
            query = st.session_state.example_query
            del st.session_state.example_query
            st.rerun()

# --- FOOTER ---
st.divider()
st.markdown("""
    <div class="custom-footer">
        <p style="font-size: 1rem; font-weight: 600; margin-bottom: 0.5rem;">
            🚀 Powered by Google Gemini 2.5 Flash
        </p>
        <p style="font-size: 0.9rem; color: #888; margin-bottom: 0.5rem;">
            Built with Streamlit • ChromaDB Vector Store • PyMuPDF
        </p>
        <p style="font-size: 0.8rem; color: #aaa;">
            Made with ❤️ for researchers and analysts
        </p>
    </div>

""", unsafe_allow_html=True)
