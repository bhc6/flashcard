"""
Flask API 后端 - Anki 闪卡生成器
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import json
import tempfile
import uuid
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

from Anki_flashcards_creator import (
    read_pdf, read_pptx, read_ppt,
    get_openai_client, PROMPTS, LANGUAGE, OCR_AVAILABLE, PPTX_AVAILABLE
)
from Anki_flashcards_from_json import (
    load_flashcards_from_json, generate_flashcards_from_text,
    enhance_flashcard_with_api, export_to_json, export_to_anki_txt,
    export_to_anki_tsv, export_to_csv
)

load_dotenv()

app = Flask(__name__)
CORS(app)

ROOT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
UPLOAD_FOLDER = os.path.join(ROOT_DIRECTORY, 'uploads')
ALLOWED_EXTENSIONS = {'pdf', 'pptx', 'ppt', 'json', 'txt'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

sessions = {}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_session(session_id):
    if session_id not in sessions:
        sessions[session_id] = {'flashcards': [], 'filename': None, 'text_content': ''}
    return sessions[session_id]

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'ok',
        'ocr_available': OCR_AVAILABLE,
        'pptx_available': PPTX_AVAILABLE,
        'api_available': os.environ.get("ARK_API_KEY") is not None
    })

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': '没有上传文件'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '未选择文件'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': '不支持的文件类型'}), 400
    
    try:
        session_id = str(uuid.uuid4())
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"{session_id}_{filename}")
        file.save(filepath)
        
        ext = filename.rsplit('.', 1)[1].lower()
        text_content = ""
        flashcards = []
        
        if ext == 'pdf':
            text_content = read_pdf(filepath)
        elif ext == 'pptx':
            text_content = read_pptx(filepath) if PPTX_AVAILABLE else ""
        elif ext == 'ppt':
            text_content = read_ppt(filepath)
        elif ext == 'json':
            result = load_flashcards_from_json(filepath)
            if result and result['type'] == 'flashcards':
                flashcards = result['content']
            elif result and result['type'] == 'raw_text':
                text_content = result['content']
        elif ext == 'txt':
            with open(filepath, 'r', encoding='utf-8') as f:
                text_content = f.read()
        
        session = get_session(session_id)
        session['filename'] = filename
        session['text_content'] = text_content
        session['flashcards'] = flashcards
        
        os.remove(filepath)
        
        return jsonify({
            'session_id': session_id,
            'filename': filename,
            'text_length': len(text_content),
            'flashcards_count': len(flashcards),
            'has_text': bool(text_content),
            'has_flashcards': bool(flashcards)
        })
    except Exception as e:
        return jsonify({'error': f'处理文件失败: {str(e)}'}), 500

@app.route('/api/generate', methods=['POST'])
def generate_flashcards():
    data = request.get_json()
    session_id = data.get('session_id')
    text = data.get('text', '')
    
    if session_id and session_id in sessions:
        if not text:
            text = sessions[session_id].get('text_content', '')
    
    if not text:
        return jsonify({'error': '没有可处理的文本'}), 400
    
    try:
        flashcards = generate_flashcards_from_text(text)
        if not flashcards:
            return jsonify({'error': '生成闪卡失败'}), 500
        
        if session_id:
            get_session(session_id)['flashcards'] = flashcards
        
        return jsonify({'success': True, 'flashcards': flashcards, 'count': len(flashcards)})
    except Exception as e:
        return jsonify({'error': f'生成失败: {str(e)}'}), 500

@app.route('/api/flashcards', methods=['GET'])
def get_flashcards():
    session_id = request.args.get('session_id')
    if not session_id or session_id not in sessions:
        return jsonify({'error': '会话不存在'}), 404
    
    session = sessions[session_id]
    return jsonify({
        'flashcards': session['flashcards'],
        'filename': session['filename'],
        'count': len(session['flashcards'])
    })

@app.route('/api/flashcards', methods=['POST'])
def save_flashcards():
    data = request.get_json()
    session_id = data.get('session_id') or str(uuid.uuid4())
    get_session(session_id)['flashcards'] = data.get('flashcards', [])
    return jsonify({'success': True, 'session_id': session_id})

@app.route('/api/flashcards/<int:index>', methods=['PUT'])
def update_flashcard(index):
    data = request.get_json()
    session_id = data.get('session_id')
    if not session_id or session_id not in sessions:
        return jsonify({'error': '会话不存在'}), 404
    
    flashcards = sessions[session_id]['flashcards']
    if 0 <= index < len(flashcards):
        flashcards[index] = {'question': data.get('question', ''), 'answer': data.get('answer', '')}
        return jsonify({'success': True})
    return jsonify({'error': '索引超出范围'}), 400

@app.route('/api/flashcards/<int:index>', methods=['DELETE'])
def delete_flashcard(index):
    session_id = request.args.get('session_id')
    if not session_id or session_id not in sessions:
        return jsonify({'error': '会话不存在'}), 404
    
    flashcards = sessions[session_id]['flashcards']
    if 0 <= index < len(flashcards):
        flashcards.pop(index)
        return jsonify({'success': True, 'count': len(flashcards)})
    return jsonify({'error': '索引超出范围'}), 400

@app.route('/api/flashcards/add', methods=['POST'])
def add_flashcard():
    data = request.get_json()
    question, answer = data.get('question', ''), data.get('answer', '')
    if not question or not answer:
        return jsonify({'error': '问题和答案不能为空'}), 400
    
    session_id = data.get('session_id') or str(uuid.uuid4())
    session = get_session(session_id)
    session['flashcards'].append({'question': question, 'answer': answer})
    return jsonify({'success': True, 'session_id': session_id, 'count': len(session['flashcards'])})

@app.route('/api/enhance', methods=['POST'])
def enhance_flashcards():
    data = request.get_json()
    session_id = data.get('session_id')
    if not session_id or session_id not in sessions:
        return jsonify({'error': '会话不存在'}), 404
    
    flashcards = sessions[session_id]['flashcards']
    if not flashcards:
        return jsonify({'error': '没有可增强的闪卡'}), 400
    
    try:
        for i in range(len(flashcards)):
            flashcards[i] = enhance_flashcard_with_api(flashcards[i])
        return jsonify({'success': True, 'count': len(flashcards)})
    except Exception as e:
        return jsonify({'error': f'增强失败: {str(e)}'}), 500

@app.route('/api/export', methods=['POST'])
def export_flashcards():
    data = request.get_json()
    session_id = data.get('session_id')
    format_type = data.get('format', 'json')
    
    if not session_id or session_id not in sessions:
        return jsonify({'error': '会话不存在'}), 404
    
    flashcards = sessions[session_id]['flashcards']
    if not flashcards:
        return jsonify({'error': '没有可导出的闪卡'}), 400
    
    try:
        base_name = sessions[session_id].get('filename', 'flashcards')
        if '.' in base_name:
            base_name = base_name.rsplit('.', 1)[0]
        
        temp_dir = tempfile.mkdtemp()
        output_path = os.path.join(temp_dir, f"{base_name}_anki.{format_type}")
        
        if format_type == 'json':
            export_to_json(flashcards, output_path)
        elif format_type == 'txt':
            export_to_anki_txt(flashcards, output_path)
        elif format_type == 'tsv':
            export_to_anki_tsv(flashcards, output_path)
        elif format_type == 'csv':
            export_to_csv(flashcards, output_path)
        else:
            return jsonify({'error': '不支持的格式'}), 400
        
        return send_file(output_path, as_attachment=True, download_name=os.path.basename(output_path))
    except Exception as e:
        return jsonify({'error': f'导出失败: {str(e)}'}), 500

@app.route('/api/import-json', methods=['POST'])
def import_json():
    data = request.get_json()
    flashcards = data.get('flashcards', [])
    
    valid_cards = [{'question': str(c['question']), 'answer': str(c['answer'])}
                   for c in flashcards if isinstance(c, dict) and 'question' in c and 'answer' in c]
    
    if not valid_cards:
        return jsonify({'error': '没有有效的闪卡数据'}), 400
    
    session_id = str(uuid.uuid4())
    get_session(session_id)['flashcards'] = valid_cards
    return jsonify({'success': True, 'session_id': session_id, 'count': len(valid_cards)})

@app.route('/api/parse-text', methods=['POST'])
def parse_text():
    data = request.get_json()
    text = data.get('text', '')
    separator = data.get('separator', ';')
    
    if not text:
        return jsonify({'error': '没有可解析的文本'}), 400
    
    flashcards = []
    for line in text.strip().split('\n'):
        if separator in line:
            parts = line.split(separator, 1)
            q, a = parts[0].strip(), parts[1].strip()
            if q and a:
                flashcards.append({'question': q, 'answer': a})
    
    if not flashcards:
        return jsonify({'error': '未能解析出任何闪卡'}), 400
    
    session_id = str(uuid.uuid4())
    get_session(session_id)['flashcards'] = flashcards
    return jsonify({'success': True, 'session_id': session_id, 'flashcards': flashcards, 'count': len(flashcards)})

if __name__ == '__main__':
    print("=" * 50)
    print("Anki 闪卡生成器 API 服务")
    print(f"OCR: {'可用' if OCR_AVAILABLE else '不可用'}")
    print(f"PPTX: {'可用' if PPTX_AVAILABLE else '不可用'}")
    print(f"API: {'可用' if os.environ.get('ARK_API_KEY') else '不可用'}")
    print("=" * 50)
    print("http://localhost:5000")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5000, debug=True)
