# User Value Map - TradeHabit Mentor

### Persona
Retail traders that are struggling with discipline problems.

### Customer Journey
| Stage | Activities |
|-------|------------|
| Upload | 1. Export trade history CSV from NinjaTrader <br/>2. Navigate to TradeHabit app and upload the CSV file |
| Interpret | 1. Comprehend the data, metrics and methods to assess performance (what do all these analyses mean?) <br/>2. Understand the specific problems that are affecting performance and their magnitude (what mistakes am I making and what is their impact?) |
| Decide | 1. Synthesize insights for each mistake category (frequency, severity, and impact data) <br/>2. Prioritize which behavioral problems to address first based on their impact on trading performance |
| Set Goals | 1. Create goal(s) that are calibrated to the user's ability, so they are a challenge, yet attainable |
| Track Progress | 1. Monitor performance and figure out how to correct behavioral problems to get back on track  |

### Pain Point Prioritization

| Pain Point | Magnitude | Frequency | Severity | Competition | Contrast | Priority |
|------------|-----------|-----------|----------|-------------|----------|----------|
| Not understanding analytics/metrics | High | High | High | Weak | High | **High** |
| Can't identify behavior-performance connection | High | Medium | High | Weak | High | **High** |
| Overwhelmed by multiple issues, can't prioritize | High | High | Medium | Weak | High | **High** |
| Doesn't know how to implement behavioral corrections | High | High | High | Medium | High | **High** |
| Lacks ongoing accountability and feedback | High | High | High | Strong | High | **Medium** |
| Sets unrealistic goals (too hard) | Medium | Medium | High | Medium | Medium | **Medium** |
| Sets goals that are too easy | Medium | Low | Medium | Weak | Low | **Medium** |
| Doesn't understand magnitude/severity of mistakes | Medium | Medium | Medium | Weak | Medium | **Medium** |
| Lacks motivation to stick with changes | High | Medium | Medium | Strong | Medium | **Medium** |
| Doesn't notice slipping back into bad habits | Medium | High | Medium | Medium | Medium | **Medium** |
| Doesn't know how to course-correct | Medium | Medium | Medium | Medium | Medium | **Medium** |
| Data upload format issues | Medium | Low | Medium | Weak | Low | **Low** |
| Finding/downloading correct data | Low | Low | Low | N/A | N/A | **Low** |

### Strategic Implementation Priority

While the pain point analysis above identifies market opportunities across all stages, the sequential and dependent nature of the customer journey creates a critical implementation imperative: **TradeHabit Mentor must first solve interpretation-stage pain points before addressing downstream issues.**

**The Interpretation Bottleneck:**
- Users who can't understand analytics/metrics will abandon the platform entirely
- Users who can't connect behaviors to performance outcomes won't progress to decision-making
- Downstream pain points (goal-setting, motivation, accountability) are irrelevant if users get stuck at interpretation

**Therefore, Mentor's initial focus should prioritize:**
1. **Not understanding analytics/metrics** - foundational comprehension
2. **Can't identify behavior-performance connection** - actionable insight generation  
3. **Doesn't understand magnitude/severity of mistakes** - context for decision-making

Success at the interpretation stage unlocks the entire customer journey. Failure here renders all other coaching capabilities worthless, regardless of their market opportunity.


### AI Opportunities

**Pain Points Addressable by Generative AI:**

1. **Not understanding analytics/metrics** - LLMs excel at explaining complex statistical concepts (sigma multipliers, Z-scores, distributions) in plain, accessible language tailored to the user's experience level
2. **Can't identify behavior-performance connection** - LLMs can analyze patterns in data and articulate cause-and-effect relationships between specific behaviors and trading outcomes in clear, narrative form
3. **Doesn't understand magnitude/severity of mistakes** - LLMs can provide contextual comparisons and relative severity assessments ("This revenge trading pattern is costing you 23% of your profits compared to typical traders")
4. **Overwhelmed by multiple issues, can't prioritize** - LLMs can synthesize complex information across multiple behavioral patterns and provide clear, reasoned prioritization frameworks
5. **Sets goals that are poorly calibrated (too hard or too easy)** - LLMs can analyze historical performance data to set appropriately challenging goals that are realistic yet ambitious based on the user's trading patterns and progression capability
6. **Doesn't know how to implement behavioral corrections** - LLMs excel at providing specific, actionable guidance ("Here are 3 concrete steps to improve your stop-loss discipline based on your trading style")
7. **Lacks motivation to stick with changes** - LLMs can provide personalized motivational coaching, celebrate progress, and reframe setbacks constructively
8. **Doesn't know how to course-correct** - LLMs can analyze current performance against goals and provide specific corrective strategies tailored to the user's situation

**Pain Points NOT Well-Suited for Generative AI:**
- Data upload format issues (technical validation problem)
- Finding/downloading correct data (external system dependency)
- Doesn't notice slipping back into bad habits (requires proactive monitoring system, though LLMs can help interpret once flagged)
