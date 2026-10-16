# job-matcher

A tool I'm building to help with my own Summer 2027 internship search. It pulls internship postings from company job boards, turns each one into a structured record (skills, degree, grad dates, location, work authorization), compares it against my resume, and keeps track of which skills keep showing up across the roles I'm looking at.

Still in progress. I started it in September 2026 and I'm using it on real applications as I build it.

## Why build this instead of pasting postings into ChatGPT

Pasting one posting and one resume into a chatbot works for a single job, but it falls short for a whole search:

- It doesn't watch for new postings. Most internships are reviewed on a rolling basis, so I want to know when a matching role opens, not find out two weeks later.
- It doesn't remember anything between postings, so it can't tell me which skills show up most across 50+ roles or which of those I'm missing.
- The output format changes every time, so nothing can be stored or compared.
- There's no way to know how often it gets things wrong. I'm measuring extraction accuracy against postings I labeled myself (see Evaluation below).

## What it does (planned)

| Feature | Status |
|---|---|
| Requirement extraction: posting text to a structured record | In progress |
| Resume match and gap report: fit, missing skills, which of my experiences to highlight | Planned |
| Application tracker in SQLite | Planned |
| Skill trends: most-requested skills across saved postings, and my gaps | Planned |
| New-posting alerts: scheduled checks of target companies' job boards | Planned |

Things it won't do:

- Auto-apply to jobs
- Make up resume content. Suggestions only use experience I actually have.
- Scrape LinkedIn, Indeed, or any site whose terms don't allow it

## How it's put together

```
posting text / job board feed        my resume
            |                            |
            v                            v
   +-------------- agent (LLM + tools) --------------+
   | fetch_postings, extract_requirements,           |
   | match_resume, check_tracker, save_posting       |
   +-------------------------------------------------+
            |                            |
            v                            v
      SQLite database  ------------>  skill trends report
            |
            v
   scheduled check  ---->  alert for a new matching posting
```

The LLM only does the parts that need reading comprehension: pulling requirements out of messy posting text and judging resume fit. Everything with a definite right answer (scheduling, duplicate detection, database writes, checking whether my grad date falls in a posting's window) is regular Python, so it's predictable and testable.

More detail, including the data model and the open questions I haven't settled yet, is in [docs/DESIGN.md](docs/DESIGN.md).

## Stack

- Python 3.11
- Pydantic for the data model and for validating LLM output
- SQLite for storage
- LLM: comparing Gemini (free tier) against a local model through Ollama before picking one
- FastAPI, a scheduler, and hosting are still to be decided
- pytest and GitHub Actions for tests and CI

## Running it

Not much to run yet. Current setup:

```bash
git clone https://github.com/Asaini434/job-matcher.git
cd job-matcher

conda create -n jobmatcher python=3.11
conda activate jobmatcher
pip install -r requirements.txt

# API key goes in .env, which is gitignored
cp .env.example .env    # then paste your Gemini key into .env

# check that every hand label matches the data model
PYTHONPATH=src python scripts/validate_labels.py
```

## Evaluation

I labeled 14 real postings following the rules in [docs/LABELLING.md](docs/LABELLING.md). Four of them are a dev set I use while writing prompts; the other ten are held out as the test set and only used to report results. Ten postings is a small sample, so the numbers will be a rough estimate.

What I'll measure:

- Precision and recall on required skills
- Exact-match accuracy on fields like employment type, work mode, and grad dates
- How often the model fills in something the posting never said (for example, guessing a sponsorship policy)

| Metric | Gemini | Local (Ollama) |
|---|---|---|
| Required-skill precision | - | - |
| Required-skill recall | - | - |

The raw posting text isn't in the repo since it's the companies' content. Each label includes the posting's source URL.

## Roadmap

- [x] Week 1: design doc, repo setup, labeled postings
- [ ] Week 2: requirement extraction, compare two LLM providers
- [ ] Week 3: resume parsing, match and gap logic
- [ ] Week 4: agent loop and tools
- [ ] Week 5: SQLite tracker and skill trends
- [ ] Week 6: new-posting alerts
- [ ] Week 7: evaluation, tests, CI, deployment
- [ ] Week 8: demo and cleanup

## Notes so far

Labeling postings by hand turned up more design problems than I expected:

- Many postings ask for "at least one of Java, Python, C++...", which my data model can't express yet. Listing all of them as required makes the gap report look worse than it should.
- Job links carry tracking parameters (`?utm_source=...`), so the same posting can show up under different URLs. Duplicate checks need to strip those or use the company's requisition ID.
- Some careers pages load the job description with JavaScript, so a plain HTTP request only gets an empty page.
- "Full time" on an internship usually describes the hours, not the type of role.

## Author

Ananya Saini, M.S. Computer Science, George Mason University
