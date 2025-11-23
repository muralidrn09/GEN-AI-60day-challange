import streamlit as st
import sys
import os
from Hybridrag.hybrid import HybridRAG

# Add parent directory to Python path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Initialize theme state BEFORE page config
if 'theme' not in st.session_state:
    st.session_state.theme = 'light'

# Page configuration
st.set_page_config(
    page_title="TextBOT RAG System",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS - Black background with white text
st.markdown("""
<style>
    /* Main app background */
    .stApp {
        background-color: #000000 !important;
    }
    
    /* Header toolbar - transparent grey */
    header[data-testid="stHeader"] {
        background-color: rgba(128, 128, 128, 0.2) !important;
        backdrop-filter: blur(10px);
    }
    
    /* All text to white */
    .stApp, .stApp p, .stApp span, .stApp div, .stApp label, .stApp h1, .stApp h2, .stApp h3 {
        color: #ffffff !important;
    }
    
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        color: #ffffff;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        text-align: center;
        color: #cccccc;
        margin-bottom: 2rem;
    }
    .response-box {
        border: 2px solid #444444;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        background-color: #1a1a1a;
        color: #ffffff;
    }
    .vector-response {{
        border-left: 5px solid #4CAF50;
    }}
    .graph-response {{
        border-left: 5px solid #2196F3;
    }}
    .confidence-high {{
        color: #4CAF50;
        font-weight: bold;
    }}
    .confidence-medium {{
        color: #FF9800;
        font-weight: bold;
    }}
    .confidence-low {
        color: #F44336;
        font-weight: bold;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #1a1a1a !important;
    }
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }
    
    /* Sidebar collapse button - make it visible */
    [data-testid="collapsedControl"] {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 2px solid #666666 !important;
    }
    [data-testid="collapsedControl"]:hover {
        background-color: #f0f0f0 !important;
        border-color: #58a6ff !important;
    }
    [data-testid="collapsedControl"] svg {
        color: #000000 !important;
        fill: #000000 !important;
    }
    
    /* Sidebar close button */
    [data-testid="stSidebar"] button[kind="header"] {
        color: #ffffff !important;
    }
    [data-testid="stSidebar"] button[kind="header"]:hover {
        background-color: rgba(255, 255, 255, 0.1) !important;
    }
    
    /* File uploader styling */
    [data-testid="stSidebar"] button[kind="secondary"] {
        border: 2px solid #000000 !important;
        color: #000000 !important;
        background-color: #ffffff !important;
    }
    [data-testid="stSidebar"] button[kind="secondary"]:hover {
        border-color: #333333 !important;
        background-color: #f0f0f0 !important;
    }
    [data-testid="stSidebar"] .stFileUploader button {
        border: 2px solid #000000 !important;
        color: #000000 !important;
        background-color: #ffffff !important;
    }
    [data-testid="stSidebar"] .stFileUploader button:hover {
        border-color: #333333 !important;
        background-color: #f0f0f0 !important;
    }
    /* File uploader drop zone background */
    [data-testid="stSidebar"] [data-testid="stFileUploader"] > div > div {
        background-color: #ffffff !important;
        border: 2px dashed #000000 !important;
    }
    [data-testid="stSidebar"] [data-testid="stFileUploadDropzone"] {
        background-color: #ffffff !important;
        border: 2px dashed #000000 !important;
    }
    [data-testid="stSidebar"] .stFileUploader label {
        color: #000000 !important;
    }
    [data-testid="stSidebar"] .stFileUploader small {
        color: #333333 !important;
    }
    
    /* Text input and textarea */
    .stTextArea textarea, .stTextInput input {
        background-color: #2a2a2a !important;
        color: #ffffff !important;
        border: 1px solid #ffffff !important;
        font-size: 18px !important;
        caret-color: #ffffff !important;
    }
    .stTextArea textarea:focus, .stTextInput input:focus {
        border: 2px solid #ffffff !important;
        outline: none !important;
        box-shadow: none !important;
        caret-color: #ffffff !important;
    }
    
    /* Placeholder text styling */
    .stTextArea textarea::placeholder, .stTextInput input::placeholder {
        color: #888888 !important;
        opacity: 1 !important;
        font-size: 18px !important;
    }
    
    /* Custom button styling */
    .stButton > button {
        background-color: transparent !important;
        border: 2px solid #ffffff !important;
        color: #ffffff !important;
        pointer-events: auto !important;
        cursor: pointer !important;
    }
    .stButton > button:hover {
        border-color: #58a6ff !important;
        background-color: rgba(88, 166, 255, 0.1) !important;
    }
    .stButton > button:focus {
        background-color: transparent !important;
        border-color: #ffffff !important;
        box-shadow: none !important;
    }
    .stButton > button:active {
        background-color: transparent !important;
        border-color: #ffffff !important;
    }
    .stButton > button[data-baseweb="button"][kind="primary"],
    .stButton > button[kind="primary"] {
        background-color: transparent !important;
        border-color: #ffffff !important;
    }
    .stButton > button[data-baseweb="button"][kind="primary"]:hover,
    .stButton > button[kind="primary"]:hover {
        background-color: transparent !important;
        border-color: #58a6ff !important;
    }
    .stButton > button[data-baseweb="button"][kind="primary"]:focus,
    .stButton > button[kind="primary"]:focus {
        background-color: transparent !important;
        border-color: #ffffff !important;
        box-shadow: none !important;
    }
    .stButton > button[data-baseweb="button"][kind="primary"]:active,
    .stButton > button[kind="primary"]:active {
        background-color: transparent !important;
        border-color: #ffffff !important;
    }
    .stButton > button[data-baseweb="button"][kind="secondary"],
    .stButton > button[kind="secondary"] {
        background-color: transparent !important;
        border-color: #ffffff !important;
    }
    .stButton > button[data-baseweb="button"][kind="secondary"]:hover,
    .stButton > button[kind="secondary"]:hover {
        background-color: transparent !important;
        border-color: #58a6ff !important;
    }
    .stButton > button[data-baseweb="button"][kind="secondary"]:focus,
    .stButton > button[kind="secondary"]:focus {
        background-color: transparent !important;
        border-color: #ffffff !important;
        box-shadow: none !important;
    }
    .stButton > button[data-baseweb="button"][kind="secondary"]:active,
    .stButton > button[kind="secondary"]:active {
        background-color: transparent !important;
        border-color: #ffffff !important;
    }
    
    /* Success/Error messages */
    .stSuccess, .stError, .stWarning {
        color: #ffffff !important;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: #2a2a2a !important;
        color: #ffffff !important;
    }
    
    /* Divider */
    hr {
        border-color: #444444 !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state FIRST - before anything else
if 'initialized' not in st.session_state:
    st.session_state.initialized = False
    st.session_state.rag_system = None
    st.session_state.chat_history = []
    st.session_state.response_mode = 'both'  # 'vector', 'graph', or 'both'
    st.session_state.input_counter = 0  # For clearing input after send

# Try to initialize RAG system if not already done
if not st.session_state.initialized and st.session_state.rag_system is None:
    with st.spinner('🚀 Initializing BookBuddy RAG System...'):
        try:
            st.session_state.rag_system = HybridRAG()
            st.session_state.initialized = True
        except Exception as e:
            st.error(f"⚠️ Failed to initialize RAG system: {str(e)}")
            st.warning("Please check your configuration in `Hybridrag/config.py`")
            st.session_state.initialized = False

# Header
st.markdown('<div class="main-header">🤖 BookBuddy </div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header"> Your Education Companion</div>', unsafe_allow_html=True)

# Sidebar for document upload
with st.sidebar:
    st.header("📄 Document Upload")
    uploaded_file = st.file_uploader("Upload PDF Document", type=['pdf'])
    
    if uploaded_file is not None:
        if st.button("🔄 Process Document", type="primary", use_container_width=True):
            if st.session_state.initialized and st.session_state.rag_system:
                with st.spinner('Processing document...'):
                    result = st.session_state.rag_system.process_document(uploaded_file)
                    if result['success']:
                        st.success(f"✅ {result['message']}")
                    else:
                        st.error(f"❌ {result['message']}")
            else:
                st.error("❌ System not initialized. Please check configuration.")
    
    st.divider()
    
    # Temperature setting
    st.header("⚙️ Settings")
    if 'temperature' not in st.session_state:
        st.session_state.temperature = 0.3
    
    temperature = st.slider(
        "🌡️ Temperature",
        min_value=0.0,
        max_value=1.0,
        value=st.session_state.temperature,
        step=0.1,
        help="Controls randomness: 0 = focused and deterministic, 1 = creative and diverse"
    )
    st.session_state.temperature = temperature
    
    st.divider()
    
    # System stats
    st.header("📊 System Status")
    if st.session_state.initialized:
        st.success("✅ Vector Store: Connected")
        st.success("✅ Knowledge Graph: Connected")
    else:
        st.error("❌ System: Not Initialized")
    
    st.divider()
    
    # Clear data button
    # if st.button("🗑️ Clear All Data", use_container_width=True):
    #     if st.session_state.initialized and st.session_state.rag_system:
    #         st.session_state.rag_system.clear_all()
    #         st.session_state.chat_history = []
    #         st.success("✅ All data cleared!")
    #         st.rerun()
    #     else:
    #         st.error("❌ System not initialized.")

# Main chat interface
st.header("💬 Ask Questions")

# Question input - Centered with increased height and send button aligned
input_col1, input_col2, input_col3 = st.columns([2, 8, 1])

with input_col2:
    user_question = st.text_area("", placeholder="Type your question here...", 
                                  label_visibility="collapsed", 
                                  key=f"question_input_{st.session_state.input_counter}",
                                  height=100)

with input_col3:
    # Add spacing to align button with bottom of text area
    st.write("")
    st.write("")
    send_btn = st.button("Send", type="primary", use_container_width=True, key="send_button")

# Response mode selector - Below query window with smaller buttons
btn_col1, btn_col2, btn_col3, btn_col4, btn_col5, btn_col6, btn_col7 = st.columns([2, 1, 1, 1, 1, 1, 2])

with btn_col3:
    if st.button("📊", 
                 type="primary" if st.session_state.response_mode == 'vector' else "secondary",
                 help="Vector Store Only",
                 key="vector_mode"):
        st.session_state.response_mode = 'vector'
        st.rerun()

with btn_col4:
    if st.button("🕸️",
                 type="primary" if st.session_state.response_mode == 'graph' else "secondary",
                 help="Knowledge Graph Only",
                 key="graph_mode"):
        st.session_state.response_mode = 'graph'
        st.rerun()

with btn_col5:
    if st.button("🔄",
                 type="primary" if st.session_state.response_mode == 'both' else "secondary",
                 help="Both Responses",
                 key="both_mode"):
        st.session_state.response_mode = 'both'
        st.rerun()

# Handle send button
if send_btn:
    if not user_question or user_question.strip() == "":
        st.warning("⚠️ Please enter a question.")
    elif not st.session_state.initialized or not st.session_state.rag_system:
        st.error("❌ System not initialized. Please check configuration.")
    else:
        with st.spinner('🤔 Thinking...'):
            # Query the system with temperature setting
            response = st.session_state.rag_system.query(
                user_question, 
                temperature=st.session_state.temperature
            )
            
            # Store latest response to display below
            st.session_state.latest_response = {
                'question': user_question,
                'response': response,
                'response_mode': st.session_state.response_mode
            }
            
            # Clear the input box by changing the key
            st.session_state.input_counter += 1
            
            # Rerun to display response
            st.rerun()

# Display response below query window
if 'latest_response' in st.session_state and st.session_state.latest_response:
    st.divider()
    
    chat = st.session_state.latest_response
    response_mode = chat['response_mode']
    response = chat['response']
    
    # Display question
    st.markdown(f"""
    <div style='background-color: rgba(100, 100, 255, 0.1); padding: 15px; border-radius: 10px; margin-bottom: 20px;'>
        <strong>❓ Question:</strong> {chat['question']}
    </div>
    """, unsafe_allow_html=True)
    
    # Show both responses side by side if mode is 'both'
    if response_mode == 'both':
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="response-box">', unsafe_allow_html=True)
            st.markdown("### 📊 Vector Store Response")
            
            vec_resp = response['vector_response']
            st.markdown(f"**Answer:** {vec_resp['answer']}")
            
            confidence = vec_resp.get('confidence', 0.0)
            conf_class = "high-conf" if confidence >= 0.7 else "medium-conf" if confidence >= 0.4 else "low-conf"
            st.markdown(f'<p class="{conf_class}">Confidence: {confidence:.2%}</p>', unsafe_allow_html=True)
            
            if vec_resp['sources']:
                with st.expander("📚 View Sources"):
                    for i, source in enumerate(vec_resp['sources'][:3]):
                        st.text(f"Source {i+1} (Similarity: {source['similarity']:.3f}):")
                        st.caption(source['content'])
                        st.divider()
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="response-box">', unsafe_allow_html=True)
            st.markdown("### 🕸️ Knowledge Graph Response")
            
            graph_resp = response['graph_response']
            st.markdown(f"**Answer:** {graph_resp['answer']}")
            
            confidence = graph_resp.get('confidence', 0.0)
            conf_class = "high-conf" if confidence >= 0.7 else "medium-conf" if confidence >= 0.4 else "low-conf"
            st.markdown(f'<p class="{conf_class}">Confidence: {confidence:.2%}</p>', unsafe_allow_html=True)
            
            if graph_resp['entities']:
                with st.expander("🔗 View Entities & Relations"):
                    for i, entity in enumerate(graph_resp['entities'][:3]):
                        st.text(f"Entity: {entity['entity']} ({entity['type']})")
                        if entity['related_entities']:
                            st.caption(f"Related: {', '.join(entity['related_entities'][:5])}")
                        st.divider()
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Show only vector response
    elif response_mode == 'vector':
        st.markdown('<div class="response-box">', unsafe_allow_html=True)
        st.markdown("### 📊 Vector Store Response")
        
        vec_resp = response['vector_response']
        st.markdown(f"**Answer:** {vec_resp['answer']}")
        
        confidence = vec_resp.get('confidence', 0.0)
        conf_class = "high-conf" if confidence >= 0.7 else "medium-conf" if confidence >= 0.4 else "low-conf"
        st.markdown(f'<p class="{conf_class}">Confidence: {confidence:.2%}</p>', unsafe_allow_html=True)
        
        if vec_resp['sources']:
            with st.expander("📚 View Sources"):
                for i, source in enumerate(vec_resp['sources'][:3]):
                    st.text(f"Source {i+1} (Similarity: {source['similarity']:.3f}):")
                    st.caption(source['content'])
                    st.divider()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Show only graph response
    elif response_mode == 'graph':
        st.markdown('<div class="response-box">', unsafe_allow_html=True)
        st.markdown("### 🕸️ Knowledge Graph Response")
        
        graph_resp = response['graph_response']
        st.markdown(f"**Answer:** {graph_resp['answer']}")
        
        confidence = graph_resp.get('confidence', 0.0)
        conf_class = "high-conf" if confidence >= 0.7 else "medium-conf" if confidence >= 0.4 else "low-conf"
        st.markdown(f'<p class="{conf_class}">Confidence: {confidence:.2%}</p>', unsafe_allow_html=True)
        
        if graph_resp['entities']:
            with st.expander("🔗 View Entities & Relations"):
                for i, entity in enumerate(graph_resp['entities'][:3]):
                    st.text(f"Entity: {entity['entity']} ({entity['type']})")
                    if entity['related_entities']:
                        st.caption(f"Related: {', '.join(entity['related_entities'][:5])}")
                    st.divider()
        
        st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p>🚀 BookBuddy RAG System | Powered by OpenAI GPT-4o-mini, PGVector (Neon), and Neo4j</p>
    <p style='font-size: 0.8rem;'>Vector embeddings combined with knowledge graphs for accurate, hallucination-free responses</p>
</div>
""", unsafe_allow_html=True)