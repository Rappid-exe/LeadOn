# Sales Workflow Agentic System - Hackathon Project

## 🎯 Project Overview

An intelligent sales automation system that enriches a CRM database through web scraping, then automatically nurtures relationships with prospects via LinkedIn automation. The system replaces manual CRM management by automatically tracking all outreach actions.

### Core Workflow
1. **User Input** → Natural language prompt (e.g., "I want to fundraise for my AI company")
2. **Scraping & Enrichment** → Scrapers pull data from Apollo.io, job sites, etc.
3. **CRM Auto-Population** → Agents automatically add/update contacts in CRM
4. **Relationship Nurturing** → LinkedIn automation (likes, comments, endorsements, messages)
5. **Action Tracking** → All interactions automatically logged in CRM

---

## 🏗️ System Architecture

```
User Prompt → Scrapers → CRM Database → LinkedIn Automation → Action Logging (back to CRM)
```

### Technology Stack
- **Backend**: Python (FastAPI/Flask recommended)
- **Database**: PostgreSQL/SQLite for CRM
- **Scraping**: BeautifulSoup, Scrapy, Selenium
- **Automation**: Selenium for LinkedIn
- **AI/LLM**: OpenAI API or similar for prompt understanding
- **Queue System**: Celery/Redis for async tasks

---

## 👥 Team Structure & Responsibilities

### **TEAM 1: SCRAPER TEAM** 🕷️
**Objective**: Build scrapers that extract lead data and an agent that automatically populates the CRM

#### Responsibilities:
1. **Apollo.io Scraper**
   - Extract: Name, Title, Company, Email, LinkedIn URL, Phone
   - Handle authentication/API if available
   - Implement rate limiting and error handling

2. **Job Sites Scraper** (LinkedIn Jobs, Indeed, etc.)
   - Identify companies posting relevant jobs (e.g., marketing jobs = marketing service leads)
   - Extract: Company name, job title, posting date, company LinkedIn
   - Map job postings to potential lead opportunities

3. **CRM Population Agent**
   - Parse scraped data into standardized format
   - Deduplicate entries (check if contact already exists)
   - Auto-categorize leads based on scraped data
   - Insert/update CRM database with enriched information
   - Tag contacts based on user prompt context

#### Key Files to Create:
- `scrapers/apollo_scraper.py`
- `scrapers/job_sites_scraper.py`
- `scrapers/base_scraper.py` (abstract base class)
- `agents/crm_population_agent.py`
- `scrapers/utils.py` (rate limiting, proxies, etc.)

#### AI Development Guidelines for Team 1:
```
When working with AI on scraping:
- Always request: "Build a scraper for [source] that extracts [fields] with error handling and rate limiting"
- Specify: "Use Selenium for dynamic content, BeautifulSoup for static HTML"
- Include: "Add retry logic with exponential backoff"
- Request: "Create a data validation schema using Pydantic"
- Ask for: "Implement proxy rotation to avoid IP bans"
```

---

### **TEAM 2: CRM TEAM** 💾
**Objective**: Build the CRM database schema and API for storing/retrieving contact data and action logs

#### Responsibilities:
1. **Database Schema Design**
   - Contacts table (id, name, title, company, email, linkedin_url, phone, tags, source, created_at)
   - Actions table (id, contact_id, action_type, action_details, timestamp, status)
   - Campaigns table (id, user_prompt, created_at, target_tags)
   - Relationships table (contact_id, relationship_stage, last_interaction)

2. **CRM API Development**
   - CRUD endpoints for contacts
   - Action logging endpoints
   - Search/filter contacts by tags, company, title
   - Get contact history (all actions performed)
   - Bulk operations (import, export, update)

3. **Action Tracking System**
   - Log every action: "connection_request_sent", "post_liked", "comment_posted", "message_sent", "endorsed"
   - Track timestamps and status (pending, completed, failed)
   - Update contact relationship stage based on actions

4. **Dashboard/UI** (Optional, if time permits)
   - View all contacts
   - Filter by tags, actions, relationship stage
   - Manual contact editing

#### Key Files to Create:
- `crm/database.py` (SQLAlchemy models)
- `crm/schemas.py` (Pydantic schemas)
- `crm/api.py` (FastAPI routes)
- `crm/crud.py` (database operations)
- `crm/action_logger.py`
- `migrations/` (Alembic migrations)

#### AI Development Guidelines for Team 2:
```
When working with AI on CRM:
- Request: "Create SQLAlchemy models for [entity] with relationships to [other entities]"
- Specify: "Build FastAPI CRUD endpoints with Pydantic validation"
- Include: "Add database indexes for frequently queried fields"
- Ask for: "Implement soft deletes and audit trails"
- Request: "Create migration scripts using Alembic"
- Specify: "Add full-text search capabilities for contact search"
```

