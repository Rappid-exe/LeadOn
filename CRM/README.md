# CRM System - Twenty Integration

This folder contains the CRM system for the Sales Workflow Agentic System hackathon project, using the open-source [Twenty CRM](https://github.com/twentyhq/twenty).

## Overview

The CRM serves as the central database for managing contacts, tracking actions, and coordinating between the scraping and LinkedIn automation systems.

## Responsibilities

### Database Schema
- **Contacts**: Store lead information (name, title, company, email, LinkedIn URL, phone, tags, source)
- **Actions**: Log all LinkedIn automation activities (likes, comments, endorsements, connections, messages)
- **Campaigns**: Track user prompts and target segments
- **Relationships**: Monitor relationship stages and interaction history

### API Endpoints
- CRUD operations for contacts
- Action logging endpoints
- Search/filter contacts by tags, company, title
- Contact history retrieval
- Bulk operations (import, export, update)

### Action Tracking
Every LinkedIn automation action is logged with:
- Action type: `post_liked`, `comment_posted`, `skill_endorsed`, `connection_request_sent`, `message_sent`
- Timestamp and status (pending, completed, failed)
- Contact relationship stage updates

## Integration Points

### Input from Scraper Team (Team 1)
- Receives enriched contact data from Apollo.io and job site scrapers
- Auto-populates CRM with deduplicated, categorized leads
- Tags contacts based on user prompt context

### Output to LinkedIn Automation Team (Team 3)
- Provides contact lists filtered by tags and relationship stage
- Receives action logs from LinkedIn bot
- Updates contact relationship stages based on engagement

## Data Schemas

### Contact Schema
```json
{
  "id": "uuid",
  "name": "John Doe",
  "title": "Partner at XYZ Ventures",
  "company": "XYZ Ventures",
  "email": "john@xyz.com",
  "linkedin_url": "https://linkedin.com/in/johndoe",
  "phone": "+1234567890",
  "tags": ["vc", "ai_investor", "fundraising_target"],
  "source": "apollo.io",
  "relationship_stage": "new_lead",
  "created_at": "2025-11-01T10:00:00Z",
  "last_updated": "2025-11-01T10:00:00Z"
}
```

### Action Schema
```json
{
  "id": "uuid",
  "contact_id": "uuid",
  "action_type": "connection_request_sent",
  "action_details": {
    "message": "Hi John, I'm working on an AI startup...",
    "platform": "linkedin"
  },
  "timestamp": "2025-11-01T14:30:00Z",
  "status": "completed"
}
```

## Setup

Refer to the [Twenty CRM documentation](https://twenty.com/developers) for installation and configuration instructions.

## Development Guidelines

When working with AI on CRM development:
- Request: "Create SQLAlchemy models for [entity] with relationships to [other entities]"
- Specify: "Build FastAPI CRUD endpoints with Pydantic validation"
- Include: "Add database indexes for frequently queried fields"
- Ask for: "Implement soft deletes and audit trails"
- Request: "Create migration scripts using Alembic"
- Specify: "Add full-text search capabilities for contact search"

## Team Communication

This CRM system is the bridge between:
- **Team 1 (Scrapers)** → Populates contact data
- **Team 3 (LinkedIn Automation)** → Retrieves contacts and logs actions

Ensure API contracts match the schemas defined in `context.md`.
