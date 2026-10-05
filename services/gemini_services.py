from google import genai
from google.genai.errors import APIError


class GeminiServiceError(RuntimeError):
    """Raised when Gemini returns no usable text."""


def create_gemini_client(api_key: str) -> genai.Client:
    if not api_key.strip():
        raise ValueError("Gemini API key must not be empty.")
    return genai.Client(api_key=api_key)


async def chat_reply(client: genai.Client, message: str, model: str) -> str:
    prompt = message.strip()
    if not prompt:
        raise ValueError("Message must not be empty.")

    response = await client.aio.models.generate_content(model=model, contents=prompt)
    return _response_text(response.text)


async def summarize_text(client: genai.Client, text: str, model: str) -> str:
    source = text.strip()
    if not source:
        raise ValueError("Text to summarize must not be empty.")

    response = await client.aio.models.generate_content(
        model=model,
        contents=f"Summarize the following text clearly and concisely:\n\n{source}",
    )
    return _response_text(response.text)


def _response_text(text: str | None) -> str:
    if text is None or not text.strip():
        raise GeminiServiceError("Gemini returned an empty response.")
    return text.strip()
