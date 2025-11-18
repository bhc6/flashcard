"""
LLM 服务
使用火山引擎 API 生成闪卡
火山方舟模型调用 API 与 OpenAI API 协议兼容
详细说明：https://www.volcengine.com/docs/82379/1330626
"""
import os
import json
from typing import List, Dict
from openai import OpenAI


class LLMService:
    """LLM 服务类，用于生成闪卡"""
    
    def __init__(self):
        """初始化 LLM 服务"""
        api_key = os.getenv('ARK_API_KEY')
        if not api_key:
            raise ValueError("未设置 ARK_API_KEY 环境变量")
        
        # 火山方舟 API 配置
        self.client = OpenAI(
            base_url="https://ark.cn-beijing.volces.com/api/v3",
            api_key=api_key
        )
        self.model = "doubao-seed-1-6-flash-250828"
    
    def generate_flashcards(self, text_content: str, max_cards: int = 10) -> List[Dict[str, str]]:
        """
        根据文本内容生成闪卡
        
        Args:
            text_content: 输入的文本内容
            max_cards: 最多生成的闪卡数量
        
        Returns:
            闪卡列表，每个闪卡包含 question 和 answer
        
        Raises:
            Exception: API 调用失败
        """
        if not text_content or not text_content.strip():
            raise ValueError("文本内容为空，无法生成闪卡")
        
        # 限制输入文本长度，避免超过 token 限制
        max_chars = 8000
        if len(text_content) > max_chars:
            text_content = text_content[:max_chars] + "..."
        
        system_prompt = """你是一个专业的学习助手，擅长从学习资料中提取关键知识点并生成高质量的问答式闪卡。

你的任务是：
1. 仔细阅读用户提供的文本内容
2. 识别其中的重要概念、定义、事实、流程等
3. 为每个关键知识点生成一对问答
4. 问题应当简洁明确，答案应当准确完整

请以 JSON 格式输出，格式如下：
[
  {
    "question": "问题1",
    "answer": "答案1"
  },
  {
    "question": "问题2",
    "answer": "答案2"
  }
]

注意：
- 只输出 JSON 数组，不要有其他内容
- 问题要有启发性，避免过于简单
- 答案要准确且完整
- 如果文本内容很短，可以生成较少的闪卡
"""
        
        user_prompt = f"""请基于以下内容生成最多 {max_cards} 张闪卡：

{text_content}

请以 JSON 格式输出闪卡列表。"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content
            
            # 解析 JSON 响应
            flashcards = self._parse_flashcards(content)
            
            return flashcards
        
        except Exception as e:
            raise Exception(f"调用火山引擎 API 失败: {str(e)}")
    
    def _parse_flashcards(self, content: str) -> List[Dict[str, str]]:
        """
        解析 LLM 返回的闪卡内容
        
        Args:
            content: LLM 返回的文本内容
        
        Returns:
            解析后的闪卡列表
        """
        try:
            # 尝试直接解析 JSON
            flashcards = json.loads(content)
            
            # 验证格式
            if not isinstance(flashcards, list):
                raise ValueError("返回的不是数组格式")
            
            # 验证每个闪卡的格式
            validated_flashcards = []
            for card in flashcards:
                if isinstance(card, dict) and "question" in card and "answer" in card:
                    validated_flashcards.append({
                        "question": str(card["question"]),
                        "answer": str(card["answer"])
                    })
            
            if not validated_flashcards:
                raise ValueError("没有有效的闪卡")
            
            return validated_flashcards
        
        except json.JSONDecodeError:
            # 如果直接解析失败，尝试提取 JSON 部分
            import re
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                try:
                    flashcards = json.loads(json_match.group(0))
                    return self._parse_flashcards(json_match.group(0))
                except:
                    pass
            
            raise Exception("无法解析 LLM 返回的内容为有效的闪卡格式")
