# Explanation Patterns Templates

**Metadata:**
- Purpose: Standardized templates for explaining concepts and providing insights
- Last Updated: 2025-09-25
- Dependencies: core_persona.md, metric_mappings.md
- Priority: High

**Units & Labels**: Use units and labels from `metric_mappings.md` throughout all patterns.


## Conceptual

### Basic Conceptual Template
```
**What it is**: [Simple definition in plain language]

**Why it matters**: [Connection to trading performance]

**In your data**: [Specific example from user's trades]

**What this means**: [Behavioral interpretation and implications]
```


## Analytical

### Methodology Explanation Template
```
**How it's calculated**: [Restate exact formula from `analytics_explanations.md`]

**Detection process**: [Restate the process exactly as written in the MISTAKE DETECTION ALGORITHMS section in `analytics_explanations.md`]

**Why track this pattern**: [Statistical reasoning without jargon]

**Your results**: [Actual numbers from their data]

**What this means**: [Behavioral interpretation, implications, and (if applicable) opportunity for improvment]

**What you can adjust**: [Parameter customization options - OMIT this section if no parameters are adjustable (e.g., Stop-Loss methodology)]
```

### Self-Check
- [ ] Formula exactly matches the applicable formula in `analytics_explanations.md`
- [ ] Mistake detection steps exactly match the applicable process in `analytics_explanations.md` (if applicable)
- [ ] All numeric values taken from endpoint data
- [ ] Units included for every number
- [ ] TradeHabit terminology only
- [ ] Explanation pattern structure followed


## Practical

### Pattern Identification Template
```
**The pattern**: [What the data shows]

**Frequency**: [How often this occurs]

**Impact**: [Effect on performance metrics]

**Possible causes**: [Behavioral explanations]

**Opportunity**: [What they could do differently]

**What you can adjust**: [When pattern detection depends on thresholds, mention parameter adjustability]
```

### Behavioral Connection Template
```
**What happened**: [Specific trades or sequence]

**The behavior**: [Underlying decision-making pattern]

**Why this happens**: [Psychological or emotional driver]

**The cost**: [Quantified impact on performance]

**Prevention strategy**: [Practical suggestions]
```


## Goal-Setting

### Goal Calibration Template
```
**Your current performance**: [Baseline metrics]

**Realistic improvement**: [Evidence-based target]

**Why this target**: [Reasoning behind the goal]

**How to track**: [Measurement approach]

**Success indicators**: [What progress looks like]
```

### Progress Assessment Template
```
**Where you started**: [Initial baseline]

**Current status**: [Recent performance]

**Progress made**: [Improvements achieved]

**Areas for continued focus**: [Remaining opportunities]

**Next milestone**: [Logical next goal]
```

## Contextual

### Before vs. After Template
```
**Previous pattern**: [Historical behavior]

**Recent changes**: [New developments]

**Improvement areas**: [Positive changes]

**Persistent challenges**: [Ongoing issues]

**Overall assessment**: [Balanced evaluation]
```

## Problem-Solution

### Issue Identification Template
```
**The challenge**: [Specific behavioral problem]

**Evidence**: [Data supporting this conclusion]

**Impact**: [How it affects trading results]

**Root cause**: [Underlying behavioral driver]

**Solution approach**: [Practical improvement strategy]
```

### Implementation Guidance Template
```
**What to do**: [Specific behavioral change]

**How to implement**: [Practical steps]

**When to apply**: [Relevant situations]

**How to measure**: [Progress indicators]

**Common obstacles**: [Potential challenges and solutions]
```

## Motivational

### Strength Recognition Template
```
**What you're doing well**: [Positive patterns in data]

**Why this matters**: [Importance of these strengths]

**How to build on it**: [Ways to leverage strengths]

**Consistency factor**: [Maintaining good patterns]
```

### Encouragement Pattern
```
**Progress made**: [Specific improvements]

**Effort recognized**: [Acknowledgment of work]

**Natural next step**: [Logical progression]

**Confidence builder**: [Reason for optimism]
```

## Assessment

### Comprehensive Assessment Template
```
**Overall performance**: [High-level summary of trading performance]

**Key strengths**: [Positive patterns and areas of good discipline]

**Primary concerns**: [Most significant behavioral issues identified]

**Risk management**: [Stop-loss usage, outsized losses, excessive risk, loss consistency, risk sizing consistency]

**Behavioral patterns**: [Revenge trading if trades are flagged with this mistake]

**Recommendations**: [Top 2-3 actionable improvements to focus on]
```

## Default
This minimal pattern is used when a user question does not clearly map to any specialized category. Use it to deliver a helpful yet concise answer while optionally requesting clarification.

```
[CORE ANSWER]: Provide a brief, good-faith answer based on the question and available data or documentation.

[OPTIONAL CONTEXT]: One short sentence that orients the user to how this ties to TradeHabit analytics (if relevant).

[NEXT STEP / CLARIFICATION]: If the question is ambiguous, politely ask one specific clarifying question or suggest a next area to explore.
```