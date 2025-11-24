Domos Email Assistant — Backend Engineering Assignment

An AI-powered email assistant for property management that connects to an email inbox, reads unread messages, extracts tenant/unit context, generates intelligent replies using OpenAI, and triggers workflow actions such as maintenance tickets or lockout requests.

The system is fully asynchronous and supports concurrency for efficient email processing.

## 🚀 Features

- Async IMAP & SMTP (supports concurrent processing)
- Email parsing (subject, body, sender)
- Tenant & unit context loading from mock datastore
- Fully asynchronous LLM-powered reply generator using OpenAI
- Intent classification (locked_out, maintenance, rent, general)
- Workflow engine generating action tickets & saving them to JSON
- Concurrency limiting (Semaphore-based)

## ⚙️ Setup & Run Instructions
1. Clone the repository
git clone https://github.com/nikolasil/domos-assignment.git
cd domos-assignment

3. Install dependencies
pip install -r requirements.txt

4. Create a .env file
cp .env.example .env

5. Run the assistant
python main.py

The system will:

- Poll for emails
Defaults:
    - concurrency=2 (emails handled concurrently)
    - polling=2s interval
    - max_retries=2 per email
    - unread_days_back=1
- Generates asynchronous LLM replies
- Create workflow action tickets

Tickets are saved under:
output/*.json

📌 Assumptions

- Tenant and unit data is mocked and stored in .json files.
- LLM response format is forced into JSON
- Context lookup is based on SENDER EMAIL.

## ⚠️ Known Limitations / Tradeoffs

1. **IMAP is partially async**  
   While `aioimaplib` is async, some IMAP operations (especially search and fetch) may internally rely on sync calls due to library limitations.

2. **SMTP is fully async**  
   Using `aiosmtplib` provides true async sending, but network errors are logged and no retry/backoff is implemented.

3. **LLM call is fully asynchronous**
    AsyncOpenAI ensures non-blocking requests, with concurrent execution support.

4. **No persistence layer**  
   Tickets and logs are still stored as JSON files, not in a database.

6. **No conversation history**  
   The LLM receives only single-email context + tenant/unit info

## Given additional development time, I would implement:

### 🚀 Product / Infrastructure

- Full Gmail OAuth (instead of passwords / app passwords)
- Dockerization
- Web dashboard to view tickets, logs, and email threads
- Postgres persistence for emails and workflows
- Prometheus metrics

### ⚙️ Backend / Code Quality

- Unit tests & integration tests (pytest)
- Retry & backoff strategy for IMAP/SMTP/LLM
- Add internal event bus (Redis)

### 🤖 AI Enhancements

- Embedding-based similarity search for conversation history
- Fine-tuning or RAG prompts for more consistent replies
- Evaluation metrics ("response correctness", "hallucination score")

### 🤖 AI Notes

Used ChatGPT (GPT-4/GPT-5) for architecture planning, async design, prompt design, and refactoring guidance.

AI assisted with:

- Designing the modular folder structure
- Constructing async patterns (semaphores, task spawning, executors)
- Building workflow abstractions
- Creating prompt formats for structured JSON
- Refining error handling and logging
- Improving system robustness and readability

What worked well

- Iterating on architecture and async concurrency model
- Generating high-quality boilerplate while focusing on core logic
- Snippets for emails (IMAP search etc)

Challenges

- IMAP & SMTP async libraries
- Maintaining clean async patterns while mixing sync libraries
- Ensuring LLM always returns valid JSON (needed careful prompting)
- Ensuring the LLM email answer was correct