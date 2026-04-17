import os
import sys
import asyncio
import json

# Add parent directory to path to allow imports from 'app'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.audio_service import audio_service
from app.services.llm_service import llm_service
from app.core.config import settings

async def debug_extract(file_path: str, call_llm: bool = True):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    print(f"--- Processing File: {file_path} ---")
    
    # 1. Basic Metadata
    basic_meta = audio_service.extract_metadata(file_path)
    print("\n[Basic Metadata]")
    print(json.dumps(basic_meta, indent=2, ensure_ascii=False))

    # 2. Show Prompt
    prompt = f"""
        Analyze the following music file info and extract classical music metadata.
        File Path: {file_path}
        ID3/Tags: {json.dumps(basic_meta.get('tags', {}), ensure_ascii=False)}

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
    print("\n[LLM Prompt]")
    print(prompt)

    # 3. Call LLM (Optional)
    if call_llm:
        if not settings.OPENAI_API_KEY:
            print("\n[Warning] OPENAI_API_KEY not set. Skipping LLM call.")
        else:
            print("\n[LLM Result]")
            advanced_meta = await llm_service.extract_metadata(basic_meta, file_path)
            print(json.dumps(advanced_meta, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python extract_metadata_debug.py <file_path> [--no-llm]")
        sys.exit(1)
    
    target_file = sys.argv[1]
    should_call_llm = "--no-llm" not in sys.argv
    
    asyncio.run(debug_extract(target_file, should_call_llm))
