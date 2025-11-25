"""
Anki Flashcards Generator from JSON
从 JSON 文件读取闪卡数据，并可通过 API 进行增强处理

使用方法:
1. 将 JSON 闪卡文件放入 SOURCE_DOCUMENTS 文件夹或指定路径
2. 运行: python Anki_flashcards_from_json.py [json文件路径]
3. 生成的文件可以直接导入 Anki

JSON 文件格式要求:
[
    {"question": "问题1", "answer": "答案1"},
    {"question": "问题2", "answer": "答案2"},
    ...
]
"""

import os
from openai import OpenAI, APIConnectionError
from dotenv import load_dotenv
import json
import csv
import argparse

# Language setting: 'en' for English, 'zh' for Chinese
LANGUAGE = 'zh'  # 可选: 'en' 或 'zh'

ROOT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
load_dotenv()
ARK_BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"


def get_openai_client():
    """获取 OpenAI API 客户端"""
    api_key = os.environ.get("ARK_API_KEY")
    if not api_key:
        print("警告: 未设置 ARK_API_KEY，API 增强功能不可用")
        return None
    return OpenAI(api_key=api_key, base_url=ARK_BASE_URL)


# API 客户端（可选）
client = None
try:
    client = get_openai_client()
except Exception as e:
    print(f"警告: API 客户端初始化失败 - {e}")


def load_flashcards_from_json(json_path):
    """从 JSON 文件加载闪卡数据，如果解析失败则返回原始文本"""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 尝试解析 JSON
        try:
            flashcards = json.loads(content)
            
            if not isinstance(flashcards, list):
                print(f"警告: JSON 格式不是数组，将使用 API 处理原始内容")
                return {"type": "raw_text", "content": content}
            
            valid_cards = []
            for i, card in enumerate(flashcards):
                if isinstance(card, dict) and 'question' in card and 'answer' in card:
                    valid_cards.append(card)
                else:
                    print(f"警告: 第 {i+1} 张卡片格式不正确，已跳过")
            
            if valid_cards:
                print(f"成功加载 {len(valid_cards)} 张闪卡")
                return {"type": "flashcards", "content": valid_cards}
            else:
                print(f"警告: 未找到有效闪卡，将使用 API 处理原始内容")
                return {"type": "raw_text", "content": content}
        
        except json.JSONDecodeError as e:
            print(f"警告: JSON 解析失败 ({e})，将使用 API 处理原始内容")
            return {"type": "raw_text", "content": content}
    
    except FileNotFoundError:
        print(f"错误: 找不到文件 {json_path}")
        return None
    except Exception as e:
        print(f"错误: 读取文件失败 - {e}")
        return None


def generate_flashcards_from_text(text):
    """使用 API 从原始文本生成闪卡"""
    if not client:
        print("错误: API 不可用，无法处理原始文本")
        return None
    
    prompts = {
        'zh': {
            'system': "你是一个有帮助的助手。",
            'user': f"根据提供的文本创建Anki闪卡，使用以下格式：问题;答案 换行 问题;答案 等。确保问题和对应的答案在同一行。不要添加任何介绍文本。文本：{text}"
        },
        'en': {
            'system': "You are a helpful assistant.",
            'user': f"Create anki flashcards with the provided text using a format: question;answer newline question;answer etc. Keep question and the corresponding answer on the same line. Do not add any introductory text. Text: {text}"
        }
    }
    
    lang = LANGUAGE if LANGUAGE in prompts else 'en'
    prompt = prompts[lang]
    
    flashcards_list = []
    
    try:
        print("正在使用 API 从原始文本生成闪卡...")
        response = client.chat.completions.create(
            model="doubao-seed-1-6-251015",
            messages=[
                {"role": "system", "content": prompt['system']},
                {"role": "user", "content": prompt['user']}
            ],
            temperature=0.3,
            max_tokens=2048,
        )
        result = response.choices[0].message.content.strip()
        
        # 解析 API 返回的字符串
        lines = result.split('\n')
        for line in lines:
            if ';' in line:
                parts = line.split(';', 1)
                question = parts[0].strip()
                answer = parts[1].strip()
                if question and answer:
                    flashcards_list.append({"question": question, "answer": answer})
        
        print(f"API 生成完成，共 {len(flashcards_list)} 张闪卡")
        return flashcards_list
    
    except APIConnectionError as e:
        print(f"API 连接错误: {e}")
        return None
    except Exception as e:
        print(f"API 调用失败: {e}")
        return None


