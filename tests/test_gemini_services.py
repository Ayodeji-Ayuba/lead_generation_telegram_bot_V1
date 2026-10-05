import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock

from services.gemini_services import (
    GeminiServiceError,
    chat_reply,
    create_gemini_client,
    summarize_text,
)


class GeminiServiceTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.generate_content = AsyncMock(return_value=SimpleNamespace(text="  Gemini response  "))
        self.client = SimpleNamespace(
            aio=SimpleNamespace(
                models=SimpleNamespace(generate_content=self.generate_content)
            )
        )

    async def test_chat_reply_uses_async_client_and_trims_response(self):
        response = await chat_reply(self.client, "  Hello  ", "test-model")

        self.assertEqual(response, "Gemini response")
        self.generate_content.assert_awaited_once_with(
            model="test-model",
            contents="Hello",
        )

    async def test_summarize_text_uses_summary_instruction(self):
        response = await summarize_text(self.client, "  Long text  ", "test-model")

        self.assertEqual(response, "Gemini response")
        self.generate_content.assert_awaited_once_with(
            model="test-model",
            contents="Summarize the following text clearly and concisely:\n\nLong text",
        )

    async def test_empty_model_response_is_reported(self):
        self.generate_content.return_value = SimpleNamespace(text=" ")

        with self.assertRaises(GeminiServiceError):
            await chat_reply(self.client, "Hello", "test-model")

    async def test_empty_inputs_are_rejected_before_calling_gemini(self):
        with self.assertRaises(ValueError):
            await chat_reply(self.client, " ", "test-model")
        with self.assertRaises(ValueError):
            await summarize_text(self.client, " ", "test-model")

        self.generate_content.assert_not_awaited()


class GeminiClientTests(unittest.TestCase):
    def test_empty_api_key_is_rejected(self):
        with self.assertRaises(ValueError):
            create_gemini_client(" ")


if __name__ == "__main__":
    unittest.main()
