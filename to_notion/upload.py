import os
import json
from typing import List, Dict
from notion_client import Client

def upload_to_notion(papers: List[Dict], notion_api_key: str, notion_database_id: str):
    notion = Client(auth=notion_api_key)

    for paper in papers:
        # Prepare properties for the Notion page
        properties = {
            "Title": {"title": [{"text": {"content": paper["title"]}}]},
            "Authors": {"rich_text": [{"text": {"content": ", ".join(paper["authors"])}}]},
            "URL": {"url": paper["abs"]},
            "Categories": {"multi_select": [{"name": cat} for cat in paper["categories"]]},
            "Summary": {"rich_text": [{"text": {"content": paper["summary"]}}]},
        }

        # Add AI enhanced fields if available
        if "AI_summary" in paper:
            if "tldr" in paper["AI_summary"]:
                properties["TLDR"] = {"rich_text": [{"text": {"content": paper["AI_summary"]["tldr"]}}]}
            if "motivation" in paper["AI_summary"]:
                properties["Motivation"] = {"rich_text": [{"text": {"content": paper["AI_summary"]["motivation"]}}]}
            if "method" in paper["AI_summary"]:
                properties["Method"] = {"rich_text": [{"text": {"content": paper["AI_summary"]["method"]}}]}
            if "result" in paper["AI_summary"]:
                properties["Result"] = {"rich_text": [{"text": {"content": paper["AI_summary"]["result"]}}]}
            if "conclusion" in paper["AI_summary"]:
                properties["Conclusion"] = {"rich_text": [{"text": {"content": paper["AI_summary"]["conclusion"]}}]}

        try:
            notion.pages.create(
                parent={"database_id": notion_database_id},
                properties=properties
            )
            print(f"Successfully uploaded '{paper['title']}' to Notion.")
        except Exception as e:
            print(f"Error uploading '{paper['title']}': {e}")