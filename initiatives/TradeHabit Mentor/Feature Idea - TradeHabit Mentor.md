# Feature Idea: TradeHabit Mentor

## Problem Statment

Before reaching consistent profitability, the biggest and most important challenge for novice traders is learning how to avoid emotional trading, which can lead to greater risk-taking that can result in catastrophic losses. It is axiomatic that the most productive way for new traders to fix bad trading behaviors is to find a trading coach (also commonly referred to as a mentor) that can provide 1:1 individualized coaching to help traders identify, prioritize and fix bad trading behavior. But for the new trader, finding a reputable and effective mentor is fraught with difficulty. These are the main obstacles novice traders experience when seeking a mentor:

- **New traders lack the expertise to evaluate the quality of prospective mentors.** Moreover, public mentors tend not to advertise student outcomes and rarely provide verifiable track records, so traders cannot tell who is an effective coach that is profitable.
- **Good traders who offer mentor services are not always good coaches.** Many accomplished traders that market themselves as mentors may be highly proficient at trading, but they are not very good at educating and developing new traders. Coaching is much different than trading – it has its own skillset that requires talent and experience.
- **Misaligned incentives and attention scarcity.** Mentors that prioritize subscription revenue over student outcomes tend to enroll dozens to hundreds of students, leaving little to zero bandwidth for individualized, day-to-day feedback.
* **Reluctance to expose mistakes.** Many traders are introverted and/or feel embarrassed by their trading performance, so they avoid or postpone asking for help.
- **High costs for mentorship.** Unless in the extremely rare case that a trader has a friend that’s an accomplished trader that is willing to provide 1:1 mentorship, traders must find paid mentorships. These can cost anywhere from fifty to hundreds of dollars per month. Many traders cannot afford, or are put off by the high costs of paid mentorships. 

These challenges delay the development of novice traders, causing them to repeat costly behavioral mistakes.


## Value Proposition

TradeHabit Mentor turns your trade data into an always-on AI coach that pinpoints bad habits, sets realistic goals, and keeps you accountable. You get the frank, one-to-one guidance of a seasoned mentor without the hassle of vetting coaches or paying steep fees.


## Solution
TradeHabit Mentor (or just Mentor) is an AI chatbot and agent that will use TradeHabit outputs to provide candid, supportive and personalized guidance in the following ways:

1. Explanations of TradeHabit metrics, diagnostics and analytic methods. Goal: the user has a clear comprehension of the data, metrics and methods to assess his performance.
2. Deeper insights into a user’s trade performance: Goal: the user has a clear understanding of the problems that are plaguing his performance.
3. Help with prioritizing the user behaviors (which lead to mistakes) that need most attention. Goal: The user can prioritize the behaviors that need to be improved.
4. Assistance with prioritizing and setting goals that are calibrated to the user’s ability so that they are realistic and attainable. Goal: the user (or Mentor agent) has created goals in TradeHabit that are realistic and attainable. 
5. Motivational support and guidance to achieve goals. Goals: the user understands what he can do to correct the behavioral problems that he is trying to solve. 
6. Monitor performance against goals; highlight and correct when a user is getting off-track and ways to get the trader back on track. Goal: The user achieves the goals he has set.

The Mentor persona models an experienced trader who delivers hard truths gently, which aligns with TradeHabit’s ethos of candid, actionable feedback.

### Consumer Trust Design Implications
Trust is a retention gate. Without it, even accurate insights won't land. For any behavior-tagging or goal-setting insight, TradeHabit Mentor needs to:
- Ground claims in visible data ("Here's why this behavior was flagged—see these three trades").
- Offer interpretable logic paths ("We calculate discipline score using X, Y, and Z—your score dropped because...").
- Let users challenge or reclassify AI assessments, creating a collaborative feedback loop.
- Use tone that supports, not scolds—particularly when calling out underperformance or goal misses.

Mentor will not consume the CSV uploaded by the user, and thus will not produce any new data analyses. To produce its responses, it will only rely on the data consumed from the TradeHabit API’s, and the input from the user in the chatbot dialog.


## Beliefs & Evidence

| # | Belief / Assumption | Current Evidence | Confidence | Evidence Gaps / Next Data |
|---|---------------------|------------------|------------|---------------------------|
| 1 | Problem is real, painful, pervasive | First‑hand reports from trading Discords & FinTwit; repeated mistakes noted in docs | High | Survey or scrape to quantify incidence |
| 2 | Pain severe enough to motivate change | Traders actively seek credible advice online | High | Willingness‑to‑pay interviews |
| 3 | Segment exists & defined | Novice–intermediate futures traders identified | High | Market sizing deferred |
| 4 | AI Mentor can close gap | Concept aligns with coaching vision; to be validated | High | Prototype usability & A/B tests |
| 5 | Strategic fit | Coaching is explicit product pillar | High | None |
| 6 | No blocking legal/tech risks | Read‑only APIs, no PII, prototype stage | Medium | Security review; LLM cost model |


## Reach + Impact vs. Risk

| Dimension | Estimate | Rationale & Key Assumptions | Confidence |
|-----------|----------|------------------------------|------------|
| Reach | High - all users | Mentor will be available in every session | Medium |
| Impact | High | No instrumentation today; will compare Mentor‑vs‑control after event tracking added | Low |
| Risk | Medium | Desirability: Unknown;<br/>Technical: Low;<br/>Security: TBD<br/>Cost: TBD | Medium |
