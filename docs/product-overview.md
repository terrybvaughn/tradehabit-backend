# TradeHabit: Product Overview

## What Is TradeHabit?

**TradeHabit** is a browser-based behavioral analytics tool designed to help traders identify costly trading mistakes using only their historical trade order data. It combines automated analytics with an AI-powered trading coach to provide both objective diagnostics and personalized guidance.

Unlike other trade journaling and analytics apps that overwhelm new traders with complicated configurations and advanced analytics, TradeHabit focuses on the root cause of poor trade performance: behavior. By focusing on trading behavior, TradeHabit provides a set of easy-to-understand diagnostic tools that enable traders to quickly identify and correct the behaviors that are affecting their performance. And by setting goals, TradeHabit enables traders to develop good trading habits that drive personal accountability, consistency and better performance.

**TradeHabit Mentor** acts as your always-on trading coach, helping you understand your analytics, prioritize improvements, and stay accountable to your goals. Mentor delivers the frank, one-to-one guidance of a seasoned trading coach without the high costs or difficulty of finding a qualified mentor.

TradeHabit is currently a prototype; not a commercial software app. It is designed to function entirely in-browser, requiring no account creation, database, or persistent storage. It is currently deployed on Replit at app.tradehab.it.


## Who Is It For?

- **Target users**: Retail futures traders, particularly those using NinjaTrader with exportable `.csv` order data
- **User profile**:
  - Beginner to intermediate level
  - Struggling with consistency, discipline, or emotional control
  - Interested in improving execution behavior, not signal generation


## What Problem Does It Solve?

Many traders:
- Repeat the same behavioral mistakes (e.g., revenge trading, early exits)
- Have no way to analyze these patterns from their own trade history
- Lack objective, data-driven feedback on their execution behavior

TradeHabit solves this by:
- Parsing trade order history files
- Detecting and labeling specific trading mistakes
- Providing insights with tagged trades, behavioral analytics and contextual explanations


## Key Features

### Core Analytics
- **File upload** (currently only supports NinjaTrader `.csv`)
- **Mistake detection engine** for:
  - Naked Trades (trades without stop-loss protection)
  - Revenge Trading
  - Excessive Risk
  - Outsized Losses
  - Risk Sizing Inconsistency
- **Trade Log**
  - Tracks individual trades
  - Flags mistakes committed per trade
- **Insights**
  - Plain English assessment of behavioral performance according to the following rubrics:
    - Stop-Loss Discipline
    - Risk Sizing (Excessive Risk Sizing)
    - Loss Consistency (Outsized Losses)
    - Revenge Trading
    - Risk Sizing Consistency
    - Win Rate vs. Payoff Ratio Analysis
- **Performance Overview**
  - Performance
  - Mistakes
  - Streaks
- **Goals**
  - For each type of mistake, set and track goals to eliminate mistakes and build discipline
- **Dashboard**
  - Interactive dashboard that presents summaries and analyses of the following:
    - Performance Overview
    - Insights
    - Goals
    - Loss Consistency Chart (Loss Dispersion Analysis)
    - Trades - a log of all trades that highlights trades flagged with mistake(s)

### TradeHabit Mentor (AI Coach)
- **Conversational analytics explanations**: Ask questions about your trading data and get clear, personalized answers
- **Mistake methodology guidance**: Understand how TradeHabit detects each type of mistake and why it matters
- **Performance insights**: Get deeper insights into behavioral patterns affecting your trading
- **Goal-setting assistance**: Help prioritizing which behaviors to work on and setting achievable goals
- **Progress accountability**: Motivational support and monitoring as you work toward your goals
- **Always-on coaching**: Available 24/7 to answer questions and provide guidance


## What Sets It Apart

- **Focused on behavior**, not P&L: no complex analytics, technical indicators or strategies
- **Objective, data-driven insights**: objective analysis based on trade data - no manual tagging or subjective interpretation, which can be prone to error
- **AI-powered coaching**: TradeHabit Mentor provides personalized guidance and explanations that help you understand and improve your trading behavior
- **Always available**: Unlike traditional mentors, get support 24/7 without scheduling, high costs, or the difficulty of finding a qualified coach


## Current Stage of Development

**Status**: Prototype

### What Works Today
- **Core Analytics**: Upload your NinjaTrader CSV and get immediate behavioral analysis
  - Runs entirely in your browser - no account needed
  - Your data never leaves your device
  - Available at app.tradehab.it
- **TradeHabit Mentor**: AI coaching prototype in development
  - Can explain analytics and provide personalized guidance
  - Answers questions about your trading behavior
  - Helps with goal-setting and accountability

### Current Limitations
- **Platform Support**: Only NinjaTrader CSV files supported (no other brokers yet)
- **Data Storage**: No data persistence - must re-upload each session
- **Feature Set**: Limited analytics depth and tracking options
- **Monitoring**: No real-time alerts or ongoing trade monitoring
- **Mentor Integration**: AI coach is separate prototype, not yet part of main app
- **Beta Software**: Both systems are prototypes undergoing active development


## Vision

TradeHabit is evolving into a personal trading behavior coach — providing custom feedback, progress tracking, and habit formation tools to help traders improve consistency and performance through better discipline and awareness.

**TradeHabit Mentor** represents the first step in this vision, bringing AI-powered coaching to help traders understand their data, prioritize improvements, and build better trading habits. As Mentor develops, it will:
- Provide increasingly personalized coaching based on individual trading styles
- Offer proactive suggestions for improvement based on detected patterns
- Help traders set and achieve progressively more challenging behavioral goals
- Track long-term habit formation and celebrate milestones

Beyond Mentor, TradeHabit will expand to:
- Support multiple trading platforms and instruments (not limited to NinjaTrader futures)
- Integrate directly with brokers (eliminating the need for CSV uploads)
- Provide real-time behavioral monitoring and feedback
- Build a comprehensive library of trading psychology resources