"""
CricketIQ X - Gemini API Client
Central client used by all Gemini modules.
"""

import google.generativeai as genai
from app.core.config import get_settings

_client_initialized = False

def get_gemini_client():
    global _client_initialized
    settings = get_settings()

    if not settings.GEMINI_API_KEY or settings.GEMINI_API_KEY == "your_gemini_api_key_here":
        raise ValueError("GEMINI_API_KEY not set in .env file")

    if not _client_initialized:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        _client_initialized = True

    return genai.GenerativeModel(
        model_name="gemini-2.0-flash",
        generation_config={
            "temperature":      0.3,
            "top_p":            0.95,
            "max_output_tokens":1000,
        }
    )


CSK_SYSTEM_PROMPT = """You are an expert IPL cricket analyst working exclusively for
Chennai Super Kings. Always advise from CSK's perspective.
Use only the structured data provided — never invent statistics.
Be specific and tactical. When recommending a delivery, name the exact type.
When recommending a field, name exact positions.
Keep answers concise and under 150 words unless a detailed breakdown is requested."""


def ask_gemini(prompt: str, system_context: str = "") -> str:
    """
    Send a prompt to Gemini and return the text response.
    Falls back to a placeholder if API key is not set.
    """
    try:
        model    = get_gemini_client()
        full_prompt = f"{CSK_SYSTEM_PROMPT}\n\n{system_context}\n\n{prompt}" if system_context else f"{CSK_SYSTEM_PROMPT}\n\n{prompt}"
        response = model.generate_content(full_prompt)
        return response.text.strip()
    except ValueError as e:
        return f"[Gemini not configured: {e}]"
    except Exception as e:
        return f"[Gemini error: {str(e)[:100]}]"