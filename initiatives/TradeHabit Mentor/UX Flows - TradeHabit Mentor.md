# UX Flows - TradeHabit Mentor

#### Flows
1. Comprehend Analytics Package: User understands metrics, analytics, parameters, insights and methodology (**analytics package** for short)
2. Adjust Parameters: User can adjust analytics parameters to fit the user's trading style
3. Understand Performance Analysis: User understands the trading performance analysis and insights presented

## 1. Comprehend Analytic Package

- **User Goal:** Make sense of TradeHabit metrics, analytics, parameters, insights and methodology
- **Preconditions:** User has successfully uploaded data and the system has output all of its analytic data
- **Success Criteria:** AI Assistanct can explain all features of the TradeHabit analytics package

### Happy Path

| Step | User | System | AI Assistant |
|------|------|--------|--------------|
| P | | Output analytics package with default parameters | |
| 1 | | | Consume system outputs |
| 2 | | | - Output a friendly introduction<br />- Present prompt suggestions based on common user questions |
| 3 | - Click a prompt suggestion, or<br />- Input question(s) | | |
| 4 | | |  Respond in accordance with System Instructions |

#### Applicable Conversation UX Patterns to Explore
- Indicate status when generation is in progress
- Progressive disclosure of responses (TBD)
- Conversation memory - AI Assistant can reference previous chat content
- Clarification requests when user questions are ambiguous
- When applicable, responses should reference specific TradeHabit analytic features, methodologies or user performance results, e.g. "Based on..."


## 2. Adjust Parameters

- **User Goal:** Calibrate analytics parameters to match their specific trading style and approach
- **Preconditions:** User understands the basic analytics methodology and has seen initial results
- **Success Criteria:** AI Assistant has helped user set appropriate parameter thresholds that produce meaningful, relevant behavioral insights

### Happy Path

| Step | User | System | AI Assistant |
|------|------|--------|--------------|
| 1 | | | - Assess current parameter settings and results<br />- Explain importance of parameter calibration |
| 2 | | | Present current parameter settings and what they mean in trading terms |
| 3 | Responds with trading style info (timeframes, risk tolerance, etc.) | | |
| 4 | | | - Analyze user's trading approach<br />- Recommend specific parameter adjustments<br />- Explain rationale for recommendations |
| 5 | Approves/modifies recommended parameters | Update analytics with new parameters | |
| 6 | | Re-generate analytics package with calibrated parameters | Confirm parameters are now properly calibrated |

## 3. Understand Performance Analysis

- **User Goal:** Understand the trading performance analysis and insights presented
- **Preconditions:** Parameters are calibrated and user has basic understanding of analytics methodology
- **Success Criteria:** AI Assistant can provide meaningful behavioral insights based on properly calibrated analysis