def enhance_flashcard_with_api(card):
    """使用 API 增强闪卡内容（可选功能）"""
    if not client:
        return card
    
    prompts = {
        'zh': {
            'system': "你是一个有帮助的助手。",
            'user': f"请优化以下闪卡的问题和答案，使其更清晰易懂。保持原意不变。\n问题: {card['question']}\n答案: {card['answer']}\n\n请用格式返回：问题;答案"
        },
        'en': {
            'system': "You are a helpful assistant.",
            'user': f"Please optimize the following flashcard to make it clearer. Keep the original meaning.\nQuestion: {card['question']}\nAnswer: {card['answer']}\n\nReturn in format: question;answer"
        }
    }
    
    lang = LANGUAGE if LANGUAGE in prompts else 'en'
    prompt = prompts[lang]
    
    try:
        response = client.chat.completions.create(
            model="doubao-seed-1-6-251015",
            messages=[
                {"role": "system", "content": prompt['system']},
                {"role": "user", "content": prompt['user']}
            ],
            temperature=0.3,
            max_tokens=512,
        )
        result = response.choices[0].message.content.strip()
        
        if ';' in result:
            parts = result.split(';', 1)
            return {"question": parts[0].strip(), "answer": parts[1].strip()}
    except Exception as e:
        print(f"API 增强失败: {e}")
    
    return card


def export_to_json(flashcards, output_path):
    """导出为 JSON 格式"""
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(flashcards, f, ensure_ascii=False, indent=4)
        
        print(f"已导出 JSON 文件: {output_path}")
        return True
    except Exception as e:
        print(f"错误: 导出 JSON 失败 - {e}")
        return False


def export_to_anki_txt(flashcards, output_path):
    """导出为 Anki 可导入的 TXT 格式 (分号分隔)"""
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            for card in flashcards:
                question = card['question'].replace('\n', ' ').replace(';', '；')
                answer = card['answer'].replace('\n', ' ').replace(';', '；')
                f.write(f"{question};{answer}\n")
        
        print(f"已导出 Anki TXT 文件: {output_path}")
        print(f"导入说明: 在 Anki 中选择 '文件' -> '导入'，分隔符设为 ';'")
        return True
    except Exception as e:
        print(f"错误: 导出 TXT 失败 - {e}")
        return False


def export_to_anki_tsv(flashcards, output_path):
    """导出为 Anki 可导入的 TSV 格式 (制表符分隔)"""
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            for card in flashcards:
                question = card['question'].replace('\n', '<br>').replace('\t', ' ')
                answer = card['answer'].replace('\n', '<br>').replace('\t', ' ')
                f.write(f"{question}\t{answer}\n")
        
        print(f"已导出 Anki TSV 文件: {output_path}")
        return True
    except Exception as e:
        print(f"错误: 导出 TSV 失败 - {e}")
        return False


def export_to_csv(flashcards, output_path):
    """导出为 CSV 格式"""
    try:
        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Front', 'Back'])
            for card in flashcards:
                question = card['question'].replace('\n', '<br>')
                answer = card['answer'].replace('\n', '<br>')
                writer.writerow([question, answer])
        
        print(f"已导出 CSV 文件: {output_path}")
        return True
    except Exception as e:
        print(f"错误: 导出 CSV 失败 - {e}")
        return False


def print_flashcards_preview(flashcards, max_display=5):
    """预览闪卡内容"""
    print("\n--- 闪卡预览 ---")
    display_count = min(len(flashcards), max_display)
    for i, card in enumerate(flashcards[:display_count]):
        print(f"\n[卡片 {i+1}]")
        q_preview = card['question'][:100] + ('...' if len(card['question']) > 100 else '')
        a_preview = card['answer'][:100] + ('...' if len(card['answer']) > 100 else '')
        print(f"Q: {q_preview}")
        print(f"A: {a_preview}")
    
    if len(flashcards) > max_display:
        print(f"\n... 还有 {len(flashcards) - max_display} 张卡片未显示")


def find_json_files(directory):
    """在目录中查找 JSON 文件"""
    json_files = []
    if os.path.exists(directory):
        for f in os.listdir(directory):
            if f.endswith('.json'):
                json_files.append(os.path.join(directory, f))
    return json_files


