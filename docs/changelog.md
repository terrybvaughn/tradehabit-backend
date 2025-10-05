# TradeHabit Changelog

This changelog documents significant updates to the TradeHabit codebase and documentation.  
It is intended for developers, collaborators, and system integrators to understand what has changed, when, and why.


## Template for Future Entries

Use the format below for each new entry:

## [YYYY-MM-DD] <Summary of Change>

<Short description of what changed and why>

**Updated:**
- <filename.md> — <1-line summary of change>

**Added:**
- <filename.md> — <1-line summary of purpose>

**Removed:**
- <filename.md> — <reason>



## [2025-10-05] TradeHabit Mentor Documentation

Comprehensive documentation added for TradeHabit Mentor, an AI-powered trading coach prototype. Mentor is a separate system (Next.js Chat UI + Flask Tool Runner + OpenAI Assistants API) that provides conversational analytics explanations, goal-setting assistance, and behavioral coaching. All existing documentation updated to acknowledge Mentor as a complementary system alongside the core analytics backend.

**Added:**
- `mentor.md` — Complete technical documentation for Mentor (architecture, data flow, function tools, prompt corpus, setup, limitations)

**Updated:**
- `api.md` — Added Mentor API section noting separate prototype status and future integration plans
- `architecture.md` — Added Mentor system diagram, architectural approach, design principles, security considerations, and performance characteristics
- `dependencies.md` — Added comprehensive Mentor dependency analysis (Next.js, React, OpenAI SDK, TypeScript, Flask, function schemas)
- `functionality.md` — Added system overview distinguishing core backend from Mentor with pointer to mentor.md
- `product-overview.md` — Updated with Mentor features for non-technical audience, revised "What Sets It Apart" and "Current Stage" sections
- `security-considerations.md` — Added extensive Mentor security analysis including critical concerns (OpenAI data transmission, no authentication, API key exposure, open CORS), vulnerabilities prioritization, production requirements, and best practices
- `setup.md` — Added complete Mentor setup guide (prerequisites, local development, OpenAI configuration, testing, troubleshooting, deployment considerations)
- `state-management.md` — Added minimal Mentor state management section (conversation state on OpenAI, tool runner cache, Chat UI React state, future persistence plans)

## [2025-07-17] Initial Knowledge Upload

Established initial documentation structure in the `/docs` directory.  
These files serve as the baseline source of truth for TradeHabit’s prototype implementation.

**Added:**
- `architecture.md` — Describes the tech stack and high-level application design.
- `functionality.md` — Summarizes implemented business logic and feature behaviors.
- `state-management.md` — Documents frontend state structure and flow using Zustand.
- `api.md` — Outlines available API endpoints, inputs/outputs, and contract expectations.
- `dependencies.md` — Lists major libraries and their roles in the codebase.
- `data-requirements.md` — Defines supported trade data formats and validation rules.
- `security-considerations.md` — Identifies current data handling practices and open risks.
- `testing-opportunities.md` — Highlights areas of the codebase needing better test coverage.
- `performance-baseline.md` — Notes performance-impacting patterns and future concerns.
- `setup.md` — Provides local and Replit-based setup instructions.
- `product-overview.md` — Describes product purpose, target users, current state, and vision.
