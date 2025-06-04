import os
import openai
import requests
from dotenv import load_dotenv

# ✅ Load environment variables from .env file
load_dotenv()

# ✅ Set your keys
openai_api_key = os.getenv("OPENAI_API_KEY")
openai_project_id = os.getenv("OPENAI_PROJECT_ID")  # NEW line
notion_token = os.getenv("NOTION_API_KEY")
notion_database_id = os.getenv("NOTION_DATABASE_ID")

# ✅ Validate environment variables
if not openai_api_key:
    raise ValueError("❌ Missing OPENAI_API_KEY")
if not openai_project_id:
    raise ValueError("❌ Missing OPENAI_PROJECT_ID")  # NEW line
if not notion_token:
    raise ValueError("❌ Missing NOTION_API_KEY")
if not notion_database_id:
    raise ValueError("❌ Missing NOTION_DATABASE_ID")

# ✅ OpenAI Client for project-based key
client = openai.OpenAI(
    api_key=openai_api_key,
    project=openai_project_id
)

# ✅ Use GPT to generate a motivational message
print("🔁 Asking GPT for your test win log...")
response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {
            "role": "user",
            "content": "Write a motivational status log for Antonio Branch launching BranchBot Codex full stack."
        }
    ]
)
message = response.choices[0].message.content
print("🧠 GPT Message:", message)

# ✅ Send to Notion
print("📤 Sending to Notion...")
notion_url = "https://api.notion.com/v1/pages"
headers = {
    "Authorization": f"Bearer {notion_token}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}
payload = {
    "parent": {"database_id": notion_database_id},
    "properties": {
        "Name": {"title": [{"text": {"content": "BranchBot Full Stack Test"}}]},
        "Category": {"rich_text": [{"text": {"content": "System Check"}}]},
        "Description": {"rich_text": [{"text": {"content": message}}]}
    }
}

res = requests.post(notion_url, headers=headers, json=payload)
if res.status_code in (200, 201):
    print("✅ Notion log created successfully.")
else:
    print("❌ Notion log failed:", res.status_code, res.text)
