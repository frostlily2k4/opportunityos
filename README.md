# OpportunityOS — Your AI Opportunity Agent

> **Read. Reason. Act.**

OpportunityOS is an AI-powered opportunity discovery agent that helps students find and act on relevant **internships, hackathons, scholarships, and competitions**.

Instead of simply returning a list of links, OpportunityOS:

1. 🔎 Searches the live web
2. 📖 Reads and extracts opportunity requirements
3. ✅ Checks eligibility against the user's profile
4. 🎯 Scores and ranks opportunities
5. 📋 Generates an application checklist
6. ✉️ Creates a tailored application draft

### Example

```text
"Find me 5 AI internships I can apply to this week"

The agent searches live opportunities, understands their requirements, checks whether the student is eligible, ranks the best matches, and prepares the next steps.

🚀 Why OpportunityOS?

Most opportunity-finder tools stop at:

"Here are some opportunities."

OpportunityOS goes one step further:

"Here are the opportunities you are most likely to benefit from — and here's what you should do next."

The Act stage is the key differentiator.

For each actionable opportunity, the agent can generate:

A concrete application checklist
Eligibility reasons
A fit score
A score rationale
A tailored application email / cover note

The system intentionally does not automatically submit applications on third-party websites. Instead, it prepares the user to complete the application themselves safely and transparently.

🧠 Agent Architecture
                    User Query
                        │
                        ▼
              ┌──────────────────┐
              │   1. SEARCH      │
              │   Tavily API     │
              └────────┬─────────┘
                       │
                       ▼
              ┌──────────────────┐
              │   2. EXTRACT     │
              │   Gemini         │
              └────────┬─────────┘
                       │
                       ▼
              ┌──────────────────┐
              │ 3. ELIGIBILITY   │
              │   Gemini         │
              └────────┬─────────┘
                       │
                       ▼
              ┌──────────────────┐
              │    4. SCORE      │
              │   Gemini         │
              └────────┬─────────┘
                       │
                       ▼
              ┌──────────────────┐
              │    5. RANK       │
              │    Top 5         │
              └────────┬─────────┘
                       │
                       ▼
              ┌──────────────────┐
              │     6. ACT       │
              │ Checklist +      │
              │ Application Draft│
              └────────┬─────────┘
                       │
                       ▼
                 Best Matches
🛠️ Tech Stack
Frontend
Next.js
React
Plain CSS
Server-Sent Events (SSE) for live pipeline updates
Backend
FastAPI
Python
Async pipeline orchestration
AI Reasoning
Google Gemini 2.5 Flash
Used for:
Opportunity extraction
Eligibility reasoning
Opportunity scoring
Application checklist generation
Tailored application draft generation
Web Search
Tavily API
Used to search the live web and retrieve webpage content for the agent.
Reliability
Local query caching
Cached fallback when live search temporarily fails
Explicit pipeline error reporting
JSON-structured AI outputs
✨ Key Features
🔎 Live Opportunity Discovery

Search for opportunities using natural language.

Examples:

AI internships in India

Machine learning internships for undergraduate students

AI hackathons I can participate in

Scholarships for AI students
📖 Requirement Extraction

The agent reads webpage content and extracts structured information such as:

Opportunity title
Organization
Opportunity type
Deadline
Location
Eligibility requirements
Required documents
Stipend / prize
Application URL
Summary

Generic search pages, social posts, discussions, and non-opportunity pages are filtered out.

✅ Eligibility Checking

The user's profile is compared against the opportunity.

The agent considers:

Education
Skills
Location
Experience
Work authorization when relevant
Application deadline

The system can return:

Eligible
Ineligible
Eligibility unclear
Expired

Expired opportunities are automatically excluded from the final actionable ranking.

🎯 Intelligent Ranking

Every actionable opportunity receives a 0–100 fit score.

The score considers:

Eligibility fit
Skills and interests
Deadline/actionability
Opportunity value
Learning potential
Prize / stipend when available

The UI also explains:

Why this matches

so the user can understand the recommendation instead of receiving a mysterious number.

📋 Application Checklist

For actionable opportunities, the agent generates an ordered checklist based on the actual requirements found on the opportunity page.

Example:

☐ Verify student eligibility
☐ Prepare resume
☐ Prepare required project links
☐ Complete application form
☐ Review submitted information
☐ Submit before the deadline

The checklist is generated from the opportunity information rather than blindly applying a generic template.

✉️ Tailored Application Draft

The agent can generate a short application email or cover note tailored to:

The opportunity
The student's education
Their skills
Their interests
Their actual projects or experience

The user can copy, edit, and send the draft.

🔐 Safe & Transparent "Act" Stage

OpportunityOS deliberately does not automatically submit applications.

Automatically submitting applications across third-party websites can be fragile, unreliable, and may conflict with website policies.

Instead, the agent prepares the user to act:

Discover
   ↓
Understand
   ↓
Verify
   ↓
Rank
   ↓
Prepare
   ↓
User submits

This keeps the human in control while still providing meaningful automation.

🛡️ Reliability & Demo Resilience

Live web applications can fail because of network problems, API limits, or temporary service issues.

OpportunityOS includes a caching fallback.

Cache

Successful search results are cached locally.

If the same query is run again and live search temporarily fails, the system can use the cached result instead of failing immediately.

The UI also reports failures honestly rather than pretending the agent succeeded.

Example:

Live search failed — using a cached run for this query.

This makes the system more reliable during demonstrations.

📁 Project Structure
opportunityos/
│
├── README.md
├── .gitignore
│
├── backend/
│   ├── .env.example
│   ├── main.py
│   ├── requirements.txt
│   │
│   └── agent/
│       ├── __init__.py
│       ├── cache.py
│       ├── checklist.py
│       ├── eligibility.py
│       ├── extract.py
│       ├── llm.py
│       ├── pipeline.py
│       ├── scoring.py
│       └── search.py
│
└── frontend/
    ├── next.config.js
    ├── package.json
    ├── package-lock.json
    │
    ├── pages/
    │   ├── _app.js
    │   └── index.js
    │
    └── styles/
        └── globals.css
⚙️ Local Setup
1. Clone the repository
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd opportunityos
2. Create the Python environment
Windows
python -m venv .venv
.venv\Scripts\activate
macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
3. Install backend dependencies
cd backend
pip install -r requirements.txt
4. Configure API keys

Create:

backend/.env

using .env.example as a template.

Add:

GEMINI_API_KEY=your_gemini_api_key
TAVILY_API_KEY=your_tavily_api_key

Never commit .env to GitHub.

5. Start the backend

From the backend directory:

uvicorn main:app --reload --port 8000

The backend will run on:

http://localhost:8000
6. Install frontend dependencies

Open another terminal:

cd frontend
npm install
7. Start the frontend
npm run dev

Open:

http://localhost:3000

The Next.js application proxies /api/* requests to the FastAPI backend.

🔑 API Keys

OpportunityOS requires:

Google Gemini

Used for AI reasoning and structured generation.

Get a Gemini API key from Google's AI developer platform.

Tavily

Used for live web search and webpage content retrieval.

A Tavily API key is required for opportunity discovery.

API keys should always remain server-side and must never be exposed in frontend code or committed to the repository.

🔄 Agent Pipeline

The complete pipeline is:

User Query
     │
     ▼
Live Search
     │
     ▼
Web Content
     │
     ▼
Opportunity Extraction
     │
     ▼
Generic Page Filtering
     │
     ▼
Eligibility Analysis
     │
     ▼
Opportunity Scoring
     │
     ▼
Expired / Ineligible Filtering
     │
     ▼
Top Opportunities
     │
     ▼
Application Checklist
     │
     ▼
Tailored Application Draft

Each stage sends progress updates to the frontend so users can see what the agent is doing.

🎥 Demo Flow

A typical demonstration can follow this flow:

1. Enter a query
Find me AI internships I can apply to this week
2. Add a student profile

Example:

Education: B.Sc Artificial Intelligence & Machine Learning
Skills: Python, Machine Learning, R
Location: India
Interests: AI, Data Science
3. Run the agent

The UI displays:

Search
   ↓
Read
   ↓
Check
   ↓
Score
   ↓
Act
4. Review the results

Each result shows:

Fit score
Eligibility
Deadline
Summary
Match rationale
Application checklist
Tailored application draft
Application link

💡 What Makes It Different?

Traditional opportunity platforms:

Search → List opportunities

OpportunityOS:

Search
  ↓
Read
  ↓
Reason
  ↓
Verify eligibility
  ↓
Score
  ↓
Prepare action

The goal is not just to help students find opportunities.

It is to reduce the gap between:

"I found an opportunity."

and

"I'm ready to apply."

🚧 Future Improvements

Potential future extensions include:

Deadline calendar / .ics export
Persistent student profiles
More specialized searches for each opportunity type
Personalized notifications
Opportunity tracking
Application status tracking
More advanced agent actions with user approval
Additional web sources

🏆 Hackathon Project

Built for the Anakin Forge Hackathon.

Theme

Build AI Agents That Read, Reason, and Act

OpportunityOS demonstrates this through a multi-stage agent that:

Reads live opportunity information →
Reasons about eligibility and relevance →
Acts by preparing the user for the application.

License

This project was created as a hackathon prototype.


