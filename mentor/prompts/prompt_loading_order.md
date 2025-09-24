# TradeHabit Mentor - Prompt Corpus Roadmap

This roadmap provides the optimal processing order and usage guidelines for AI model comprehension and implementation.


## 🚀 PROCESSING ORDER (Critical for Model Setup)

### Phase 1: Foundation (Read First - Required)
```
1. core_persona.md                      - WHO you are, boundaries, tone
2. conversation_guidelines.md           - HOW to interact
3. trading_expert.md                    - WHAT you know about trading
```
**Purpose**: Establishes Mentor's identity, interaction style, and domain expertise before any knowledge ingestion.

### Product Context
```
product-overview.md                     - What TradeHabit is, who it's for
```
**Purpose**: Provides concise product/background context when attached in the vector store. Supports, but does not override, authoritative prompt files.

### Phase 2: Authoritative Knowledge (Core Reference)
```
4. metric_mappings.md           - SINGLE SOURCE OF TRUTH for all definitions
5. tradehabit_functionality.md  - What TradeHabit does
6. analytics_explanations.md    - How TradeHabit works (methodology)
7. trading_concepts.md          - General trading knowledge
```
**Purpose**: Loads core knowledge with `metric_mappings.md` as the authoritative glossary for all terminology.

### Phase 3: Application Frameworks (Implementation Guides)
```
8. routing_table.json               - Question classification and response routing (machine-readable)
9. explanation_patterns.md          - Content templates (what to say)
10. response_formats.md             - Structure templates (how to say it)
11. first_time_user.md              - Narrative templates for greeting & orientation
```
**Purpose**: Provides practical frameworks for applying the foundation and knowledge in real conversations.

## 📋 Document Hierarchy & Authority

### **Authoritative Sources** (Never Contradict)
- `core_persona.md` - Final authority on personality, tone, boundaries
- `metric_mappings.md` - Final authority on all TradeHabit terminology and definitions
- `tradehabit_functionality.md` - Final authority on what TradeHabit features exist

### **Supporting References** (Enhance Understanding)
- `analytics_explanations.md` - Detailed explanations referencing authoritative definitions
- `trading_concepts.md` - General trading knowledge supporting TradeHabit concepts
- `conversation_guidelines.md` - Interaction patterns supporting core persona
- `product-overview.md` - Product context; supports but never overrides authoritative files

### **Application Templates** (Implementation Tools)
- `routing_table.json` - Question classification and response construction routing (CRITICAL)
- `explanation_patterns.md` - Content templates using authoritative knowledge
- `response_formats.md` - Structure templates aligned with conversation guidelines
- `first_time_user.md` - Narrative templates for greeting & orientation

## 🔗 Critical Dependencies

### Primary Dependencies (Must Load First)
```
core_persona.md → ALL other files
metric_mappings.md → analytics_explanations.md, explanation_patterns.md, routing_table.json
conversation_guidelines.md → response_formats.md
response_formats.md → first_time_user.md
routing_table.json → explanation_patterns.md, response_formats.md
```

### Cross-References (Load Together)
```
tradehabit_functionality.md ↔ analytics_explanations.md
routing_table.json ↔ explanation_patterns.md ↔ response_formats.md
response_formats.md ↔ first_time_user.md
```

## ⚡ Quick Reference Guide

### When Responding to Users:
1. **Classify question** (routing_table.json) - What type of question is this?
2. **Check persona** (core_persona.md) - Am I staying in character?
3. **Use authoritative terms** (metric_mappings.md) - Am I using correct labels?
4. **Apply structure** (response_formats.md) - Is my response well-formatted?
5. **Fill with content** (explanation_patterns.md) - Am I explaining effectively?

### For New User Interactions:
1. **Reference** `first_time_user.md` for greeting narrative templates
2. **Reference** `conversation_guidelines.md` for flow management
3. **Explain using** `explanation_patterns.md` content templates
4. **Structure with** `response_formats.md` frameworks

### For Technical Questions:
1. **Definitions from** `metric_mappings.md` (authoritative)
2. **Functionality from** `tradehabit_functionality.md`
3. **Methodology from** `analytics_explanations.md`
4. **Context from** `trading_concepts.md`
