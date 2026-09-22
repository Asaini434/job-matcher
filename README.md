# Job Posting Matcher Agent

> 🚧 **Status: In development** (started September 2026). Features below are marked ✅ done or ⬜ planned. This README will be updated as each milestone ships.

An LLM-powered agent that tracks internship postings, extracts their requirements into structured data, matches them against my resume, and surfaces which skills the market is asking for, so I can apply to the right roles early.

I'm building it for my own Summer 2027 internship search and using it on real applications as I go.

---

## Why not just paste postings into ChatGPT?

A chatbot can compare one posting to one resume. It can't:

- **Watch for new postings.** It only responds when asked. This agent checks target companies' job boards on a schedule and alerts me when a matching role opens. Most companies review applications on a rolling basis, so applying early matters.
- **Remember across postings.** This agent stores every posting it has seen, so it can answer questions like *"Which skills appear most across the 60 roles I'm targeting, and which am I missing?"*
- **Tell you how accurate it is.** I measure this agent's extraction accuracy against postings I labeled by hand (see [Evaluation](#evaluation)).
- **Give consistent output.** Every posting becomes the same structured record, stored and searchable.

---

## Features

| Feature | Status |
|---|---|
| ⭐ **New-posting alerts**: scheduled checks of target companies' job boards | ⬜ Planned |
| ⭐ **Skill trend insights**: most-requested skills across saved postings, and my gaps | ⬜ Planned |
| **Requirement extraction**: posting text → structured data (required and preferred skills, degree, location, work authorization) | ⬜ Planned |
| **Resume match and gap report**: fit score with reasons, missing skills, which real experiences to highlight | ⬜ Planned |
| **Application tracker**: postings and application status in a database | ⬜ Planned |

⭐ = headline features

### Non-goals

- Does **not** auto-apply to jobs
- Does **not** invent resume content. Suggestions only draw on real experience.
- Does **not** scrape LinkedIn, Indeed, or any site whose terms prohibit it

---

## Architecture

```
[Posting text / job-board feed]      [My resume]
              │                           │
              ▼                           ▼
        ┌──────────────── Agent (LLM + tools) ────────────────┐
        │ tools: fetch_postings, extract_requirements,        │
        │        match_resume, check_tracker, save_posting    │
        └─────────────────────────────────────────────────────┘
              │                                   │
              ▼                                   ▼
        SQLite database  ─────────────►  Skill trends report
              │
              ▼
     Scheduled check  ──►  Alert (new matching posting)
```

The LLM decides which tools to call and in what order. Scheduling and database writes stay as regular code, so they're predictable and testable. Design reasoning is in [`docs/DESIGN.md`](docs/DESIGN.md).

---

## Tech stack

| Part | Choice |
|---|---|
| Language | Python |
| LLM provider | _TBD_ |
| Backend | FastAPI |
| Data validation | Pydantic |
| Database | SQLite |
| Scheduler | _TBD_ |
| Tests / CI | pytest, GitHub Actions |
| Hosting | _TBD_ |

---

## Getting started

> ⚠️ Setup steps will be finalized once the first milestone is built.

```bash
# 1. Clone the repo
git clone https://github.com/<your-username>/<repo-name>.git
cd <repo-name>

# 2. Create the conda environment
conda create -n jobmatcher python=3.11
conda activate jobmatcher

# 3. Install dependencies (requirements.txt added in week 2)
pip install -r requirements.txt

# 4. Add your LLM API key to a .env file (never commit this file)
echo "LLM_API_KEY=your-key-here" > .env
```

---

## Evaluation

> ⬜ Planned for week 7. Results will be filled in here.

- **Dataset:** 20–30 real internship postings, required skills labeled by hand
- **Metrics:** precision and recall of extracted required skills; spot-checked match scores
- **Failure analysis:** which kinds of postings the extractor gets wrong, and why

| Metric | Result |
|---|---|
| Required-skill precision | _TBD_ |
| Required-skill recall | _TBD_ |

---

## Roadmap

- [ ] Week 1: Design doc, repo setup, hand-label 20–30 postings
- [ ] Week 2: Requirement extraction (structured output)
- [ ] Week 3: Resume parsing, match and gap logic
- [ ] Week 4: Agent loop and tools
- [ ] Week 5: SQLite tracker and skill trends ⭐
- [ ] Week 6: New-posting alerts ⭐
- [ ] Week 7: Evaluation, tests, CI, deployment
- [ ] Week 8: Demo video, polish

---

## What I learned

_To be written as the project progresses._

---

## Author

**Ananya Saini**, M.S. Computer Science, George Mason University