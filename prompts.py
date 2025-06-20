import json
import os
import re

def split_action_items(action_text: str) -> list:
    """
    Splits a string of numbered action items into a list.
    Handles bullets or numbered lists.
    """
    return re.findall(r"(?:\d+\.\s+|\*\*|\n)(.*?)(?=\n\d+\.|\n\*\*|$)", action_text, re.DOTALL)

def generate_user_prompts(action_items_path="data/action_items.json", output_path="data/user_prompts.json"):
    with open(action_items_path, "r") as f:
        data = json.load(f)

    prompts = []

    for item in data:
        assignee = item["assigned_to"]
        ticket_id = item["ticket_id"]
        action_lines = split_action_items(item["action_items"])

        for idx, action in enumerate(action_lines, 1):
            clean_action = action.strip().replace("**", "")
            prompt_text = (
                f"Hi {assignee}, in our last stand-up, you were assigned the following task:\n"
                f"\"{clean_action}\"\nCan you please give a quick update?"
            )

            prompts.append({
                "ticket_id": ticket_id,
                "assigned_to": assignee,
                "action_id": f"{ticket_id}-{idx}",
                "prompt": prompt_text
            })

    with open(output_path, "w") as f:
        json.dump(prompts, f, indent=2)

    print(f"✅ User prompts saved to: {output_path}")

if __name__ == "__main__":
    generate_user_prompts()
