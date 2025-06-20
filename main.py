import os
import json
import time
import re
from openai import AzureOpenAI
from dotenv import load_dotenv
from gtts import gTTS
import playsound 

load_dotenv()

# Azure OpenAI client setup
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-02-15-preview",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)
DEPLOYMENT_NAME = "gpt-4o-mini" 

# Paths
ACTION_ITEMS_PATH = "data/action_items.json"
RESPONSES_PATH = "responses/member_responses/member_responses.json"
FINAL_SUMMARY_PATH = "standup_output/meeting_summary.json"
AUDIO_DIR = "standup_output/audio"

os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(os.path.dirname(FINAL_SUMMARY_PATH), exist_ok=True)

def speak(text: str, filename: str):
    """Generate and play voice prompt."""
    path = os.path.join(AUDIO_DIR, f"{filename}.mp3")
    tts = gTTS(text=text, lang='en')
    tts.save(path)
    playsound.playsound(path)

def validate_response(action_item: str, response_text: str) -> str:
    prompt = (
        f"Action Item: \"{action_item}\"\n"
        f"User responded: \"{response_text}\"\n\n"
        f"Does this indicate completion, progress, or is it unclear?\n"
        f"Respond with one of: ✅ Completed, 🕐 In Progress, ❌ Unclear"
    )
    try:
        result = client.chat.completions.create(
            model=DEPLOYMENT_NAME,
            messages=[
                {"role": "system", "content": "You are a helpful assistant validating stand-up updates."},
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

def run_standup():
    with open(ACTION_ITEMS_PATH, "r") as f:
        tickets = json.load(f)
    with open(RESPONSES_PATH, "r") as f:
        responses = json.load(f)

    final_log = []

    for ticket in tickets:
        ticket_id = ticket["ticket_id"]
        assigned_to = ticket["assigned_to"]
        action_list = split_action_items(ticket["action_items"])

        for idx, action_item in enumerate(action_list, 1):
            action_id = f"{ticket_id}-{idx}"
            action_clean = action_item.strip().replace("**", "")
            response_text = responses.get(action_id, None)

            print(f"\n🎤 Prompting {assigned_to} for action: {action_clean}")
            speak(f"Hi {assigned_to}, last time you were assigned: {action_clean}. Can you give an update?", action_id)
            print(f"response_text: {response_text}")
            time.sleep(1)

            if not response_text:
                print(f"⚠️ No response found for {action_id}. Skipping.")
                continue

            # Simulate retries if validation fails
            max_retries = 1
            for attempt in range(max_retries + 1):
                validation = validate_response(action_clean, response_text)
                print(f"🧠 Validation ({action_id}): {validation}")
                
                if validation.startswith("✅") or validation.startswith("🕐"):
                    break
                elif attempt < max_retries:
                    print(f"🔁 Response unclear. Simulating re-ask...")
                    speak("Hmm, can you clarify your update a bit more?", f"{action_id}_retry{attempt}")
                    time.sleep(1)

            final_log.append({
                "ticket_id": ticket_id,
                "action_id": action_id,
                "assigned_to": assigned_to,
                "action_item": action_clean,
                "response": response_text.strip(),
                "validation": validation
            })

    with open(FINAL_SUMMARY_PATH, "w") as f:
        json.dump(final_log, f, indent=2)

    print(f"\n✅ Stand-up simulation complete! Summary saved to: {FINAL_SUMMARY_PATH}")

if __name__ == "__main__":
    run_standup()
