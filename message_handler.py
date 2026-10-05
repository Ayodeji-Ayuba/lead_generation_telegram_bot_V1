import logging

from google import genai
from google.genai.errors import APIError
from telegram import Update
from telegram.ext import ContextTypes

from services.gemini_services import GeminiServiceError, chat_reply, summarize_text

logger = logging.getLogger(__name__)


def _gemini_settings(
    context: ContextTypes.DEFAULT_TYPE,
) -> tuple[genai.Client | None, str]:
    client = context.bot_data.get("gemini_client")
    model = context.bot_data["gemini_model"]
    return client, model


async def ask_gemini(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message
    question = message.text.partition(" ")[2].strip()
    if not question:
        await message.reply_text("Usage: /ask your question")
        return

    client, model = _gemini_settings(context)
    if client is None:
        await message.reply_text("AI chat is disabled. Set GEMINI_API_KEY to enable it.")
        return

    try:
        response = await chat_reply(client, question, model)
    except (APIError, GeminiServiceError):
        logger.exception("Gemini chat request failed")
        await message.reply_text("Gemini could not answer just now. Please try again later.")
        return

    await message.reply_text(response)


async def summarize_with_gemini(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message
    source = message.text.partition(" ")[2].strip()
    if not source:
        await message.reply_text("Usage: /summarize text you want summarized")
        return

    client, model = _gemini_settings(context)
    if client is None:
        await message.reply_text("AI summaries are disabled. Set GEMINI_API_KEY to enable them.")
        return

    try:
        summary = await summarize_text(client, source, model)
    except (APIError, GeminiServiceError):
        logger.exception("Gemini summarization request failed")
        await message.reply_text("Gemini could not summarize that just now. Please try again later.")
        return

    await message.reply_text(summary)
