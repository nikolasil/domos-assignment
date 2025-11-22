import json
import logging

from openai import OpenAI
from config.settings import settings
from core.models import LLMResponse

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class LLMClient:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def generate_response(self, email, context) -> LLMResponse:
        """
        Sends email + context to the model and expects structured JSON output.
        """

        system_prompt = """
You are an AI assistant for a property management company.
Your job is to read tenant emails and provide a professional, helpful response.

Instructions:
1. Understand the tenant's request fully.
2. Use the provided context to enhance your reply.
3. Generate a clear, concise, human-sounding response.
4. Determine the intent of the email.
5. List any action items needed.

Output JSON ONLY in the following schema:
{
  "reply": "<string>",                # The text to send back to the tenant
  "intent": "<locked_out | maintenance | rent | general>",
  "action_items": [
      { "type": "<string>", "details": "<string>" }
  ]
}

Rules:
- "locked_out": if tenant is locked out of property.
- "maintenance": if tenant mentions repairs, broken items, or issues needing attention.
- "rent": if tenant asks about rent, payment, or balance.
- "general": for anything else.
- action_items must be [] if no action is required.
- Always return valid JSON only, no extra commentary or text outside JSON.
- Keep replies professional, polite, and helpful.
"""

        user_prompt = f"""
EMAIL RECEIVED:
Subject: {email.subject}
From: {email.sender}
Body: {email.body}

CONTEXT:
{json.dumps(context, indent=2)}

RULES:
- Do NOT hallucinate information. If you don't know something, leave it blank or empty string.
- action_items = [] if no action is required.
- Always return valid JSON ONLY. No commentary, no greetings, no signatures.
- Do NOT use placeholders like [insert amount here] or $[Your Name].
- Keep replies professional, polite, and helpful.
- Use the data in CONTEXT to have a more full response. Those data are related to the person sending the mail.
"""

        try:
            completion = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt.strip()},
                    {"role": "user", "content": user_prompt.strip()},
                ],
                temperature=0.2,
            )

            raw = completion.choices[0].message.content
            data = json.loads(raw)
            return LLMResponse(**data)

        except json.JSONDecodeError:
            logger.warning("LLM returned invalid JSON. Raw output:\n%s", raw)
        except Exception as e:
            logger.error("LLM error: %s", e)

        # Fallback response
        return LLMResponse(
            reply="Sorry, something went wrong while generating a response.",
            intent="general",
            action_items=[]
        )
