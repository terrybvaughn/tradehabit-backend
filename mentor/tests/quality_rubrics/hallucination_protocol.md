# Hallucination Detection & Escalation Protocol – TradeHabit Mentor

**Metadata:**
- Purpose: Guidelines for reviewers to identify and handle hallucinations in Mentor outputs
- Last Updated: [DATE]
- Dependencies: metric_mappings.md, help docs, API sample data
- Priority: High

## 1. Definition
A hallucination is any claim, metric, methodology, or number not supported by:
1. TradeHabit API data (`/api/...` endpoints)
2. Help files / knowledge base
3. System prompt corpus

## 2. Detection Checklist
- [ ] Statement cites Help anchor or metric mapping?  
- [ ] Numeric claim matches sample API output?  
- [ ] Metric/label exists in `metric_mappings.md`?  
- [ ] No new mistake categories or analytics concepts invented?

## 3. Severity Levels & Scoring Impact
| Severity | Description | Action | Accuracy Penalty |
|----------|-------------|--------|------------------|
| Minor | Uncertain phrasing, lacks citation | Mark ❕, deduct 1 point | –1 |
| Major | Fabricated metric/number or methodology | Mark ❌, automatic fail | Fail |

## 4. Reviewer Actions
1. Highlight hallucination lines with ❌ or ❕.  
2. Log issue in GitHub referencing prompt file needing correction.  
3. If automatic fail, stop further scoring.

## 5. Model Guardrail Reminder
Mentor prompt directive: *“If not highly confident or lacking data, state limitation or ask for clarification—never fabricate information.”*
