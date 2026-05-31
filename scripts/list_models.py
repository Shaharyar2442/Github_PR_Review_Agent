import asyncio
import google.generativeai as genai
from config import GEMINI_API_KEY

def list_models():
    genai.configure(api_key=GEMINI_API_KEY)
    for m in genai.list_models():
        if 'embedContent' in m.supported_generation_methods:
            print(f"Model: {m.name}")

if __name__ == "__main__":
    list_models()