---

### **TEAM 3: LINKEDIN AUTOMATION TEAM** 🤖
**Objective**: Build Selenium scripts that automate LinkedIn interactions and log actions to CRM

#### Responsibilities:
1. **LinkedIn Authentication**
   - Login automation with session persistence
   - Handle 2FA/security challenges
   - Cookie management for multiple accounts

2. **Engagement Automation**
   - **Like Posts**: Navigate to profile, find recent posts, like them
   - **Comment on Posts**: Generate contextual comments (AI-powered), post comments
   - **Endorse Skills**: Go to profile, endorse top skills
   - **Send Connection Request**: With personalized message
   - **Send Direct Message**: After connection accepted

3. **Action Execution Flow**
   - Receive contact list from CRM
   - Determine action sequence based on relationship stage
   - Execute actions with human-like delays (randomized timing)
   - Handle errors (profile not found, already connected, etc.)
   - Log each action back to CRM via API

4. **Safety & Rate Limiting**
   - Implement daily action limits (LinkedIn restrictions)
   - Random delays between actions (5-30 seconds)
   - Avoid detection patterns
   - Graceful error handling and retries

#### Key Files to Create:
- `linkedin_automation/linkedin_bot.py` (main bot class)
- `linkedin_automation/actions/like_post.py`
- `linkedin_automation/actions/comment_post.py`
- `linkedin_automation/actions/endorse_skills.py`
- `linkedin_automation/actions/send_connection.py`
- `linkedin_automation/actions/send_message.py`
- `linkedin_automation/session_manager.py`
- `linkedin_automation/action_scheduler.py`

#### AI Development Guidelines for Team 3:
```
When working with AI on LinkedIn automation:
- Request: "Create a Selenium script to [action] on LinkedIn with error handling"
- Specify: "Add random delays between 5-30 seconds to mimic human behavior"
- Include: "Handle common exceptions: ElementNotFound, TimeoutException, StaleElementReference"
- Ask for: "Implement headless mode with user-agent rotation"
- Request: "Create a session manager that persists cookies across runs"
- Specify: "Add logging for each action with screenshots on failure"
- Include: "Implement action queue with priority levels"
```

---

## 🔄 Integration Flow

### End-to-End Process:

1. **User submits prompt**: "I want to fundraise for my AI company"

2. **Prompt Analysis** (AI Agent):
   - Extract intent: fundraising
   - Extract industry: AI
   - Determine target personas: VCs, angel investors, startup accelerators

3. **Scraping Phase** (Team 1):
   - Apollo.io: Search for VCs, investors in AI space
   - Job sites: Find companies hiring AI roles (potential partners)
   - Return structured data

4. **CRM Population** (Team 1 → Team 2):
   - Agent calls CRM API to insert contacts
   - Tags: "vc", "ai_investor", "fundraising_target"
   - Status: "new_lead"

5. **Automation Phase** (Team 3):
   - Query CRM for contacts with tag "fundraising_target"
   - For each contact:
     - Day 1: Like recent post
     - Day 2: Comment on post
     - Day 3: Endorse skills
     - Day 4: Send connection request with personalized message
     - Day 7: Send follow-up message (if connected)

6. **Action Logging** (Team 3 → Team 2):
   - After each action, call CRM API to log:
     - `POST /api/actions` with contact_id, action_type, timestamp

---

## 📋 Shared Data Contracts

### Contact Schema (JSON)
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

### Action Schema (JSON)
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

### Action Types (Enum)
- `post_liked`
- `comment_posted`
- `skill_endorsed`
- `connection_request_sent`
- `message_sent`
- `profile_viewed`

---

## 🚀 Development Workflow

### Phase 1: Setup (All Teams)
- [ ] Set up project structure
- [ ] Create virtual environment
- [ ] Install dependencies
- [ ] Set up database (Team 2)
- [ ] Create `.env` file for credentials

### Phase 2: Parallel Development
- [ ] **Team 1**: Build scrapers + test with sample data
- [ ] **Team 2**: Build database + API + test endpoints
- [ ] **Team 3**: Build LinkedIn bot + test individual actions

### Phase 3: Integration
- [ ] Team 1 → Team 2: Test scraper to CRM flow
- [ ] Team 2 → Team 3: Test CRM to automation flow
- [ ] End-to-end test with real user prompt

### Phase 4: Polish
- [ ] Add error handling everywhere
- [ ] Add logging and monitoring
- [ ] Create simple UI/dashboard
- [ ] Prepare demo

---

## 🛠️ AI Collaboration Best Practices

### For ALL Teams:

