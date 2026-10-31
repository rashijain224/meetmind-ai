import os
from dotenv import load_dotenv
from notion_client import Client

load_dotenv()

notion = Client(auth=os.getenv("NOTION_TOKEN"))

DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

def create_notion_task(task, owner, deadline, priority, meeting_title):

    properties = {"Task": {"title": [{"text": {"content": task}}
            ]},
        "Owner": {
            "rich_text": [
                {"text": {"content": owner}}]},
        "Priority": {
            "select": {"name": priority}},
        "Source Meeting": {"rich_text": [{"text": {"content": meeting_title}}]}}

    if deadline and deadline != "Unknown":properties["Deadline"] = {"date": {"start": deadline}}

    return notion.pages.create(parent={"database_id": DATABASE_ID},properties=properties)