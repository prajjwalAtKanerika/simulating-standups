import os
import logging
from deepgram.utils import verboselogs
from deepgram import (
    DeepgramClient,
    SpeakOptions,
)
SPEAK_TEXT = {"text": "[19556] Abhi is working on the test epic and he has started with testing of one feature which was not tested before. He will be doing some more work after that to complete it. The next step would be to do regression tests as well so we can have confidence about our code quality. We are also going through all the features from scratch again now since there were no changes made during sprints"}
filename = "test.mp3"
def generateAudio():
    try:
        # STEP 1 Create a Deepgram client using the API key from environment variables
        deepgram = DeepgramClient()
        # STEP 2 Call the save method on the speak property
        options = SpeakOptions(
            model="aura-2-thalia-en",
        )
        response = deepgram.speak.rest.v("1").save(filename, SPEAK_TEXT, options)
        print(response.to_json(indent=4))
    except Exception as e:
        print(f"Exception: {e}")

generateAudio()

# prompt_text = "Ticket 19558 is now done. QA is complete and it's moving to deployment."
# text_to_speech_deepgram(prompt_text, output_path="standup_ticket_19558.wav")