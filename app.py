import streamlit as st
import os
import fitz
import google.generativeai as genai
from PIL import Image
import chromadb
from datetime import datetime
import json
import re
import plotly.graph_objects as go
import plotly.express as px

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
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    * { font-family: 'Inter', sans-serif; }
    .main { padding: 1rem; }
    @media (min-width: 768px) { .main { padding: 2rem; } }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
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
        top: 0; left: 0; right: 0; bottom: 0;
        background: linear-gradient(45deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0) 100%);
        pointer-events: none;
    }
    @media (min-width: 768px) { .header-container { padding: 2.5rem; border-radius: 25px; } }
    
    .header-title {
        color: white;
        font-size: 1.8rem;
        font-weight: 700;
        margin: 0;
        text-align: center;
        position: relative;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    @media (min-width: 768px) { .header-title { font-size: 2.8rem; } }
    
    .header-subtitle {
        color: rgba(255, 255, 255, 0.95);
        font-size: 0.9rem;
        text-align: center;
        margin-top: 0.5rem;
        position: relative;
    }
    @media (min-width: 768px) { .header-subtitle { font-size: 1.2rem; margin-top: 0.8rem; } }
    
    .header-container::after {
        content: '';
        position: absolute;
        width: 200%; height: 200%;
        top: -50%; left: -50%;
        background: repeating-linear-gradient(
            45deg, transparent, transparent 10px,
            rgba(255,255,255,0.03) 10px, rgba(255,255,255,0.03) 20px
        );
        animation: slide 20s linear infinite;
        pointer-events: none;
    }
    @keyframes slide { 0% { transform: translate(0, 0); } 100% { transform: translate(50px, 50px); } }
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 1rem;
    }
    [data-testid="stSidebar"] > div { padding-top: 2rem; }
    
    .status-card {
        background: white;
        padding: 1.2rem;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
        margin-bottom: 1rem;
        transition: all 0.3s ease;
        border: 1px solid rgba(0,0,0,0.05);
    }
    @media (min-width: 768px) { .status-card { padding: 1.5rem; } }
    .status-card:hover { transform: translateY(-3px); box-shadow: 0 6px 20px rgba(0, 0, 0, 0.12); }
    .status-card-success { border-left: 5px solid #28a745; background: linear-gradient(135deg, #ffffff 0%, #f0fff4 100%); }
    .status-card-info { border-left: 5px solid #17a2b8; background: linear-gradient(135deg, #ffffff 0%, #e7f6f8 100%); }
    .status-card-warning { border-left: 5px solid #ffc107; background: linear-gradient(135deg, #ffffff 0%, #fff9e6 100%); }
    
    .stChatMessage {
        background: white;
        border-radius: 15px;
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
        word-wrap: break-word;
    }
    @media (min-width: 768px) { .stChatMessage { padding: 1.5rem; } }
    
    [data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    @media (min-width: 768px) { [data-testid="stMetricValue"] { font-size: 2.5rem; } }
    [data-testid="stMetricLabel"] { font-size: 0.85rem; color: #666; font-weight: 500; }
    
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
        min-height: 48px;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4); }
    .stButton>button:active { transform: translateY(0); }
    
    [data-testid="stFileUploader"] {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        border: 3px dashed #667eea;
        transition: all 0.3s ease;
    }
    @media (min-width: 768px) { [data-testid="stFileUploader"] { padding: 2.5rem; } }
    [data-testid="stFileUploader"]:hover { border-color: #764ba2; background: #f8f9ff; }
    
    .stProgress > div > div { background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); border-radius: 10px; }
    
    .info-box {
        background: linear-gradient(135deg, #e7f3ff 0%, #f0f7ff 100%);
        border-left: 5px solid #2196F3;
        padding: 1.2rem;
        border-radius: 12px;
        margin: 1rem 0;
        box-shadow: 0 2px 10px rgba(33, 150, 243, 0.1);
    }
    @media (min-width: 768px) { .info-box { padding: 1.5rem; } }

    .chart-badge {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 700;
        display: inline-block;
        margin-bottom: 0.5rem;
        letter-spacing: 0.5px;
    }
    
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
    @media (min-width: 768px) { .feature-card { padding: 2rem; } }
    .feature-card:hover { transform: translateY(-8px) scale(1.02); box-shadow: 0 8px 30px rgba(102, 126, 234, 0.2); border-color: #667eea; }
    .feature-icon { font-size: 2.5rem; margin-bottom: 1rem; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1)); }
    @media (min-width: 768px) { .feature-icon { font-size: 3.5rem; } }
    .feature-title { font-size: 1.1rem; font-weight: 700; margin-bottom: 0.5rem; color: #333; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
    @media (min-width: 768px) { .feature-title { font-size: 1.3rem; } }
    .feature-desc { color: #666; font-size: 0.85rem; line-height: 1.6; }
    @media (min-width: 768px) { .feature-desc { font-size: 0.95rem; } }
    
    .streamlit-expanderHeader { background: linear-gradient(135deg, #f8f9ff 0%, #ffffff 100%); border-radius: 10px; font-weight: 600; border: 1px solid rgba(102, 126, 234, 0.2); }
    .streamlit-expanderHeader:hover { background: linear-gradient(135deg, #eef0ff 0%, #f8f9ff 100%); border-color: #667eea; }
    
    .stTextInput>div>div>input { border-radius: 10px; border: 2px solid #e0e0e0; padding: 0.8rem; font-size: 1rem; transition: all 0.3s ease; min-height: 48px; }
    .stTextInput>div>div>input:focus { border-color: #667eea; box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1); }
    
    .stChatInputContainer { border-top: 2px solid #e0e0e0; padding: 1rem; background: white; position: sticky; bottom: 0; z-index: 100; }
    @media (min-width: 768px) { .stChatInputContainer { padding: 1.5rem; } }
    
    hr { margin: 2rem 0; border: none; height: 2px; background: linear-gradient(90deg, transparent 0%, #667eea 50%, transparent 100%); }
    .stSuccess, .stError, .stWarning, .stInfo { border-radius: 12px; padding: 1rem; font-weight: 500; }
    @media (min-width: 768px) { .stSuccess, .stError, .stWarning, .stInfo { padding: 1.2rem; } }
    .stSpinner > div { border-top-color: #667eea !important; }
    .stImage { border-radius: 12px; overflow: hidden; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1); }
    
    .badge { display: inline-block; padding: 0.4rem 0.8rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600; margin: 0.2rem; }
    @media (min-width: 768px) { .badge { padding: 0.5rem 1rem; font-size: 0.85rem; } }
    .badge-success { background: linear-gradient(135deg, #28a745 0%, #20c997 100%); color: white; }
    .badge-info { background: linear-gradient(135deg, #17a2b8 0%, #138496 100%); color: white; }
    .badge-primary { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
    
    .gradient-section {
        background: linear-gradient(-45deg, #667eea, #764ba2, #f093fb, #4facfe);
        background-size: 400% 400%;
        animation: gradientShift 15s ease infinite;
        padding: 2rem;
        border-radius: 20px;
        color: white;
        margin: 1rem 0;
    }
    @keyframes gradientShift { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
    
    .custom-footer { text-align: center; color: #666; padding: 2rem 1rem; background: linear-gradient(180deg, transparent 0%, #f8f9fa 100%); border-radius: 20px 20px 0 0; margin-top: 3rem; }
    html { scroll-behavior: smooth; }
    @media (max-width: 767px) { .header-container { margin-bottom: 1rem; } .stButton>button { font-size: 0.9rem; padding: 0.7rem 1rem; } [data-testid="stMetricValue"] { font-size: 1.5rem; } }
    </style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.markdown("""
    <div class="header-container">
        <h1 class="header-title">🔬 Smart Research Assistant</h1>
        <p class="header-subtitle">AI-Powered Analysis • Text, Tables, Charts & Graphs • Powered by Gemini</p>
    </div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# GRAPH PLOTTING HELPERS
# ─────────────────────────────────────────────

CHART_KEYWORDS = [
    "plot", "graph", "chart", "visualize", "visualise", "bar chart", "line chart",
    "pie chart", "scatter", "trend", "compare", "comparison", "over time",
    "revenue", "growth", "distribution", "percentage", "breakdown",
    "quarterly", "monthly", "annually", "year", "figures", "numbers", "statistics",
    "data", "metrics", "kpi", "performance", "sales", "profit", "loss",
]

def should_plot_graph(query: str) -> bool:
    """Heuristic: return True if the query seems to ask for quantitative/visual output."""
    q = query.lower()
    return any(kw in q for kw in CHART_KEYWORDS)


def extract_chart_data(query: str, page_text: str, model) -> dict | None:
    """
    Ask Gemini to extract structured chart data from the page context.
    Returns a dict with keys: chart_type, title, labels, datasets
    or None if extraction fails.
    """
    extraction_prompt = f"""
You are a data extraction assistant. Given the document context and user query below,
extract numeric data suitable for plotting a chart.

User query: {query}

Document context (page summary/content):
{page_text}

Return ONLY valid JSON (no markdown, no extra text) in this exact schema:
{{
  "chart_type": "bar" | "line" | "pie" | "scatter",
  "title": "string — a short descriptive chart title",
  "x_label": "string — label for x-axis (or 'Category' for pie)",
  "y_label": "string — label for y-axis (or 'Value' for pie)",
  "labels": ["label1", "label2", ...],
  "datasets": [
    {{
      "name": "series name",
      "values": [num1, num2, ...]
    }}
  ]
}}

Rules:
- labels and values arrays must have the same length.
- datasets can have multiple series for grouped bar/line charts.
- For pie charts, use a single dataset with one series.
- If the document does not contain enough numeric data to plot anything meaningful, return: {{"error": "no_data"}}
- Never include non-numeric values in the values array.
"""
    try:
        response = model.generate_content(extraction_prompt)
        raw = response.text.strip()
        # Strip any accidental markdown fences
        raw = re.sub(r"^```[a-z]*\n?", "", raw)
        raw = re.sub(r"\n?```$", "", raw)
        data = json.loads(raw)
        if "error" in data:
            return None
        return data
    except Exception:
        return None


def render_plotly_chart(chart_data: dict):
    """Render a Plotly chart from extracted chart_data dict."""
    chart_type = chart_data.get("chart_type", "bar").lower()
    title      = chart_data.get("title", "Chart")
    x_label    = chart_data.get("x_label", "")
    y_label    = chart_data.get("y_label", "")
    labels     = chart_data.get("labels", [])
    datasets   = chart_data.get("datasets", [])

    PURPLE_PALETTE = [
        "#667eea", "#764ba2", "#f093fb", "#4facfe",
        "#43e97b", "#fa709a", "#fee140", "#30cfd0",
    ]

    fig = None

    if chart_type == "pie" and datasets:
        values = datasets[0].get("values", [])
        fig = go.Figure(go.Pie(
            labels=labels,
            values=values,
            hole=0.35,
            marker=dict(colors=PURPLE_PALETTE[:len(labels)]),
            textinfo="label+percent",
        ))

    elif chart_type == "line":
        fig = go.Figure()
        for i, ds in enumerate(datasets):
            fig.add_trace(go.Scatter(
                x=labels,
                y=ds.get("values", []),
                name=ds.get("name", f"Series {i+1}"),
                mode="lines+markers",
                line=dict(color=PURPLE_PALETTE[i % len(PURPLE_PALETTE)], width=3),
                marker=dict(size=8),
            ))

    elif chart_type == "scatter" and datasets:
        # For scatter: treat first dataset as y, labels as x (if numeric)
        fig = go.Figure()
        for i, ds in enumerate(datasets):
            try:
                x_vals = [float(l) for l in labels]
            except ValueError:
                x_vals = list(range(len(labels)))
            fig.add_trace(go.Scatter(
                x=x_vals,
                y=ds.get("values", []),
                name=ds.get("name", f"Series {i+1}"),
                mode="markers",
                marker=dict(color=PURPLE_PALETTE[i % len(PURPLE_PALETTE)], size=10),
            ))

    else:  # default: bar
        fig = go.Figure()
        for i, ds in enumerate(datasets):
            fig.add_trace(go.Bar(
                x=labels,
                y=ds.get("values", []),
                name=ds.get("name", f"Series {i+1}"),
                marker_color=PURPLE_PALETTE[i % len(PURPLE_PALETTE)],
            ))
        if len(datasets) > 1:
            fig.update_layout(barmode="group")

    if fig is None:
        return

    fig.update_layout(
        title=dict(text=title, font=dict(size=18, family="Inter, sans-serif", color="#333")),
        xaxis_title=x_label,
        yaxis_title=y_label,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", size=13, color="#444"),
        legend=dict(bgcolor="rgba(255,255,255,0.8)", bordercolor="#ddd", borderwidth=1),
        margin=dict(l=50, r=30, t=60, b=50),
        xaxis=dict(gridcolor="#f0f0f0", zeroline=False),
        yaxis=dict(gridcolor="#f0f0f0", zeroline=False),
        hoverlabel=dict(bgcolor="white", bordercolor="#ddd", font=dict(size=13)),
    )

    st.plotly_chart(fig, use_container_width=True)


# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### ⚙️ Configuration")
    
    api_key = st.text_input(
        "Google AI Studio API Key",
        type="password",
        help="Enter your API key from Google AI Studio",
        placeholder="Enter API key..."
    )
    
    if api_key:
        genai.configure(api_key=api_key)
        indexing_model  = genai.GenerativeModel('gemini-2.5-flash')
        reasoning_model = genai.GenerativeModel('gemini-2.5-flash')
        st.markdown('<span class="badge badge-success">✅ Connected</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="badge badge-info">⚠️ Not Connected</span>', unsafe_allow_html=True)
    
    st.divider()
    
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

    # ── NEW: Graph settings ──────────────────────────────────────────────────
    st.markdown("### 📊 Graph Settings")
    auto_plot = st.toggle(
        "Auto-plot graphs",
        value=True,
        help="Automatically detect and plot charts when the query involves numeric data.",
    )
    chart_type_override = st.selectbox(
        "Preferred chart type",
        ["Auto-detect", "Bar", "Line", "Pie", "Scatter"],
        help="Override the AI's chart type choice.",
    )
    st.divider()
    # ────────────────────────────────────────────────────────────────────────

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
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Clear", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    with col2:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()
    
    with st.expander("📖 How to Use"):
        st.markdown("""
        **Quick Start:**
        1. 🔑 Enter API Key above
        2. 📤 Upload your PDF document
        3. ⏳ Wait for processing
        4. 💬 Ask questions about your document
        5. 📊 Get AI-powered insights + auto charts!
        """)
    
    with st.expander("💡 Graph Tips"):
        st.markdown("""
        **To trigger a graph, ask things like:**
        - *"Plot the quarterly revenue"*
        - *"Show a bar chart of sales by region"*
        - *"Visualize the expense breakdown"*
        - *"Graph the year-over-year growth"*
        - *"Pie chart of market share"*
        
        Or simply enable **Auto-plot graphs** — it will detect data automatically!
        """)
    
    with st.expander("🎯 Example Queries"):
        st.markdown("""
        - *"What are the Q3 revenue figures?"*
        - *"Plot monthly sales as a bar chart"*
        - *"Show a pie chart of expense categories"*
        - *"Graph revenue trends over the years"*
        - *"Compare year-over-year growth"*
        """)

# ─────────────────────────────────────────────
# MAIN CONTENT
# ─────────────────────────────────────────────
if not api_key:
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
    
    st.markdown("### ✨ Powerful Features")
    col1, col2, col3, col4 = st.columns(4)
    features = [
        ("📊", "Chart Analysis", "Extract insights from complex graphs and visualizations"),
        ("📋", "Table Extraction", "Parse and analyze tabular data from any document"),
        ("🔍", "Smart Search", "Find relevant information instantly across entire documents"),
        ("📈", "Auto Graphing", "Ask a question → get an interactive Plotly chart instantly"),
    ]
    for col, (icon, title, desc) in zip([col1, col2, col3, col4], features):
        with col:
            st.markdown(f"""
                <div class="feature-card">
                    <div class="feature-icon">{icon}</div>
                    <div class="feature-title">{title}</div>
                    <div class="feature-desc">{desc}</div>
                </div>
            """, unsafe_allow_html=True)

else:
    # ── HELPER: convert PDF to images ────────────────────────────────────────
    def get_pdf_images(uploaded_file):
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        image_paths = []
        if not os.path.exists("temp_images"):
            os.makedirs("temp_images")
        for i in range(len(doc)):
            page = doc.load_page(i)
            pix  = page.get_pixmap(matrix=fitz.Matrix(2, 2))
            path = f"temp_images/page_{i}.png"
            pix.save(path)
            image_paths.append(path)
        return image_paths

    # ── File upload ───────────────────────────────────────────────────────────
    st.markdown("### 📤 Upload Your Document")
    col1, col2 = st.columns([3, 1])
    with col1:
        uploaded_file = st.file_uploader(
            "Drag and drop or click to browse",
            type="pdf",
            help="Upload PDFs like financial reports, research papers, or technical documents",
            label_visibility="collapsed",
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

    # ── Document processing ───────────────────────────────────────────────────
    if uploaded_file and api_key:
        if 'vector_db' not in st.session_state or st.session_state.get('last_file') != uploaded_file.name:
            st.markdown("""
                <div class="status-card status-card-info loading-pulse">
                    <h3 style="margin:0;">🔄 Processing Your Document</h3>
                    <p style="margin-top:0.5rem; color:#666;">This may take a moment depending on document size...</p>
                </div>
            """, unsafe_allow_html=True)
            
            with st.status("🚀 Processing Pipeline Active", expanded=True) as status:
                st.write("📄 **Step 1/3:** Converting PDF pages to high-quality images...")
                progress_bar = st.progress(0)
                img_paths = get_pdf_images(uploaded_file)
                progress_bar.progress(33)
                st.success(f"✅ Converted {len(img_paths)} pages successfully!")
                
                st.write("🤖 **Step 2/3:** AI is analyzing each page and generating summaries...")
                summaries = []
                for idx, path in enumerate(img_paths):
                    try:
                        img = Image.open(path)
                        res = indexing_model.generate_content([
                            "Summarize this page accurately for search. Include all numbers, "
                            "tables, figures, percentages and data values you can see.",
                            img,
                        ])
                        summaries.append(res.text)
                        progress_bar.progress(33 + int((idx + 1) / len(img_paths) * 34))
                    except Exception as e:
                        st.error(f"Error processing page {idx + 1}: {str(e)}")
                        summaries.append(f"Page {idx + 1} - Processing error")
                st.success(f"✅ Generated {len(summaries)} AI summaries!")
                
                st.write("💾 **Step 3/3:** Building searchable vector database...")
                client = chromadb.Client()
                collection = client.create_collection(
                    name=f"col_{uploaded_file.name[:5]}_{int(datetime.now().timestamp())}"
                )
                for i, s in enumerate(summaries):
                    collection.add(
                        documents=[s],
                        metadatas=[{"path": img_paths[i], "page": i + 1, "summary": s}],
                        ids=[str(i)],
                    )
                progress_bar.progress(100)
                st.success("✅ Vector database created and optimized!")
                
                st.session_state.vector_db   = collection
                st.session_state.last_file   = uploaded_file.name
                st.session_state.query_count = 0
                st.session_state.img_paths   = img_paths
                st.session_state.summaries   = summaries

                status.update(label="✅ Processing Complete!", state="complete", expanded=False)
            
            st.balloons()
            st.markdown(f"""
                <div class="status-card status-card-success">
                    <h3 style="margin:0;">🎉 Document Ready for Analysis!</h3>
                    <p style="margin-top:0.5rem; color:#666;">
                        Successfully indexed <strong>{len(img_paths)} pages</strong> from
                        <strong>{uploaded_file.name}</strong>
                    </p>
                    <p style="margin-top:0.5rem; font-size:0.9rem; color:#28a745;">
                        💬 You can now ask questions below — including chart requests!
                    </p>
                </div>
            """, unsafe_allow_html=True)

        st.divider()

        # ── CHAT INTERFACE ────────────────────────────────────────────────────
        st.markdown("### 💬 Ask Questions About Your Document")
        
        if "messages" not in st.session_state:
            st.session_state.messages = []
        
        # Replay chat history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])
                # Re-render stored chart data
                if message.get("chart_data"):
                    st.markdown('<span class="chart-badge">📈 AUTO GRAPH</span>', unsafe_allow_html=True)
                    render_plotly_chart(message["chart_data"])
                if "image" in message and "page" in message:
                    with st.expander(f"📄 View Source — Page {message['page']}", expanded=False):
                        st.image(message["image"], use_container_width=True)
        
        query = st.chat_input("💭 Ask about charts, tables, data — or say 'plot a bar chart of...'")
        
        if query:
            st.session_state.query_count = st.session_state.get('query_count', 0) + 1
            
            with st.chat_message("user"):
                st.write(query)
            st.session_state.messages.append({"role": "user", "content": query})
            
            with st.chat_message("assistant"):
                with st.spinner("🔍 Searching document and analyzing..."):
                    try:
                        # ── Retrieval ────────────────────────────────────────
                        results = st.session_state.vector_db.query(
                            query_texts=[query], n_results=1
                        )
                        best_meta    = results['metadatas'][0][0]
                        best_page_path = best_meta['path']
                        page_num       = best_meta['page']
                        page_summary   = best_meta.get('summary', '')

                        # ── Generation (text answer) ─────────────────────────
                        img_to_analyze = Image.open(best_page_path)
                        prompt = (
                            f"Using the provided document image, answer this question in detail: {query}\n\n"
                            "Provide specific information, numbers, and insights from the image."
                        )
                        response = reasoning_model.generate_content([prompt, img_to_analyze])
                        st.write(response.text)

                        # ── Graph plotting logic ─────────────────────────────
                        wants_chart  = should_plot_graph(query)
                        chart_data   = None

                        if auto_plot and wants_chart:
                            with st.spinner("📊 Extracting data for chart..."):
                                # Combine page summary + AI answer for richer context
                                context = f"{page_summary}\n\n{response.text}"

                                # Apply user override if set
                                modified_query = query
                                if chart_type_override != "Auto-detect":
                                    modified_query = f"{query} (use {chart_type_override.lower()} chart)"

                                chart_data = extract_chart_data(
                                    modified_query, context, reasoning_model
                                )

                            if chart_data:
                                st.markdown(
                                    '<span class="chart-badge">📈 AUTO GRAPH</span>',
                                    unsafe_allow_html=True,
                                )
                                render_plotly_chart(chart_data)
                            else:
                                st.info(
                                    "💡 Couldn't extract structured numeric data for a chart. "
                                    "Try rephrasing: e.g. *'Plot a bar chart of quarterly revenue'*."
                                )

                        # ── Manual plot button (always shown for data queries) ──
                        elif not auto_plot and wants_chart:
                            if st.button("📊 Generate Chart from this Answer", key=f"plot_{st.session_state.query_count}"):
                                context    = f"{page_summary}\n\n{response.text}"
                                chart_data = extract_chart_data(query, context, reasoning_model)
                                if chart_data:
                                    render_plotly_chart(chart_data)
                                else:
                                    st.warning("No plottable numeric data found on this page.")

                        # ── Source expander ──────────────────────────────────
                        with st.expander(f"📄 View Source — Page {page_num}", expanded=False):
                            st.image(img_to_analyze, use_container_width=True)
                            st.caption(f"📍 Reference: Page {page_num} of {uploaded_file.name}")

                        # ── Save to history ──────────────────────────────────
                        st.session_state.messages.append({
                            "role":       "assistant",
                            "content":    response.text,
                            "image":      img_to_analyze,
                            "page":       page_num,
                            "chart_data": chart_data,
                        })

                    except Exception as e:
                        st.error(f"❌ Error processing query: {str(e)}")
                        st.info("💡 Try rephrasing your question or check your API key.")

        # ── Example queries ───────────────────────────────────────────────────
        if len(st.session_state.messages) == 0:
            st.markdown("### 💡 Example Questions to Get Started")
            st.markdown('<p style="color:#666;margin-bottom:1rem;">Click any example or type your own:</p>', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📊 Plot quarterly revenue as bar chart", use_container_width=True):
                    st.session_state.example_query = "Plot the quarterly revenue as a bar chart"
                    st.rerun()
                if st.button("📈 Graph trends over time", use_container_width=True):
                    st.session_state.example_query = "Graph trends or growth over time as a line chart"
                    st.rerun()
                if st.button("🥧 Pie chart of expense categories", use_container_width=True):
                    st.session_state.example_query = "Show a pie chart of the expense or cost categories"
                    st.rerun()
            with col2:
                if st.button("📝 Summarize key findings", use_container_width=True):
                    st.session_state.example_query = "What are the main findings or conclusions?"
                    st.rerun()
                if st.button("🔍 What are the key metrics?", use_container_width=True):
                    st.session_state.example_query = "What are the key financial metrics or important numbers?"
                    st.rerun()
                if st.button("💰 Compare year-over-year growth", use_container_width=True):
                    st.session_state.example_query = "Plot year-over-year growth as a bar or line chart"
                    st.rerun()

        if 'example_query' in st.session_state:
            del st.session_state.example_query
            st.rerun()

# --- FOOTER ---
st.divider()
st.markdown("""
    <div class="custom-footer">
        <p style="font-size: 1rem; font-weight: 600; margin-bottom: 0.5rem;">
            🚀 Powered by Google Gemini 2.5 Flash + Plotly
        </p>
        <p style="font-size: 0.9rem; color: #888; margin-bottom: 0.5rem;">
            Built with Streamlit • ChromaDB Vector Store • PyMuPDF • Plotly
        </p>
        <p style="font-size: 0.8rem; color: #aaa;">
            Made with ❤️ for researchers and analysts
        </p>
    </div>
""", unsafe_allow_html=True)
