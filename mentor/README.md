# TradeHabit Mentor - Prompt Corpus

This directory contains the complete prompt engineering corpus for TradeHabit Mentor, the AI-powered trading coach that helps retail traders understand their behavioral patterns and improve their trading discipline.

## Directory Structure

### `/prompts/system_instructions/`
Core system prompts that define Mentor's personality, expertise, and interaction patterns:
- `core_persona.md` - Fundamental personality and coaching philosophy
- `trading_expert.md` - Domain expertise and analytical capabilities
- `conversation_guidelines.md` - Interaction patterns and conversation management

### `/prompts/knowledge_base/`
Comprehensive knowledge reference for all TradeHabit functionality and trading concepts:
- `tradehabit_functionality.md` - Complete feature reference and API capabilities
- `trading_concepts.md` - Behavioral psychology and trading fundamentals
- `analytics_explanations.md` - Statistical methodology and interpretation guidance

### `/prompts/conversation_starters/`
Templates for initial user engagement based on user type and session context:
- `first_time_user.md` - Onboarding patterns for new users
- `returning_user.md` - Re-engagement patterns for experienced users

### `/prompts/templates/`
Standardized response patterns and formatting guidelines:
- `explanation_patterns.md` - Templates for teaching concepts and providing insights
- `response_formats.md` - Structured approaches for different interaction types

### `/tests/`
Validation and quality assurance for prompt effectiveness:
- `prompt_validation/` - Tests for prompt accuracy and coverage
- `conversation_flows/` - End-to-end conversation testing scenarios

## Usage Guidelines

### Development Workflow
1. **Reference existing templates** before creating new response patterns
2. **Update knowledge base** when TradeHabit functionality changes
3. **Test prompt changes** using validation scenarios
4. **Version control** all changes for rollback capability

### Maintenance Priorities
1. **System instructions** - Core personality and expertise (highest priority)
2. **Knowledge base** - Accuracy of TradeHabit functionality (critical)
3. **Conversation starters** - User engagement patterns (important)
4. **Templates** - Response standardization (helpful)

### Integration Points
- **Backend APIs**: Knowledge base must stay synchronized with actual TradeHabit endpoints
- **Frontend flows**: Conversation starters should align with UX design
- **Analytics engine**: Statistical explanations must match actual algorithms

## Key Principles

### Behavioral Focus
All prompts emphasize trading behavior and discipline improvement over market predictions or strategy recommendations.

### Data-Driven Insights
Responses should always reference the user's actual trading data when providing explanations or guidance.

### Progressive Disclosure
Information should be presented in digestible chunks, building complexity based on user engagement and comprehension.

### Empathetic Coaching
Maintain supportive tone while delivering direct feedback about behavioral patterns and improvement opportunities.

## Quality Standards

### Accuracy Requirements
- All TradeHabit functionality references must be current and correct
- Statistical methodology explanations must align with actual implementation
- Trading psychology concepts must be evidence-based

### Consistency Standards
- Personality and tone should be consistent across all interactions
- Terminology and explanations should be standardized
- Response patterns should follow established templates

### Completeness Criteria
- All TradeHabit features must have explanation coverage
- Common user questions should have templated responses
- Edge cases and error conditions should be addressed

## Version Control Strategy

### File-Level Versioning
Each prompt file includes metadata header with:
- Purpose and scope
- Last updated date
- Dependencies on other files
- Priority level for updates

### Change Management
- **Major updates**: Personality changes, new features, methodology updates
- **Minor updates**: Clarifications, examples, formatting improvements
- **Patches**: Typo fixes, broken references, minor corrections

### Testing Requirements
- **New prompts**: Must include validation scenarios
- **Modified prompts**: Regression testing on existing scenarios
- **Knowledge updates**: Accuracy verification against actual system behavior

## Implementation Notes

### LLM Considerations
- Prompts designed for modern LLM capabilities (GPT-4 class models)
- Context window management through modular prompt structure
- Token efficiency balanced with prompt completeness

### Personalization Approach
- Dynamic content insertion based on user's trading data
- Adaptive complexity based on user engagement patterns
- Progressive conversation building through session memory

### Error Handling
- Graceful degradation when data is insufficient
- Clear boundaries for out-of-scope questions
- Helpful redirections to appropriate resources or topics