import os
import json
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()

# Use the new AzureOpenAI client
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-02-15-preview",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

DEPLOYMENT_NAME = "gpt-4o-mini"  # Replace with your actual Azure deployment name

def extract_action_items(ticket) -> str:
    prompt = (
        f"Given the following Agile ticket, generate 1-3 clear, concise action items "
        f"that would be discussed during a stand-up. Include assignee if known.\n\n"
        f"Title: {ticket['title']}\n"
        f"State: {ticket['state']}\n"
        f"Assigned To: {ticket['assigned_to']}\n"
        f"Comments:\n" + "\n".join(f"- {c}" for c in ticket.get("comments", [])) +
        "\n\nAction Items:"
    )

    try:
        response = client.chat.completions.create(
            model=DEPLOYMENT_NAME,
            messages=[
                {"role": "system", "content": "You are an assistant that creates clear action items from Agile updates."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4,
            max_tokens=250,
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"[ERROR] {e}"

def run_summary_pipeline(json_path: str = "data/data.json"):
    with open(json_path, "r") as f:
        tickets = json.load(f)

    action_items = []
    for ticket in tickets:
        items = extract_action_items(ticket)
        action_items.append({
            "ticket_id": ticket["ticket_id"],
            "assigned_to": ticket["assigned_to"],
            "action_items": items
        })

    with open("data/action_items.json", "w") as f:
        json.dump(action_items, f, indent=2)

    print("✅ Action items extracted to: data/action_items.json")

if __name__ == "__main__":
    run_summary_pipeline()
