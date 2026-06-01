import requests
from io import BytesIO
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")

def transcrever_audio_wpp(audio_id):

    headers = {
        "Authorization": f"Bearer {VERIFY_TOKEN}"
    }

    url = f"https://graph.facebook.com/v19.0/{audio_id}"
    res = requests.get(url, headers=headers)
    audio_url = res.json().get("url")

    if not audio_url:
        raise Exception("Erro ao obter URL do audio")
    
    audio_res = requests.get(audio_url, headers=headers)
    audio_bytes = BytesIO(audio_res.content)

    transcription = client.audio.transcriptions.create(
        model="gpt-4o-transcribe",
        file=("audio.ogg", audio_bytes)
    )
    return transcription.text