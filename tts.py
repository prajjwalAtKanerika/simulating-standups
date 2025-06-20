from gtts import gTTS
import json
import os

AUDIO_OUTPUT_DIR = "responses/audio"
PROMPTS_JSON = "data/user_prompts.json"

def text_to_speech(text: str, filename: str):
    tts = gTTS(text=text, lang='en')
    tts.save(filename)

def generate_prompt_audio():
    os.makedirs(AUDIO_OUTPUT_DIR, exist_ok=True)

    with open(PROMPTS_JSON, "r") as f:
        prompts = json.load(f)

    for p in prompts:
        filename = f"{AUDIO_OUTPUT_DIR}/{p['action_id']}.mp3"
        text_to_speech(p["prompt"], filename)
        print(f"🔊 Saved audio: {filename}")

    print("✅ All prompts converted to audio.")

if __name__ == "__main__":
    generate_prompt_audio()