1. **Be Specific with AI Requests**
   ```
   ❌ Bad: "Create a scraper"
   ✅ Good: "Create a Python scraper using Selenium that extracts name, title, and company from Apollo.io search results, with error handling for missing elements and rate limiting of 1 request per 2 seconds"
   ```

2. **Request Modular Code**
   - Ask for separate functions/classes for each responsibility
   - Request type hints and docstrings
   - Ask for unit tests

3. **Iterate Incrementally**
   - Build one feature at a time
   - Test before moving to next feature
   - Ask AI to review/refactor code

4. **Use This Context File**
   - Reference this file when asking AI for help
   - Example: "Based on the context.md file, create the apollo_scraper.py following Team 1 guidelines"

5. **Share Code Snippets**
   - When integrating, share relevant schemas/interfaces
   - Ensure consistent naming conventions

---

## 📦 Project Structure

```
sales-workflow-agentic/
├── scrapers/
│   ├── __init__.py
│   ├── base_scraper.py
│   ├── apollo_scraper.py
│   ├── job_sites_scraper.py
│   └── utils.py
├── agents/
│   ├── __init__.py
│   ├── crm_population_agent.py
│   └── prompt_analyzer.py
├── crm/
│   ├── __init__.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── api.py
│   ├── crud.py
│   └── action_logger.py
├── linkedin_automation/
│   ├── __init__.py
│   ├── linkedin_bot.py
│   ├── session_manager.py
│   ├── action_scheduler.py
│   └── actions/
│       ├── __init__.py
│       ├── like_post.py
│       ├── comment_post.py
│       ├── endorse_skills.py
│       ├── send_connection.py
│       └── send_message.py
├── tests/
│   ├── test_scrapers/
│   ├── test_crm/
│   └── test_automation/
├── migrations/
├── .env.example
├── requirements.txt
├── context.md (this file)
└── README.md
```

---

## 🔐 Environment Variables

Create a `.env` file with:
```
# Database
DATABASE_URL=postgresql://user:pass@localhost/sales_crm

# LinkedIn Credentials
LINKEDIN_EMAIL=your_email@example.com
LINKEDIN_PASSWORD=your_password

# Apollo.io
APOLLO_API_KEY=your_api_key

# OpenAI (for AI features)
OPENAI_API_KEY=your_openai_key

# Rate Limiting
MAX_DAILY_LINKEDIN_ACTIONS=50
SCRAPER_DELAY_SECONDS=2
```

---

## 🎯 Success Criteria

- [ ] User can input a natural language prompt
- [ ] Scrapers successfully extract at least 20 contacts per prompt
- [ ] CRM stores and retrieves contacts via API
- [ ] LinkedIn bot can perform all 5 actions (like, comment, endorse, connect, message)
- [ ] All actions are logged back to CRM with timestamps
- [ ] System runs end-to-end without manual intervention
- [ ] Demo-ready with sample data

---

## 🚨 Important Notes

### For Team 1 (Scrapers):
- **Respect rate limits** - Apollo.io and job sites will block you
- **Use proxies** if scraping at scale
- **Validate data** before inserting to CRM
- **Handle missing fields** gracefully

### For Team 2 (CRM):
- **Use database transactions** for data integrity
- **Index frequently queried fields** (linkedin_url, tags)
- **Implement pagination** for large result sets
- **Add API authentication** (JWT tokens)

### For Team 3 (LinkedIn Automation):
- **LinkedIn has strict limits** - max 100 connection requests/week
- **Use random delays** - 5-30 seconds between actions
- **Handle CAPTCHA** - may need manual intervention
- **Session persistence** - save cookies to avoid re-login
- **Headless mode** - use `--headless=new` for production

---

## 📞 Team Communication

### Daily Standup Questions:
1. What did you complete yesterday?
2. What are you working on today?
3. Any blockers or dependencies on other teams?

### Integration Points (Critical):
- **Team 1 → Team 2**: Contact data format, API endpoint for insertion
- **Team 2 → Team 3**: Contact retrieval API, action logging endpoint
- **Team 3 → Team 2**: Action schema, status updates

---

## 🏁 Quick Start Commands

```bash
# Setup
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run database migrations (Team 2)
alembic upgrade head

# Start API server (Team 2)
uvicorn crm.api:app --reload

# Run scraper (Team 1)
python scrapers/apollo_scraper.py --query "AI investors"

# Run LinkedIn bot (Team 3)
python linkedin_automation/linkedin_bot.py --contact-id <uuid>
```

---

## 🎓 Learning Resources

- **Selenium**: https://selenium-python.readthedocs.io/
- **FastAPI**: https://fastapi.tiangolo.com/
- **SQLAlchemy**: https://docs.sqlalchemy.org/
- **Web Scraping**: https://realpython.com/beautiful-soup-web-scraper-python/

---