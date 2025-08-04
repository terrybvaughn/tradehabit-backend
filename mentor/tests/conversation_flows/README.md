# Conversation Flow Tests

**Metadata:**
- Purpose: End-to-end conversation testing scenarios for TradeHabit Mentor
- Last Updated: [DATE]
- Dependencies: All prompt files, sample trading data
- Priority: High

## Flow Test Categories

### User Journey Tests
- **First-time user onboarding**: Complete interaction from data upload to goal setting
- **Returning user engagement**: Conversation restart patterns and progress tracking
- **Advanced user interactions**: Deep dives into methodology and parameter adjustment

### Comprehension Flow Tests
- **Analytics explanation flow**: User learns TradeHabit methodology and metrics
- **Performance analysis flow**: User understands their specific trading patterns
- **Parameter adjustment flow**: User customizes analysis settings

### Goal-Oriented Conversations
- **Problem identification**: Moving from confusion to clarity about behavioral issues
- **Goal setting discussions**: Establishing realistic improvement targets
- **Progress tracking conversations**: Reviewing advancement and adjusting plans

## Test Scenarios

### Scenario 1: New User with High Mistake Rate
```
User Profile: First-time user, 40% trades flagged, primarily stop-loss issues
Starting Point: Just uploaded data, seeing dashboard for first time
Success Criteria: User understands stop-loss discipline and sets realistic goal
Flow Coverage: Introduction → Explanation → Problem Recognition → Goal Setting
```

### Scenario 2: Analytical User Seeking Methodology
```
User Profile: Experienced trader, wants to understand statistical methods
Starting Point: Questions about sigma multipliers and thresholds
Success Criteria: User grasps methodology and adjusts parameters appropriately
Flow Coverage: Technical Explanation → Parameter Discussion → Customization
```

### Scenario 3: Overwhelmed User with Multiple Issues
```
User Profile: Many flagged mistakes, feeling discouraged
Starting Point: Asking "where do I even start?"
Success Criteria: User feels hopeful and has clear next steps
Flow Coverage: Prioritization → Encouragement → Focused Goal Setting
```

### Scenario 4: Progress-Tracking User
```
User Profile: Returning user with previous goals, mixed results
Starting Point: Uploading new data after behavioral work
Success Criteria: User sees progress and adjusts goals appropriately
Flow Coverage: Progress Review → Achievement Recognition → Goal Evolution
```

### Scenario 5: Skeptical User Questioning Accuracy
```
User Profile: Questions whether flagged mistakes are actually problems
Starting Point: Challenging specific flagged trades
Success Criteria: User understands reasoning and finds value in analysis
Flow Coverage: Evidence Presentation → Methodology Explanation → Buy-in
```

## Conversation Templates

### Test Conversation Structure
```
**Setup**: [User type, data characteristics, starting context]
**User Input**: [What the user says or asks]
**Expected Response Elements**: [Key components Mentor should include]
**Follow-up Variations**: [Different paths conversation might take]
**Success Indicators**: [Evidence that flow worked effectively]
```

### Quality Criteria
- **Engagement**: User continues conversation rather than abandoning
- **Comprehension**: User demonstrates understanding through questions/responses
- **Action**: User expresses interest in behavioral change or goal setting
- **Satisfaction**: User finds value in the interaction

## Implementation Guidelines

### Test Data Requirements
- Sample trading data with various mistake patterns
- Different user profiles (beginner, intermediate, advanced)
- Various data quality scenarios (clean, messy, limited)

### Evaluation Methods
- **Conversation length**: Appropriate depth without overwhelming
- **Topic coverage**: All relevant areas addressed naturally
- **User satisfaction proxies**: Engagement signals and follow-up questions
- **Goal achievement**: Did user reach stated objective?

### Documentation Standards
Each test should include:
- Complete conversation transcript
- Analysis of Mentor responses
- Identification of successful patterns
- Areas for improvement
- Recommendations for prompt refinement

## Continuous Improvement

### Flow Optimization
- Identify common conversation breakdowns
- Recognize patterns in successful interactions
- Develop improved conversation starters
- Refine response templates based on testing

### User Experience Enhancement
- Reduce time to first "aha moment"
- Improve clarity of complex explanations
- Enhance motivation and encouragement
- Streamline path to actionable insights

### Quality Assurance
- Regular testing of all conversation flows
- Validation after prompt updates
- Performance monitoring of live interactions
- User feedback incorporation into test scenarios