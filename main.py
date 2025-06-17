import time
import requests

NOTION_TOKEN = "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"
TIMER_DB_ID = "1e7c9afdd53b809bbbe3d6aafae6fdc6"
TARGET_DB_ID = "1fcc9afdd53b80948663de3af2f442c3"

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

def get_new_timer_entries():
    url = f"https://api.notion.com/v1/databases/{TIMER_DB_ID}/query"
    payload = {
        "filter": {
            "and": [
                {"property": "Státusz", "select": {"equals": "Elindítva"}},
                {"property": "Vágók", "relation": {"is_empty": True}}
            ]
        }
    }
    res = requests.post(url, headers=HEADERS, json=payload)
    return res.json().get("results", [])

def get_target_page_by_person(person_name):
    url = f"https://api.notion.com/v1/databases/{TARGET_DB_ID}/query"
    payload = {
        "filter": {
            "property": "Person",
            "rich_text": {"equals": person_name}
        }
    }
    res = requests.post(url, headers=HEADERS, json=payload)
    results = res.json().get("results", [])
    return results[0]["id"] if results else None

def update_timer_relation(timer_page_id, target_page_id):
    url = f"https://api.notion.com/v1/pages/{timer_page_id}"
    payload = {
        "properties": {
            "Kapcsolódó feladat": {
                "relation": [{"id": target_page_id}]
            }
        }
    }
    res = requests.patch(url, headers=HEADERS, json=payload)
    return res.status_code == 200

def main():
    new_entries = get_new_timer_entries()
    print(f"🔍 Új bejegyzések száma: {len(new_entries)}")
    for entry in new_entries:
        props = entry["properties"]
        timer_page_id = entry["id"]
        try:
            person = props["Person"]["rich_text"][0]["plain_text"]
        except (KeyError, IndexError):
            print("❌ Person mező üres vagy hiányzik.")
            continue

        target_id = get_target_page_by_person(person)
        if target_id:
            success = update_timer_relation(timer_page_id, target_id)
            print("✅ Kapcsolva:", person) if success else print("⚠️ Nem sikerült kapcsolni.")
        else:
            print("❌ Nem találtam feladatot:", person)

# 🚀 Végtelen ciklus, 30mp-es újrafutással
while True:
    main()
    time.sleep(300)
