# LinkedIn Automation Bot

Selenium-based LinkedIn automation for engagement actions (likes, endorsements, connections).

## Setup

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Install ChromeDriver:**
   - Download from: https://chromedriver.chromium.org/downloads
   - Or use: `pip install webdriver-manager` (auto-manages drivers)
   - Ensure ChromeDriver is in your PATH

3. **Configure credentials:**
```bash
cp .env.example .env
# Edit .env with your LinkedIn credentials
```

## Usage

### Test Script (Interactive)
```bash
python test_bot.py
```

### Programmatic Usage
```python
from linkedin_automation.linkedin_bot import LinkedInBot

bot = LinkedInBot(headless=False)

try:
    if bot.start():
        # Like posts
        bot.like_posts("https://www.linkedin.com/in/profile/", max_posts=3)
        
        # Endorse skills
        bot.endorse("https://www.linkedin.com/in/profile/", max_skills=3)
        
        # Send connection
        bot.connect("https://www.linkedin.com/in/profile/", 
                   message="Hi! Let's connect!")
        
        # Or run full sequence
        bot.run_engagement_sequence(
            profile_url="https://www.linkedin.com/in/profile/",
            include_connection=True,
            connection_message="Hi! I'd love to connect."
        )
finally:
    bot.stop()
```

## Features

- **Session Management**: Cookie persistence to avoid repeated logins
- **Anti-Detection**: Random delays, human-like behavior, user-agent spoofing
- **Error Handling**: Graceful failures with detailed error reporting
- **Action Tracking**: All actions logged with results

## Safety Notes

- LinkedIn limits: ~100 connection requests/week
- Random delays: 5-30 seconds between actions
- Use responsibly to avoid account restrictions

## Project Structure

```
linkedin_automation/
├── __init__.py
├── linkedin_bot.py          # Main bot class
├── session_manager.py       # Authentication & cookies
└── actions/
    ├── like_post.py         # Like posts action
    ├── endorse_skills.py    # Endorse skills action
    └── send_connection.py   # Connection request action
```
