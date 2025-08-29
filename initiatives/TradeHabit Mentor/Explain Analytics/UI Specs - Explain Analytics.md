# UI Specs - Explain Analytics

## Chat UI Elements

### Core Chat Interface
- **Chat Input Field**: Primary text box for user messages and queries
- **Send Button**: Mechanism for submitting user input, usually placed next to the input field
- **Chat Output Area**: Scrollable section displaying all system responses and user inputs for clear reading
- **Scrollable Conversation History**: The ability to review and scroll back through prior messages for context and continuity
- **Editable Message Interface**: Clickable user messages that transform into editable text fields with submit/cancel buttons when selected

### Initial Experience
- **Welcome Message**: Initial greeting that sets expectations for chat capabilities and offers basic instructions
- **Suggested Prompts**: Examples beneath the input box to help users start the conversation or understand the app's core functions. Only display once after Welcome Message

### Response Enhancement
- **Expandable / "Show-More" Blocks**: Collapsible container used by the progressive-disclosure pattern to reveal the full calculation walk-through or statistical deep-dive
- **Quoted-Help Snippet Card**: Distinct visual card (different background or quote style) for direct excerpts from Help files, including quoted text and deep-link icon that opens the relevant Help anchor in a new tab/modal
- **Disambiguation Prompt Chips**: When Mentor detects an ambiguous question, clickable chips such as "Definition" "Calculation" "Example from my trades" to clarify user intent without extra typing

### System Feedback
- **System Thinking Indicator**: Animation or ellipsis signaling the AI is processing a request to reduce user uncertainty
- **Toast / Inline Error Banner**: For ambiguity detection and error handling - if Mentor cannot map the question to a known metric or concept, an inline banner explains the issue and suggests reformulating or selecting from disambiguation chips
- **Error Message Handling**: Human-readable error states for API or system failures, guiding users on next steps

### Session Management
- **Session Reset/New Conversation Button**: Option to clear the chat and restart the session, supporting workflows or privacy needs


## Chat UI States

### 1. **Initial State**
- Welcome message displayed
- Suggested prompts visible below input field
- Empty chat history
- Input field focused and ready

### 2. **Processing State**
- User has submitted a question
- System thinking indicator active
- Input field disabled during processing
- Previous conversation history visible

### 3. **Standard Response State**
- AI response displayed in chat output area
- Input field re-enabled
- Suggested prompts hidden (only show after welcome)
- Scrollable conversation history

### 4. **Progressive Disclosure State**
- AI response with expandable "Show More" blocks
- Some content collapsed by default
- User can click to reveal deeper explanations
- Help snippet cards visible when referenced

### 5. **Disambiguation State**
- AI detects ambiguous question
- Disambiguation prompt chips displayed
- Brief explanatory text above chips
- User can click chips or type clarification

### 6. **Direct Quote State**
- AI response includes quoted Help file content
- Blockquote styling visually distinguishes authoritative source material
- Source attribution with deep-link displayed below quote
- Combines quoted content with personalized interpretation

### 7. **Inline Citation State**
- AI response references Help content without direct quotes
- Italicized citation links appear at end of explanatory paragraphs
- Subtle attribution maintains natural conversation flow
- Deep-links available for source verification

### 8. **Prompt Edit State**
- User clicks on a previous prompt to edit
- Selected prompt transforms into editable text field
- Submit and cancel buttons appear next to edited prompt
- Rest of conversation grayed out or disabled during editing
- Upon submission, conversation regenerates from that point

### 9. **Error State**
- Toast/inline error banner visible
- Clear error message with suggested next steps
- Input field remains enabled
- Option to retry or reformulate question