def main():
    parser = argparse.ArgumentParser(
        description='从 JSON 文件生成 Anki 闪卡',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python Anki_flashcards_from_json.py flashcards.json
  python Anki_flashcards_from_json.py flashcards.json -f tsv
  python Anki_flashcards_from_json.py flashcards.json --enhance
  python Anki_flashcards_from_json.py --list
        """
    )
    
    parser.add_argument('json_file', nargs='?', help='JSON 闪卡文件路径')
    parser.add_argument('-f', '--format', choices=['json', 'txt', 'tsv', 'csv', 'all'], 
                        default='json', help='输出格式 (默认: json)')
    parser.add_argument('-o', '--output', help='输出文件路径')
    parser.add_argument('--list', action='store_true', help='列出可用的 JSON 文件')
    parser.add_argument('--preview', action='store_true', help='预览闪卡内容')
    parser.add_argument('--no-export', action='store_true', help='只预览不导出')
    parser.add_argument('--enhance', action='store_true', help='使用 API 增强闪卡内容')
    
    args = parser.parse_args()
    
    source_docs_path = os.path.join(ROOT_DIRECTORY, 'SOURCE_DOCUMENTS')
    os.makedirs(source_docs_path, exist_ok=True)
    
    # 列出所有 JSON 文件
    if args.list:
        json_files = find_json_files(source_docs_path) + find_json_files(ROOT_DIRECTORY)
        if json_files:
            print("可用的 JSON 闪卡文件:")
            for f in json_files:
                print(f"  - {os.path.basename(f)}")
        else:
            print("未找到 JSON 闪卡文件")
        return
    
    # 确定要使用的 JSON 文件
    if not args.json_file:
        json_files = find_json_files(source_docs_path)
        if not json_files:
            json_files = find_json_files(ROOT_DIRECTORY)
        
        if len(json_files) == 1:
            args.json_file = json_files[0]
            print(f"自动选择文件: {os.path.basename(args.json_file)}")
        elif len(json_files) > 1:
            print("找到多个 JSON 文件，请指定要使用的文件:")
            for f in json_files:
                print(f"  - {os.path.basename(f)}")
            print("\n用法: python Anki_flashcards_from_json.py <文件名>")
            return
        else:
            print("错误: 请指定 JSON 文件路径")
            return
    
    # 加载闪卡
    result = load_flashcards_from_json(args.json_file)
    if not result:
        return
    
    # 根据加载结果处理
    if result["type"] == "flashcards":
        flashcards = result["content"]
    elif result["type"] == "raw_text":
        flashcards = generate_flashcards_from_text(result["content"])
        if not flashcards:
            print("错误: 无法从原始文本生成闪卡")
            return
    else:
        return
    
    # 使用 API 增强（可选）
    if args.enhance:
        if client:
            print("正在使用 API 增强闪卡...")
            enhanced_cards = []
            for i, card in enumerate(flashcards):
                print(f"  处理卡片 {i+1}/{len(flashcards)}...")
                enhanced_cards.append(enhance_flashcard_with_api(card))
            flashcards = enhanced_cards
            print("API 增强完成")
        else:
            print("警告: API 不可用，跳过增强步骤")
    
    # 预览
    if args.preview or args.no_export:
        print_flashcards_preview(flashcards)
    
    if args.no_export:
        return
    
    # 生成输出文件名
    base_name = os.path.splitext(os.path.basename(args.json_file))[0]
    if base_name.endswith('_flashcards'):
        base_name = base_name[:-11]
    
    # 导出
    formats = ['json', 'txt', 'tsv', 'csv'] if args.format == 'all' else [args.format]
    
    for fmt in formats:
        if args.output and len(formats) == 1:
            output_path = args.output
        else:
            output_path = os.path.join(ROOT_DIRECTORY, f"{base_name}_anki.{fmt}")
        
        if fmt == 'json':
            export_to_json(flashcards, output_path)
        elif fmt == 'txt':
            export_to_anki_txt(flashcards, output_path)
        elif fmt == 'tsv':
            export_to_anki_tsv(flashcards, output_path)
        elif fmt == 'csv':
            export_to_csv(flashcards, output_path)
    
    print(f"\n完成! 共处理 {len(flashcards)} 张闪卡")


if __name__ == "__main__":
    main()