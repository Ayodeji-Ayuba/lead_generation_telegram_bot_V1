# Telegram Lead Qualification Bot

A Telegram bot that collects a potential client's name, company, project description, budget, and timeline, then returns a qualification score.
Optional Gemini commands provide an AI chat reply and summarize text explicitly submitted with a command.

## Requirements

- Python 3.10 or newer
- A Telegram bot token from [@BotFather](https://t.me/BotFather)

## Setup

1. Create and activate a virtual environment:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

2. Install dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

3. Set your bot token and the Telegram chat ID that should receive qualified leads:

   ```powershell
   $env:TELEGRAM_BOT_TOKEN = "your_telegram_bot_token"
   $env:TELEGRAM_ADMIN_CHAT_ID = "your_admin_chat_id"
   $env:GEMINI_API_KEY = "your_gemini_api_key"
   $env:GEMINI_MODEL = "gemini-2.5-flash"
   ```

4. Start the bot:

   ```powershell
   python bot.py
   ```

The destination chat must be reachable by the bot (for a private admin chat, open the bot and send it `/start` first). Open your bot in Telegram and send `/start`. Use `/cancel` to end a conversation. Qualified and hot leads are sent to the configured admin chat; leads below the budget threshold are not forwarded.

Gemini is optional. When `GEMINI_API_KEY` is configured, use `/ask your question` for an AI response or `/summarize text to summarize` to summarize text. These commands send only the text you provide to Gemini; lead qualification itself is deterministic and does not send lead details to Gemini. Without the key, the qualification flow still works and the AI commands explain how to enable Gemini.

## Qualification score

The status is based on budget: under $500 is **Not qualified**, $500–$1,999.99 is **Qualified**, and $2,000 or more is a **Hot lead**.

The score is out of 100: budget contributes up to 50 points, timeline up to 25, project detail up to 15, and name and company contribute 5 points each. The budget thresholds and scoring are defined in `qualification.py`.

## Tests

Run the qualification tests with:

```powershell
python -m unittest discover -s tests
```
