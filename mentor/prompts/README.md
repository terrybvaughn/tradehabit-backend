# TradeHabit Mentor - Prompt Corpus Roadmap

This directory contains the complete prompt engineering corpus for TradeHabit Mentor. This roadmap provides the optimal processing order and usage guidelines for AI model comprehension and implementation.

## 🚀 PROCESSING ORDER (Critical for Model Setup)

### Phase 1: Foundation (Read First - Required)
```
1. system_instructions/core_persona.md          - WHO you are, boundaries, tone
2. system_instructions/conversation_guidelines.md - HOW to interact 
3. system_instructions/trading_expert.md        - WHAT you know about trading
```
**Purpose**: Establishes Mentor's identity, interaction style, and domain expertise before any knowledge ingestion.

### Phase 2: Authoritative Knowledge (Core Reference)
```
4. knowledge_base/metric_mappings.md           - SINGLE SOURCE OF TRUTH for all definitions
5. knowledge_base/tradehabit_functionality.md  - What TradeHabit does
6. knowledge_base/analytics_explanations.md    - How TradeHabit works (methodology)
7. knowledge_base/trading_concepts.md          - General trading knowledge
```
**Purpose**: Loads core knowledge with `metric_mappings.md` as the authoritative glossary for all terminology.

### Phase 3: Application Frameworks (Implementation Guides)
```
8. conversation_starters/first_time_user.md    - Initial user engagement patterns
9. templates/explanation_patterns.md           - Content templates (what to say)
10. templates/response_formats.md              - Structure templates (how to say it)
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

### **Application Templates** (Implementation Tools)
- `explanation_patterns.md` - Content templates using authoritative knowledge
- `response_formats.md` - Structure templates aligned with conversation guidelines
- `first_time_user.md` - Engagement patterns reflecting core persona

## 🔗 Critical Dependencies

### Primary Dependencies (Must Load First)
```
core_persona.md → ALL other files
metric_mappings.md → analytics_explanations.md, explanation_patterns.md
conversation_guidelines.md → response_formats.md
```

### Cross-References (Load Together)
```
tradehabit_functionality.md ↔ analytics_explanations.md
explanation_patterns.md ↔ response_formats.md
trading_expert.md ↔ knowledge_base/ files
```

## ⚡ Quick Reference Guide

### When Responding to Users:
1. **Check persona** (core_persona.md) - Am I staying in character?
2. **Use authoritative terms** (metric_mappings.md) - Am I using correct labels?
3. **Apply structure** (response_formats.md) - Is my response well-formatted?
4. **Fill with content** (explanation_patterns.md) - Am I explaining effectively?

### For New User Interactions:
1. **Start with** first_time_user.md templates
2. **Reference** conversation_guidelines.md for flow management
3. **Explain using** explanation_patterns.md content templates
4. **Structure with** response_formats.md frameworks

### For Technical Questions:
1. **Definitions from** metric_mappings.md (authoritative)
2. **Functionality from** tradehabit_functionality.md
3. **Methodology from** analytics_explanations.md
4. **Context from** trading_concepts.md

## 🎯 Usage Principles

### Information Priority Order:
1. **Core persona** - Never compromise identity or boundaries
2. **Authoritative definitions** - Use exact terminology from glossary
3. **User's data** - Always personalize with their specific trading patterns
4. **Template guidance** - Follow established patterns for consistency

### Conflict Resolution:
- **Terminology conflicts**: metric_mappings.md wins
- **Personality conflicts**: core_persona.md wins  
- **Functionality conflicts**: tradehabit_functionality.md wins
- **Process conflicts**: conversation_guidelines.md wins

### Parameter Calibration Priority:
- **Always emphasize** parameter calibration importance (per tradehabit_functionality.md)
- **Use templates** from first_time_user.md for parameter discussions
- **Reference** analytics_explanations.md for methodology explanation

## 📁 File Roles Summary

| Directory | Role | Authority Level |
|-----------|------|----------------|
| `system_instructions/` | Foundation & Identity | **AUTHORITATIVE** |
| `knowledge_base/` | Reference & Definitions | **AUTHORITATIVE** |
| `conversation_starters/` | Initial Engagement | Supporting |
| `templates/` | Response Structure | Supporting |

## 🔄 Maintenance Notes

When updating:
1. **System instructions** - Test all conversation flows
2. **Knowledge base** - Verify against actual TradeHabit functionality  
3. **Conversation starters** - Validate against persona guidelines
4. **Templates** - Ensure consistency with knowledge base

Critical: Any changes to `core_persona.md` or `metric_mappings.md` require comprehensive review of all dependent files.
