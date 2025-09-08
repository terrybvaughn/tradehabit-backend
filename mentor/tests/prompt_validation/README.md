# Prompt Validation Tests

**Metadata:**
- Purpose: Test scenarios for validating prompt accuracy and coverage
- Last Updated: 2025-09-08
- Dependencies: All prompt files
- Priority: High

## Test Categories

### Knowledge Base Validation
- **TradeHabit functionality coverage**: Verify all features have explanation prompts
- **Statistical accuracy**: Ensure methodology explanations match actual implementation
- **API endpoint coverage**: Confirm all endpoints are documented and explainable

### Response Quality Tests
- **Consistency checks**: Verify tone and personality remain consistent
- **Accuracy verification**: Ensure factual correctness of all explanations
- **Completeness assessment**: Confirm all user question types are addressed

### Conversation Flow Tests
- **Engagement patterns**: Test conversation starters for different user types
- **Topic transitions**: Verify smooth movement between different subjects
- **Clarification handling**: Test response to unclear or ambiguous questions

## Test Implementation

### Automated Checks
- Prompt file completeness (all required sections present)
- Cross-reference validation (dependencies exist and are current)
- Terminology consistency across files
- **Quality scoring**: Evaluate responses using `quality_rubrics/response_quality_rubric.md` and apply `quality_rubrics/hallucination_protocol.md` for hallucination checks

### Manual Review Scenarios
- Sample conversations with different user personas
- Edge case handling (insufficient data, out-of-scope questions)
- Response appropriateness for different complexity levels

### Regression Testing
- Verify existing functionality after prompt updates
- Ensure personality consistency after modifications
- Confirm knowledge base accuracy after system changes

## Test Documentation Template

```markdown
### Test Case: [TEST_NAME]
**Purpose**: [What this test validates]
**Prompt Files**: [Which files are being tested]
**Scenario**: [Test situation description]
**Expected Outcome**: [What should happen]
**Pass Criteria**: [How to determine success]
**Notes**: [Additional considerations]
```