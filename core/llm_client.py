import json
import logging
from openai import AsyncOpenAI
from config.settings import settings
from core.models import LLMResponse
from core.models import Intent

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s")


class LLMClient:
    SYSTEM_PROMPT = """
You are an assistant for a property management company.
Read tenant emails and provide a professional, helpful response.

Rules:
1. Understand the tenant's request fully.
2. Use the provided context to enhance your reply.
3. Generate a clear, concise, human-sounding response.
4. Determine the intent of the email (locked_out, maintenance, rent, general).
5. List any action items needed.
6. NEVER reveal that you are an AI.
7. Output **strict JSON only**, no extra text, no greetings, no commentary.

Output JSON schema:
{
  "reply": "<string>",
  "intent": "<locked_out | maintenance | rent | general>",
  "action_items": [
      { "type": "<string>", "details": "<string>" }
  ]
}

Intent rules:
- "locked_out": tenant is locked out of property. Action required.
- "maintenance": tenant mentions repairs or issues. Action required.
- "rent": tenant asks about rent or payment. Action may be required.
- "general": anything else. Action may be optional.

Rules for action_items:
- Provide a list of actionable tasks if needed
- Leave empty list [] if no action required
- Always provide concrete action items if the email implies a task.
- Use structured tasks: "type" = short identifier, "details" = clear description.

Examples:

Example 1:
Email: "I locked myself out of my apartment."
Output:
{
  "reply": "I understand that you are locked out. We are arranging access immediately.",
  "intent": "locked_out",
  "action_items": [
    { "type": "call_locksmith", "details": "Call locksmith to provide access to tenant" }
  ]
}

Example 2:
Email: "The heating is broken in my apartment."
Output:
{
  "reply": "Thank you for reporting the heating issue. We will send a technician as soon as possible.",
  "intent": "maintenance",
  "action_items": [
    { "type": "assign_technician", "details": "Send technician to repair heating" }
  ]
}

Example 3:
Email: "I need information about my rent payment."
Output:
{
  "reply": "You can pay your rent via your online account or contact us for assistance.",
  "intent": "rent",
  "action_items": []
}

Example 4:
Email: "I just wanted to say thank you."
Output:
{
  "reply": "You're welcome! We are happy to help.",
  "intent": "general",
  "action_items": []
}
""".strip()

    USER_PROMPT_TEMPLATE = """
EMAIL RECEIVED:
Subject: {subject}
From: {sender}
Body: {body}

CONTEXT:
{context_json}
""".strip()

    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def generate_response_async(self, email, context) -> LLMResponse:
        """
        Generate LLM response asynchronously using precompiled prompts.
        """
        context_json = json.dumps(context, separators=(",", ":"), ensure_ascii=False)
        user_prompt = self.USER_PROMPT_TEMPLATE.format(
            subject=email.subject,
            sender=email.sender,
            body=email.body,
            context_json=context_json
        )

        try:
            completion = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.2,
            )

            raw = completion.choices[0].message.content
            data = json.loads(raw)

            # Convert intent string to Intent enum
            intent_value = data.get("intent", "general")
            if intent_value not in Intent.__members__:
                intent_enum = Intent.general
            else:
                intent_enum = Intent(intent_value)

            return LLMResponse(
                reply=data.get("reply", ""),
                intent=intent_enum,
                action_items=data.get("action_items", [])
            )

        except json.JSONDecodeError:
            logger.warning("LLM returned invalid JSON. Raw output:\n%s", raw)
        except Exception as e:
            logger.error("LLM error: %s", e)

        # Fallback response
        return LLMResponse(
            reply="Sorry, something went wrong while generating a response.",
            intent=Intent.general,
            action_items=[]
        )
