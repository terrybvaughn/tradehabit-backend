# TradeHabit Mentor

This directory contains the complete TradeHabit Mentor feature implementation - an AI-powered trading coach that helps retail traders understand their behavioral patterns and improve their trading discipline through data-driven insights.

## Directory Structure

### `/prompts/`
Complete prompt engineering corpus for TradeHabit Mentor. **See [prompts/README.md](prompts/README.md) for detailed processing order and usage guidelines.**

Key components:
- `assistant/` - Core system instructions and function schemas
- `persona/` - Personality, conversation guidelines, and trading expertise
- `knowledge_base/` - TradeHabit functionality and trading concepts reference
- `conversation_starters/` - Initial user engagement templates
- `templates/` - Standardized response patterns and formatting

### `/tests/`
Validation and quality assurance for prompt effectiveness:
- `prompt_validation/` - Tests for prompt accuracy and coverage
- `conversation_flows/` - End-to-end conversation testing scenarios

## Usage Guidelines

### Prompt Corpus Management
**For detailed prompt usage guidelines, processing order, and document hierarchy, see [prompts/README.md](prompts/README.md).**

### Development Workflow
1. **Follow prompt roadmap** for optimal model comprehension
2. **Update knowledge base** when TradeHabit functionality changes  
3. **Test prompt changes** using validation scenarios
4. **Version control** all changes for rollback capability

### Integration Points
- **Backend APIs**: Knowledge base must stay synchronized with actual TradeHabit endpoints
- **Tool Runner**: Optimized with in-memory caching and smart API routing for performance
- **Frontend flows**: Conversation starters should align with UX design
- **Analytics engine**: Statistical explanations must match actual algorithms

## Key Principles

### Behavioral Focus
All prompts emphasize trading behavior and discipline improvement over market predictions or strategy recommendations.

### Data-Driven Insights
Responses should always reference the user's actual trading data when providing explanations or guidance. Tool usage is mandatory for any data-related responses to ensure accuracy and prevent hallucination.

### Progressive Disclosure
Information should be presented in digestible chunks, building complexity based on user engagement and comprehension.

### Empathetic Coaching
Maintain supportive tone while delivering direct feedback about behavioral patterns and improvement opportunities.

## Quality Standards

### Accuracy Requirements
- All TradeHabit functionality references must be current and correct
- Statistical methodology explanations must align with actual implementation
- Trading psychology concepts must be evidence-based
- Authoritative scope compliance: No feature invention or parameter modification beyond documented capabilities
- Real-time capability accuracy: Clear representation of post-session analysis limitations

### Consistency Standards
- Personality and tone should be consistent across all interactions
- Terminology and explanations should be standardized using canonical mappings
- Response patterns should follow established templates
- Parameter explanations must reference authoritative documentation sources

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
- Performance optimizations: In-memory caching and smart API routing reduce response times

### Personalization Approach
- Dynamic content insertion based on user's trading data
- Adaptive complexity based on user engagement patterns
- Progressive conversation building through session memory

### Error Handling
- Graceful degradation when data is insufficient
- Clear boundaries for out-of-scope questions
- Helpful redirections to appropriate resources or topics
- Authoritative scope enforcement prevents hallucination and feature invention