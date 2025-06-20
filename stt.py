import whisper
import os

AUDIO_DIR = "audio"
RESPONSE_AUDIO_DIR = "responses/audio"
TRANSCRIPTS_DIR = "responses/transcripts"

def transcribe_audio(file_path):
    model = whisper.load_model("base")  # You can use "tiny", "small", "base", "medium", or "large"
    result = model.transcribe(file_path)
    return result["text"]

def transcribe_all_responses():
    os.makedirs(TRANSCRIPTS_DIR, exist_ok=True)

    for file in os.listdir(RESPONSE_AUDIO_DIR):
        if file.endswith(".mp3") or file.endswith(".wav"):
            audio_path = os.path.join(RESPONSE_AUDIO_DIR, file)
            print(f"🎧 Transcribing: {file}")
            text = transcribe_audio(audio_path)

            transcript_file = os.path.join(TRANSCRIPTS_DIR, f"{file}.txt")
            with open(transcript_file, "w") as f:
                f.write(text)
            print(f"📝 Saved transcript: {transcript_file}")

if __name__ == "__main__":
    transcribe_all_responses()
