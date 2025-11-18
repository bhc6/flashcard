"""
Flask 应用主文件
提供 RESTful API 接口
"""
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from celery import Celery
from dotenv import load_dotenv
import uuid
from werkzeug.utils import secure_filename

# 加载环境变量
load_dotenv()

# 初始化 Flask 应用
app = Flask(__name__)
CORS(app)

# 配置
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')

# 确保上传目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 配置 Celery
app.config['CELERY_BROKER_URL'] = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
app.config['CELERY_RESULT_BACKEND'] = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

# 初始化 Celery
celery_app = Celery(
    app.name,
    broker=app.config['CELERY_BROKER_URL'],
    backend=app.config['CELERY_RESULT_BACKEND']
)
celery_app.conf.update(app.config)

# 支持的文件格式
ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.pptx', '.txt'}


def allowed_file(filename):
    """检查文件扩展名是否被允许"""
    return os.path.splitext(filename)[1].lower() in ALLOWED_EXTENSIONS


@celery_app.task(bind=True)
def process_file_task(self, file_path, file_extension):
    """
    处理文件的 Celery 任务
    
    Args:
        self: Celery task 实例
        file_path: 文件路径
        file_extension: 文件扩展名
    
    Returns:
        生成的闪卡列表
    """
    from services import TextExtractor, LLMService
    
    try:
        # 更新任务状态：正在提取文本
        self.update_state(state='PROGRESS', meta={'status': '正在提取文本内容...'})
        
        # 提取文本
        extractor = TextExtractor()
        text_content = extractor.extract_text(file_path, file_extension)
        
        if not text_content or not text_content.strip():
            raise ValueError("未能从文件中提取到有效文本内容")
        
        # 更新任务状态：正在生成闪卡
        self.update_state(state='PROGRESS', meta={'status': '正在调用 AI 生成闪卡...'})
        
        # 生成闪卡
        llm_service = LLMService()
        flashcards = llm_service.generate_flashcards(text_content)
        
        # 删除临时文件
        try:
            os.remove(file_path)
        except:
            pass
        
        return flashcards
    
    except Exception as e:
        # 删除临时文件
        try:
            os.remove(file_path)
        except:
            pass
        
        raise Exception(f"处理失败: {str(e)}")


@app.route('/api/generate-flashcards-async', methods=['POST'])
def generate_flashcards_async():
    """
    异步生成闪卡接口
    接收文件上传，创建后台任务，立即返回任务 ID
    """
    # 检查是否有文件
    if 'file' not in request.files:
        return jsonify({'error': '没有选择文件'}), 400
    
    file = request.files['file']
    
    # 检查文件名
    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400
    
    # 检查文件格式
    if not allowed_file(file.filename):
        return jsonify({
            'error': f'不支持的文件格式。支持的格式：{", ".join(ALLOWED_EXTENSIONS)}'
        }), 400
    
    try:
        # 生成唯一文件名
        file_extension = os.path.splitext(file.filename)[1].lower()
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        
        # 保存文件
        file.save(file_path)
        
        # 创建异步任务
        task = process_file_task.apply_async(args=[file_path, file_extension])
        
        # 返回任务 ID
        return jsonify({
            'message': '文件上传成功，正在后台处理...',
            'task_id': task.id,
            'status_url': f"{request.host_url}api/task-status/{task.id}"
        }), 202
    
    except Exception as e:
        return jsonify({'error': f'服务器错误: {str(e)}'}), 500


@app.route('/api/task-status/<task_id>', methods=['GET'])
def get_task_status(task_id):
    """
    查询任务状态接口
    
    Args:
        task_id: 任务 ID
    
    Returns:
        任务的当前状态和结果
    """
    task = process_file_task.AsyncResult(task_id)
    
    if task.state == 'PENDING':
        # 任务等待中
        response = {
            'state': task.state,
            'status': '等待处理...',
            'result': None
        }
    elif task.state == 'PROGRESS':
        # 任务进行中
        response = {
            'state': task.state,
            'status': task.info.get('status', ''),
            'result': None
        }
    elif task.state == 'SUCCESS':
        # 任务成功
        response = {
            'state': task.state,
            'status': '完成!',
            'result': task.result
        }
    else:
        # 任务失败
        response = {
            'state': task.state,
            'status': str(task.info),
            'result': None
        }
    
    return jsonify(response)


@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({'status': 'healthy'}), 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
