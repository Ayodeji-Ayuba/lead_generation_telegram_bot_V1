from decimal import Decimal

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from qualification import parse_budget, qualify_lead

NAME, COMPANY, PROJECT, BUDGET, TIMELINE = range(5)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    await update.message.reply_text(
        "Hi! I’ll ask a few questions to see whether we’re a good fit for your project.\n"
        "You can type /cancel at any time.\n\n"
        "First, what’s your name?"
    )
    return NAME


async def collect_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["name"] = update.message.text.strip()
    await update.message.reply_text("What’s your company or organization called?")
    return COMPANY


async def collect_company(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["company"] = update.message.text.strip()
    await update.message.reply_text("What would you like us to build? Please describe the project.")
    return PROJECT


async def collect_project(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["project_type"] = update.message.text.strip()
    await update.message.reply_text(
        "What’s your approximate budget? Enter one amount, for example $2,000."
    )
    return BUDGET


async def collect_budget(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        context.user_data["budget"] = parse_budget(update.message.text)
    except ValueError as error:
        await update.message.reply_text(f"{error} Please try again.")
        return BUDGET

    keyboard = [["Within 1 month", "1–3 months"], ["3–6 months", "More than 6 months"]]
    await update.message.reply_text(
        "When would you like to get started?",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True),
    )
    return TIMELINE


async def collect_timeline(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["timeline"] = update.message.text.strip()
    lead = context.user_data
    result = qualify_lead(
        budget=lead["budget"],
        timeline=lead["timeline"],
        project_type=lead["project_type"],
        company=lead["company"],
        name=lead["name"],
    )
    budget: Decimal = lead["budget"]

    if result.status == "Not qualified":
        response = (
            f"Thanks, {lead['name']}! Your project qualification score is "
            f"{result.score}/100. Based on the budget you shared (${budget:,.0f}), "
            "we may not be the right fit at this time. You’re welcome to reach out "
            "again if your project budget changes."
        )
    else:
        await context.bot.send_message(
            chat_id=context.bot_data["admin_chat_id"],
            text=(
                f"{result.status} — qualification score: {result.score}/100\n"
                f"Name: {lead['name']}\n"
                f"Company: {lead['company']}\n"
                f"Project: {lead['project_type']}\n"
                f"Budget: ${budget:,.2f}\n"
                f"Timeline: {lead['timeline']}"
            ),
        )
        response = (
            f"Thanks, {lead['name']}! Your project qualification score is "
            f"{result.score}/100 — {result.status.lower()}.\n"
            "I’ve shared your project details with our team so they can follow up."
        )

    await update.message.reply_text(response, reply_markup=ReplyKeyboardRemove())
    context.user_data.clear()
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    await update.message.reply_text(
        "No problem — your answers have been cleared. Send /start whenever you’re ready.",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END


def build_qualification_conversation_handler() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, collect_name)],
            COMPANY: [MessageHandler(filters.TEXT & ~filters.COMMAND, collect_company)],
            PROJECT: [MessageHandler(filters.TEXT & ~filters.COMMAND, collect_project)],
            BUDGET: [MessageHandler(filters.TEXT & ~filters.COMMAND, collect_budget)],
            TIMELINE: [MessageHandler(filters.TEXT & ~filters.COMMAND, collect_timeline)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True,
    )
