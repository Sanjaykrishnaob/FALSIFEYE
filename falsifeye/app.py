import os
import sys

print("Initializing FALSIFEYE...")

try:
    from flask import Flask, render_template, request, redirect, url_for, send_file, jsonify
    from werkzeug.utils import secure_filename
    print("Flask imported successfully.")
except ImportError as e:
    print(f"CRITICAL ERROR: Could not import Flask. {e}")
    sys.exit(1)

try:
    from modules.media_verifier import analyze_media
    from modules.nlp_verifier import verify_statement
    from modules.transcriber import transcribe_audio
    from modules.report_generator import generate_report
    from modules.chatbot import get_chat_response
    from modules.evidence_manager import evidence_manager
    print("Custom modules imported successfully.")
except ImportError as e:
    print(f"CRITICAL ERROR: Could not import project modules. {e}")
    print("Make sure you have installed requirements: pip install -r falsifeye/requirements.txt")
    sys.exit(1)

import uuid

app = Flask(__name__)
# Use absolute path for uploads to avoid CWD confusion
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.config['UPLOAD_FOLDER'] = os.path.join(BASE_DIR, 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 # 16MB max limit

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Store results in memory for demo purposes (use DB in production)
analysis_results_db = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/history')
def history():
    history_data = evidence_manager.get_history()
    # Sort by timestamp descending
    history_data.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
    return render_template('history.html', history=history_data)

@app.route('/settings')
def settings():
    return render_template('settings.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    
    file = request.files['file']
    evidence_type = request.form.get('type')
    
    if file.filename == '':
        return redirect(request.url)
    
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        case_id = str(uuid.uuid4())[:8]
        
        # --- Chain of Custody: Log Evidence ---
        evidence_entry = evidence_manager.log_evidence(filepath, case_id)
        file_hash = evidence_entry['sha256_hash']
        
        # Perform Analysis
        results = {}
        results['filename'] = filename
        results['type'] = evidence_type
        results['file_hash'] = file_hash
        
        if evidence_type in ['image', 'video', 'audio', 'document']:
            media_analysis = analyze_media(filepath, evidence_type)
            results.update(media_analysis)
            
            if evidence_type == 'audio':
                transcription = transcribe_audio(filepath)
                results['transcription'] = transcription
                
        elif evidence_type == 'text':
            # For text, we expect a text file or direct input (here assuming file for consistency)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                nlp_analysis = verify_statement(content)
                results.update(nlp_analysis)
                results['content_snippet'] = content[:100] + "..."
            except:
                results['error'] = "Could not read text file."

        # Generate PDF Report
        report_filename = f"report_{case_id}.pdf"
        report_path = os.path.join(app.config['UPLOAD_FOLDER'], report_filename)
        generate_report(case_id, filename, results, report_path, file_hash=file_hash)
        results['report_path'] = report_filename
        
        # Log Analysis Completion
        evidence_manager.log_analysis(case_id, file_hash, results)
        
        analysis_results_db[case_id] = results
        
        return redirect(url_for('result', case_id=case_id))

@app.route('/result/<case_id>')
def result(case_id):
    result_data = analysis_results_db.get(case_id)
    if not result_data:
        return "Result not found", 404
    return render_template('result.html', result=result_data, case_id=case_id)

@app.route('/download/<filename>')
def download_report(filename):
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename), as_attachment=True)

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        query = data.get('query')
        case_id = data.get('case_id')
        
        context = analysis_results_db.get(case_id, {})
        response = get_chat_response(query, context)
        
        return jsonify({'response': response})
    except Exception as e:
        print(f"ERROR in /chat: {e}")
        import traceback
        with open("error_log.txt", "a") as f:
            f.write(f"ERROR in /chat: {e}\n")
            traceback.print_exc(file=f)
        return jsonify({'response': "Internal Server Error"}), 500

if __name__ == '__main__':
    print("Running Flask app...")
    # Run on 0.0.0.0 to ensure it's accessible from external browsers if needed
    app.run(debug=False, host='0.0.0.0', port=8081)
    print("App finished running.")
