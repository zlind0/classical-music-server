import json
from typing import Dict, Any, List, Optional
from openai import AsyncOpenAI
from app.core.config import settings

class LLMService:
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_API_BASE
        )

    async def extract_metadata(self, raw_metadata: Dict[str, Any], file_path: str) -> Dict[str, Any]:
        """Uses LLM to extract advanced classical music metadata."""
        prompt = f"""
Analyze the following music file info and extract classical music metadata.
File Path: {file_path}
ID3/Tags: {json.dumps(raw_metadata.get('tags', {}), ensure_ascii=False)}

请输出一个包含以下字段的 JSON 对象：

    composer：作曲家的为人熟悉的名字（例如莫扎特、贝多芬、马勒、门德尔松）。
    work_title：作品标题（例如：第五交响曲）。
    key：调性（例如：C 小调）。
    catalog：目录编号（例如：Op. 67、K. 550、BWV 232）。
    work_type：作品类型（交响曲、协奏曲、奏鸣曲等）。
    era：时期，选自 [文艺复兴、巴洛克、古典主义、浪漫主义、现代、后现代]。
    mood：情绪，选自 [欢快/明亮、悲伤/忧郁、愤怒/激烈、平静/沉思、神秘/朦胧、辉煌/庄严、俏皮/轻快]。
    movement_title：乐章标题（如适用）。
    movement_number：乐章编号。
    summary：作品或歌词的简要概述（如适用）。

请确保输出为有效的 JSON 格式，字段名使用英文，而内容使用中文。
        """

        response = await self.client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are an expert in classical music and metadata extraction."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )

        result = json.loads(response.choices[0].message.content)
        
        # Generate canonical string
        canonical = f"Composer: {result.get('composer')} | Title: {result.get('work_title')}"
        if result.get('key'):
            canonical += f" in {result.get('key')}"
        if result.get('catalog'):
            canonical += f" | Catalog: {result.get('catalog')}"
        if result.get('work_type'):
            canonical += f" | Type: {result.get('work_type')}"
        if result.get('era'):
            canonical += f" | Era: {result.get('era')}"
        
        result["canonical_string"] = canonical
        return result

    async def get_embedding(self, text: str) -> List[float]:
        """Generates embedding for semantic search."""
        response = await self.client.embeddings.create(
            model=settings.EMBEDDING_MODEL,
            input=text
        )
        return response.data[0].embedding

llm_service = LLMService()
