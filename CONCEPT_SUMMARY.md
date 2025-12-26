# My3 Concept Document & Sprint Plan Summary

## Key Requirements from Concept Document

### Core Vision
My3 is an AI-powered personal relationship and gifting concierge that:
- Remembers important people and key dates
- Understands preferences through conversation
- Recommends thoughtful, context-aware gifts
- Orchestrates discovery and purchase
- Learns continuously from feedback

### Relationship Network Map Requirements

1. **"Relationships That Matter" Focus**
   - Users should have **~10 relationships that matter** (not hundreds)
   - Graph only shows relationships where user wants to make long-term time and money investments
   - Addresses clutter concerns mentioned in sprint plan

2. **Visual Indicators**
   - Color tagging to show availability of shared gift interests/wishlist profile
   - Visual highlight for wishlist-available nodes
   - Show where user has/hasn't invested recently
   - Highlight core circle of relationships

3. **Network Graph Features**
   - Interactive visualization of "relationships that matter"
   - Show closeness, interaction recency, and upcoming occasions
   - Relationship network map showing investment patterns

### Key Features to Implement

#### 1. Wishlist System
- Each user maintains a wishlist profile (brands, sizes, do/don't wants)
- Wishlists have visibility controls (private or shared)
- When shared, My3 prioritizes those items in recommendations
- Visual tagging in network graph for wishlist-available profiles

#### 2. Proactive Nudges
- 30 days before key dates (configurable), My3 nudges user
- Example: "Your sister's birthday is coming up. Shall we plan something special?"

#### 3. Relationship Profiling
- Capture recipient's personality, interests, gifting preferences
- Build rich profiles through conversational interaction
- Store in recipient profile

#### 4. Recommendation Engine
- Multi-signal recommendation engine learning from:
  - Past gifts and outcomes
  - Wish lists and registries
  - Publicly available signals (where appropriate)
  - Aggregate community behavior

#### 5. Feedback Loop
- Dual-sided reviews from gifters and recipients
- Track delivery and prompt for feedback
- Improve model and future suggestions

### Current Implementation Status

✅ **Implemented:**
- Basic network graph visualization
- User, Recipient, Occasion, GiftIdea data models
- Chat interface with LangGraph workflow
- Basic relationship management

❌ **Missing/Needs Enhancement:**
- "Relationships that matter" flag/filtering (limit to ~10)
- Wishlist system and visual indicators
- Proactive nudge system (30-day reminders)
- Investment recency tracking
- Wishlist availability indicators in graph
- Enhanced profiling through conversation
- Multi-signal recommendation engine
- Feedback/review system

### Sprint Plan Notes
- Concern about clutter addressed: users won't have more than 10 "relationships that matter"
- Graph only shows relationships where long-term investment is intended
- Base44 links provided for reference

## Next Steps

1. Add "relationships_that_matter" flag to Recipient model
2. Enhance NetworkGraph to show wishlist indicators
3. Add investment recency tracking
4. Implement wishlist system
5. Add proactive nudge/reminder system
6. Enhance recommendation engine




