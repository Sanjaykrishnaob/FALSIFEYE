import os
import sys
import uuid
import json
import traceback
from pathlib import Path

import streamlit as st
from streamlit_option_menu import option_menu

st.set_page_config(page_title="FALSIFEYE — Forensics", layout="wide", initial_sidebar_state="expanded")

BASE_DIR = Path(__file__).parent
UPLOAD_FOLDER = BASE_DIR / 'falsifeye' / 'uploads'
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

# Try to import project modules
MODULES_OK = True
try:
    from werkzeug.utils import secure_filename
    from falsifeye.modules.media_verifier import analyze_media
    from falsifeye.modules.nlp_verifier import verify_statement
    from falsifeye.modules.transcriber import transcribe_audio
    from falsifeye.modules.report_generator import generate_report
    from falsifeye.modules.chatbot import get_chat_response
    from falsifeye.modules.evidence_manager import evidence_manager
except Exception as e:
    MODULES_OK = False
    IMPORT_ERR = e


def save_uploaded_file(uploaded_file):
    """Save uploaded file to disk."""
    filename = secure_filename(uploaded_file.name)
    filepath = UPLOAD_FOLDER / filename
    filepath.write_bytes(uploaded_file.getbuffer())
    return filename, str(filepath)


def run_analysis(filepath, filename, evidence_type):
    """Run forensic analysis on uploaded file."""
    results = {'filename': filename, 'type': evidence_type}
    try:
        case_id = str(uuid.uuid4())[:8]
        evidence_entry = evidence_manager.log_evidence(filepath, case_id)
        file_hash = evidence_entry.get('sha256_hash', 'N/A')
        results['file_hash'] = file_hash
        results['case_id'] = case_id

        if evidence_type in ['image', 'video', 'audio', 'document']:
            media_analysis = analyze_media(filepath, evidence_type)
            results.update(media_analysis)
            
            if evidence_type == 'audio':
                transcription = transcribe_audio(filepath)
                results['transcription'] = transcription

        elif evidence_type == 'text':
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                nlp_analysis = verify_statement(content)
                results.update(nlp_analysis)
                results['content_snippet'] = content[:200] + '...'
            except Exception:
                results['error'] = 'Could not read text file.'

        report_filename = f"report_{case_id}.pdf"
        report_path = UPLOAD_FOLDER / report_filename
        generate_report(case_id, filename, results, str(report_path), file_hash=file_hash)
        results['report_path'] = report_filename

        evidence_manager.log_analysis(case_id, file_hash, results)
        return case_id, results
    except Exception as e:
        st.error(f"Analysis failed: {e}")
        traceback.print_exc()
        return None, {'error': str(e)}


def main():
    st.title("🔍 FALSIFEYE — AI Forensic Toolkit")
    st.markdown("*Detect deepfakes, manipulated documents, and synthetic audio using advanced forensic AI*")

    if not MODULES_OK:
        st.error("⚠️ Project modules failed to import. Please check dependencies.")
        st.exception(IMPORT_ERR)
        st.stop()

    # Sidebar menu
    with st.sidebar:
        page = option_menu(
            "Menu",
            ["📊 Upload & Analyze", "💬 Forensic Chatbot", "📋 History"],
            icons=["upload", "chat", "list"],
            menu_icon="cast",
            default_index=0
        )

    # PAGE: Upload & Analyze
    if page == "📊 Upload & Analyze":
        st.header("Upload Evidence for Forensic Analysis")
        col1, col2 = st.columns([2, 1])

        with col1:
            uploaded_file = st.file_uploader("Choose a file (image, video, audio, document, text)")
            evidence_type = st.selectbox(
                "Evidence type",
                ['image', 'video', 'audio', 'document', 'text'],
                help="Select the type of evidence you're uploading"
            )

        with col2:
            st.info("**Note:** First analysis may be slow as models load.")

        if st.button("🔬 Run Analysis", use_container_width=True):
            if not uploaded_file:
                st.error("Please upload a file first.")
            else:
                with st.spinner('📁 Saving file...'):
                    filename, filepath = save_uploaded_file(uploaded_file)

                with st.spinner('⚙️ Running forensic analysis (this may take 1–3 minutes)...'):
                    case_id, results = run_analysis(filepath, filename, evidence_type)

                if case_id:
                    st.success(f"✅ Analysis completed — **Case ID: {case_id}**")
                    
                    # Display results
                    col1, col2 = st.columns(2)
                    with col1:
                        st.subheader("📊 Analysis Results")
                        st.json(results)
                    
                    with col2:
                        st.subheader("📥 Actions")
                        if results.get('report_path'):
                            report_path = UPLOAD_FOLDER / results['report_path']
                            if report_path.exists():
                                with open(report_path, 'rb') as f:
                                    st.download_button(
                                        '📄 Download PDF Report',
                                        data=f,
                                        file_name=results['report_path'],
                                        mime='application/pdf'
                                    )
                        
                        # Store case ID for chatbot
                        st.session_state.current_case_id = case_id
                        st.info(f"Case ID saved: **{case_id}**\n\nUse this in the Chatbot to ask questions about this analysis.")

    # PAGE: Forensic Chatbot
    elif page == "💬 Forensic Chatbot":
        st.header("🤖 Forensic AI Assistant")
        st.markdown("Ask questions about forensic analysis or this specific case.")

        col1, col2 = st.columns([3, 1])
        
        with col1:
            case_id_input = st.text_input(
                '📂 Case ID (optional)',
                value=st.session_state.get('current_case_id', ''),
                help="Enter a Case ID to get context-aware responses"
            )
        
        with col2:
            st.write("")  # spacer
            if st.button("🔄 Clear", use_container_width=True):
                st.session_state.pop('current_case_id', None)

        query = st.text_area(
            '💬 Your question',
            placeholder='Ask about deepfake detection, authenticity scores, forensic techniques...',
            height=100
        )

        if st.button('📤 Send', use_container_width=True):
            if not query.strip():
                st.error("Please enter a question.")
            else:
                context = {}
                if case_id_input:
                    try:
                        history = evidence_manager.get_history()
                        match = next((h for h in history if h.get('case_id') == case_id_input), None)
                        if match:
                            context = match.get('results', {})
                            st.info(f"📂 Using context from case: {case_id_input}")
                    except Exception:
                        context = {}

                with st.spinner('🧠 AI is thinking...'):
                    try:
                        response = get_chat_response(query, context)
                        st.markdown("### 🤖 Assistant")
                        st.markdown(response)
                    except Exception as e:
                        st.error(f"Chatbot error: {e}")

    # PAGE: History
    elif page == "📋 History":
        st.header("📋 Analysis History")
        
        try:
            history = evidence_manager.get_history()
            if not history:
                st.info("No analysis history yet. Upload and analyze a file to get started.")
            else:
                # Sort by timestamp descending
                history.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
                
                for idx, entry in enumerate(history[:20], 1):  # Show last 20
                    with st.expander(f"**Case {idx}:** {entry.get('filename', 'Unknown')} — {entry.get('timestamp', 'N/A')}"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Case ID:** `{entry.get('case_id', 'N/A')}`")
                            st.write(f"**Type:** {entry.get('type', 'Unknown')}")
                            st.write(f"**Hash:** `{entry.get('file_hash', 'N/A')[:16]}...`")
                        with col2:
                            results = entry.get('results', {})
                            if results:
                                st.json(results)
        except Exception as e:
            st.error(f"Could not load history: {e}")


if __name__ == '__main__':
    main()
