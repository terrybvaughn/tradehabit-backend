# PRD: "Goal" Feature for TradeHabit

## Introduction
The Goal feature enables users to track their progress toward completing a specified number of trades without committing certain types of mistakes. This feature builds on the concept of streaks (e.g., best_streak, current_streak) and allows users to see both their current and best streaks for each goal. For this first iteration, goals will be hard-coded, but the code should be designed to support future user-configurable goals. The backend will provide all necessary data; the frontend will handle presentation and notifications.

## Goals
- Implement a backend system to track multiple hard-coded goals, each defined by a title, a target number of trades, and a set of mistake types to avoid.
- For each goal, return:
  - The current streak (number of consecutive trades meeting the goal criteria)
  - The best streak ever achieved for that goal
  - The progress toward the goal as a float (0.0–1.0)
- Ensure the system is future-proof for user-defined goals and additional mistake types.

## Stories

### Story 1: Clean Trades Goal
**When** I am trying to make trades without any miskakes, **I want** to see how many consecutive trades I have completed without any mistakes, **so I can** track my progress toward a "Clean Trades" goal.
- **Acceptance Criteria:**
  - The backend returns the current and best streaks for trades with no mistakes.
  - The goal is hard-coded at 50 trades.
  - The progress value is current_streak / 50.
  - The streak resets to zero if any mistake is made.
  - Depends on: `current_streak` logic in `/api/summary` and `mistakes` in `Trade` dataclass.

### Story 2: Risk Management Goal
**When** I am trying to improve my risk management discipline, **I want** to see how many consecutive trades I have completed without "no stop-loss", "excessive risk", or "outsized loss" mistakes, **so I can** track my progress toward a "Risk Management" goal.
- **Acceptance Criteria:**
  - The backend returns the current and best streaks for trades without these mistakes.
  - The goal is hard-coded at 100 trades.
  - The progress value is current_streak / 100.
  - The streak resets to zero if any of these mistakes are made.
  - Depends on: `mistakes` in `Trade` dataclass and mistake tagging logic in `mistake_analyzer.py`.

### Story 3: Revenge Trades Goal
**When** I am trying to stop revenge trading, **I want** to see how many consecutive trades I have completed without a "revenge trade" mistake, **so I can** track my progress toward a "Revenge Trades" goal.
- **Acceptance Criteria:**
  - The backend returns the current and best streaks for trades without this mistake.
  - The goal is hard-coded at 100 trades.
  - The progress value is current_streak / 100.
  - The streak resets to zero if a "revenge trade" mistake is made.
  - Depends on: `mistakes` in `Trade` dataclass and mistake tagging logic in `mistake_analyzer.py`.

## Data Requirements
- Access to the full list of trades, each with a `mistakes` list and timestamps.
- For each goal, the backend must be able to iterate through trades in order (most recent to oldest) to calculate current and best streaks.
- Each goal is defined by:
  - `title` (string)
  - `goal` (integer)
  - `mistake_types` (list of strings)

## Intentionally Excluded
- No user interface or notification logic in the backend.
- No user-created or user-modified goals in this iteration.
- No localization or multi-language support.
- No filtering by date range or symbol in the goals endpoint.
- No return of the list of trades for each goal (handled by `/api/trades`).

## Out of Scope
- Frontend display and progress bar rendering.
- User authentication or multi-user support.

## Design Considerations
- The API response for `/api/goals` should be a list of goal objects, each with:
  - `title`
  - `goal`
  - `current_streak`
  - `best_streak`
  - `progress` (float, 0.0–1.0)

Example:
```json
[
  {
    "title": "Clean Trades",
    "goal": 50,
    "current_streak": 12,
    "best_streak": 23,
    "progress": 0.24,
  },
  {
    "title": "Risk Management",
    "goal": 100,
    "current_streak": 27,
    "best_streak": 41,
    "progress": 0.27,
  },
  {
    "title": "Revenge Trades",
    "goal": 100,
    "current_streak": 45,
    "best_streak": 60,
    "progress": 0.45,
  }
]
```

## Technical Considerations
- The calculation logic for each goal's streak should be modular and extensible for future user-defined goals.
- The `/api/goals` endpoint should be added to `app.py`.
- The logic should leverage the `mistakes` field in the `Trade` dataclass (`trade.py`).
- Mistake tagging logic in `mistake_analyzer.py` must be accurate and up-to-date.
- The code should be structured to allow for easy addition of new goals and mistake types.

## Success Metrics
- Users can see their current and best streaks for each goal on the dashboard.
- The API returns accurate streak and progress data for each goal.
- The codebase is ready for future user-defined goals and additional mistake types.

## Open Questions
- Should the API support returning additional metadata for each goal (e.g., date of best streak, last reset date) in the future? 