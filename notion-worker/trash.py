import requests
import json

NOTION_API_URL = "https://api.notion.com/v1/"
NOTION_TOKEN = "secret_pvaGGjmtgix2XU8MlKJpFoAUEjUgiR6CNW7s5av7FCI"
PAGE_ID = "dd54994d407b4721bee88ff3f038b247"

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2021-08-16"
}


def get_page_content(page_id):
    url = f"{NOTION_API_URL}blocks/{page_id}/children"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to retrieve page content: {response.status_code}")
        return None


def save_to_file(content, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(content, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    content = get_page_content(PAGE_ID)
    if content:
        save_to_file(content, "notion_page_content.json")
