import os
import json
import sys
import argparse
from typing import List, Dict

from langchain_core.exceptions import OutputParserException
from langchain.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from ai.structure import Structure
from ai.llm import get_llm
from to_notion.upload import upload_to_notion


def enhance_papers(papers: List[Dict]) -> List[Dict]:
    """
    使用 LLM 增强论文信息。

    Args:
        papers: 从爬虫获取的论文列表。

    Returns:
        增强后的论文列表。
    """
    model_name = os.environ.get("LLM_MODEL_NAME", 'gemini-1.5-flash')
    api_key = os.environ.get("LLM_API_KEY")
    base_url = os.environ.get("LLM_BASE_URL")
    language = os.environ.get("LANGUAGE", 'Chinese')

    if not api_key:
        raise ValueError("LLM_API_KEY 环境变量未设置")

    # 按ID去重，但保留关键词信息
    id_to_keywords = {}
    unique_papers = []
    for paper in papers:
        if paper['id'] not in id_to_keywords:
            id_to_keywords[paper['id']] = []
            unique_papers.append(paper)

        if 'keyword' in paper and paper['keyword']:
            if paper['keyword'] not in id_to_keywords[paper['id']]:
                id_to_keywords[paper['id']].append(paper['keyword'])

    for paper in unique_papers:
        paper['keywords'] = id_to_keywords[paper['id']]

    llm = get_llm(model_name, api_key, base_url).with_structured_output(
        Structure, method="function_calling")
    print(f'Connect to: {model_name}', file=sys.stderr)

    system_template = open("ai/system.txt", "r", encoding="utf-8").read()
    human_template = open("ai/template.txt", "r", encoding="utf-8").read()

    prompt_template = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(system_template),
        HumanMessagePromptTemplate.from_template(template=human_template)
    ])

    chain = prompt_template | llm

    enhanced_papers = []
    for idx, paper in enumerate(unique_papers):
        try:
            response: Structure = chain.invoke({
                "language": language,
                "title": paper['title'],
                "summary": paper['summary']
            })
            paper['AI_summary'] = response.model_dump()
            enhanced_papers.append(paper)
        except OutputParserException as e:
            print(f"{paper['id']} has an error: {e}", file=sys.stderr)
            paper['AI_summary'] = {
                "tldr": "Error",
                "motivation": "Error",
                "method": "Error",
                "result": "Error",
                "conclusion": "Error"
            }
            enhanced_papers.append(paper)

        print(f"Finished {idx + 1}/{len(unique_papers)}", file=sys.stderr)

    # Upload to Notion
    notion_api_key = os.environ.get("NOTION_API_KEY")
    notion_database_id = os.environ.get("NOTION_DATABASE_ID")

    if not notion_api_key:
        print("Error: NOTION_API_KEY environment variable not set. Skipping Notion upload.", file=sys.stderr)
    elif not notion_database_id:
        print("Error: NOTION_DATABASE_ID environment variable not set. Skipping Notion upload.", file=sys.stderr)
    else:
        print("Uploading enhanced papers to Notion...", file=sys.stderr)
        upload_to_notion(enhanced_papers, notion_api_key, notion_database_id)

    return enhanced_papers

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Enhance paper data with LLM and upload to Notion.")
    parser.add_argument("--data", type=str, required=True, help="Path to the JSONL data file.")
    args = parser.parse_args()

    papers_data = []
    with open(args.data, 'r', encoding='utf-8') as f:
        for line in f:
            papers_data.append(json.loads(line))

    enhance_papers(papers_data)