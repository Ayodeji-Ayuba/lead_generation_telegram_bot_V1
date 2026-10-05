import os

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
)

from google import genai
from handlers.qualification_handler import build_qualification_conversation_handler
from message_handler import ask_gemini, summarize_with_gemini
from services.gemini_services import create_gemini_client


async def close_gemini_client(application: Application) -> None:
    client: genai.Client | None = application.bot_data.get("gemini_client")
    if client is not None:
        await client.aio.aclose()


def main() -> None:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("Set the TELEGRAM_BOT_TOKEN environment variable before starting the bot.")
    admin_chat_id = os.getenv("TELEGRAM_ADMIN_CHAT_ID")
    if not admin_chat_id:
        raise RuntimeError(
            "Set the TELEGRAM_ADMIN_CHAT_ID environment variable to route qualified leads."
        )

    application = (
        Application.builder()
        .token(token)
        .post_shutdown(close_gemini_client)
        .build()
    )
    application.bot_data["admin_chat_id"] = admin_chat_id
    application.bot_data["gemini_model"] = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if gemini_api_key:
        application.bot_data["gemini_client"] = create_gemini_client(gemini_api_key)

    application.add_handler(CommandHandler("ask", ask_gemini))
    application.add_handler(CommandHandler("summarize", summarize_with_gemini))
    application.add_handler(build_qualification_conversation_handler())
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
