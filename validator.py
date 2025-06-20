import os
import json
import re
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-02-15-preview",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

DEPLOYMENT_NAME = "gpt-4o-mini"  # Or your deployed model

def validate_response(action_item: str, response_text: str) -> str:
    prompt = (
        f"You are a helpful Scrum Assistant.\n"
        f"An action item was assigned during a previous stand-up:\n"
        f"Action Item: \"{action_item}\"\n"
        f"User responded:\n\"{response_text}\"\n\n"
        f"Does this indicate completion, progress, or is it unclear?\n"
        f"Respond with only one of these: ✅ Completed, 🕐 In Progress, ❌ Unclear"
    )

    try:
        result = client.chat.completions.create(
            model=DEPLOYMENT_NAME,
            messages=[
                {"role": "system", "content": "You are a helpful assistant who classifies Agile updates."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=20
        )
        return result.choices[0].message.content.strip()
    except Exception as e:
        return f"[ERROR] {str(e)}"

def split_action_items(text: str) -> list:
    return re.findall(r"(?:\d+\.\s+|\*\*|\n)(.*?)(?=\n\d+\.|\n\*\*|$)", text, re.DOTALL)

def validate_all_responses(
    action_items_path="data/action_items.json",
    responses_path="responses/member_responses/member_responses.json",
    output_path="responses/validation_results.json"
):
    with open(action_items_path, "r") as f:
        action_items = json.load(f)

    with open(responses_path, "r") as f:
        member_responses = json.load(f)

    results = []

    for item in action_items:
        ticket_id = item["ticket_id"]
        assigned_to = item["assigned_to"]
        action_list = split_action_items(item["action_items"])

        for idx, action_item in enumerate(action_list, 1):
            action_id = f"{ticket_id}-{idx}"
            response_text = member_responses.get(action_id)

            if not response_text:
                print(f"❗ No response found for {action_id}. Skipping.")
                continue

            print(f"🔍 Validating response for {action_id}...")
            validation = validate_response(action_item.strip(), response_text.strip())

            results.append({
                "ticket_id": ticket_id,
                "action_id": action_id,
                "assigned_to": assigned_to,
                "action_item": action_item.strip(),
                "response": response_text.strip(),
                "validation": validation
            })

    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)

    print(f"✅ Validation results saved to: {output_path}")

if __name__ == "__main__":
    validate_all_responses()
