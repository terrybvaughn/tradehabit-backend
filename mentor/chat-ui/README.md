# Mentor Chat UI (Local)

## Prereqs
- Node 18+
- tool_runner running on port 5000 and exposed via ngrok (copy the https URL)

## How it works
- Visit http://localhost:3000
- Frontend posts to `/api/chat` with your message.
- Server route (Next.js) uses **Assistants API** to add your message to a thread, create a run, and handle **tool calls**.
- When tools are required, it calls your **tool_runner** via `TOOL_RUNNER_BASE_URL` and submits outputs back.
- Returns the Assistant’s grounded reply.

## Notes
- This first version uses **polling** for reliability; you can add streaming later.
- Keep your `OPENAI_API_KEY` on the server only; do not expose it to the browser.