# Design Doc: Job Posting Matcher Agent

**Author:** Ananya Saini
**Status:** Draft (Week 1)

## 1. Problem and goal

Internship postings open on a rolling basis across many company job boards, and applying early matters. Checking boards by hand is slow, and comparing each posting to my resume one at a time (for example, pasting it into a chatbot) doesn't scale: a chatbot doesn't watch for new postings, doesn't remember postings across sessions, gives inconsistently formatted answers, and gives no measure of its own accuracy.

**Goal:** a tool that finds new internship postings from target companies, extracts their requirements into consistent structured records, checks my eligibility and fit against my resume, and summarizes which skills are most in demand across the roles I'm targeting, with measured extraction accuracy.

## 2. Use cases

1. **New postings:** "Which new postings from my target companies appeared since the last check, and which do I qualify for?"
2. **Fit and gaps:** "For this posting, how well does my resume match, which required skills am I missing, and which of my real experiences should I highlight?"
3. **Skill trends:** "Across all saved postings, which skills are requested most often, and which of those am I missing?"
4. **Eligibility filter:** "Hide postings where my degree level, graduation date, or work authorization clearly doesn't fit."
5. **Tracking:** "Which postings have I applied to, and what stage is each one at?"

## 3. Scope

**In scope (8 weeks):**
- Requirement extraction from posting text into the data model in Section 4
- Resume matching and gap report
- SQLite storage for postings and applications
- Skill trend report
- Scheduled checks of target companies' job boards, with alerts for new matching postings
- Evaluation of extraction accuracy on hand-labeled postings

**Non-goals:**
- Does not auto-apply to jobs
- Does not invent resume content; suggestions only draw on real experience
- Does not scrape LinkedIn, Indeed, or any site whose terms prohibit automated access
- Not a multi-user product; built for one user (me)

## 4. Data model

Missing information is stored as `null` (or an empty list), never guessed.
Dates are stored as ISO 8601 text: `YYYY-MM-DD`.

### Table: `postings`
Facts about the company's job posting.

| Field | Type | Set by | Description |
|---|---|---|---|
| `id` | integer | code | Primary key |
| `company` | string | LLM | Company name |
| `title` | string | LLM | Job title as written |
| `source_url` | string, unique | code | Link to the original posting; used to detect duplicates |
| `external_id` | string or null | code | The job board's own ID for the posting, if it has one |
| `source` | string | code | Where it was found (e.g. a company careers page) |
| `first_seen_at` | datetime | code | When this tool first found the posting; used for "new posting" alerts and trends |
| `last_seen_at` | datetime | code | Last time a check saw it still listed; helps detect closed postings |
| `date_posted` | date or null | LLM | Posting date, if stated |
| `employment_type` | enum: `internship`, `full_time`, `part_time`, `co_op`, `unknown` | LLM | Type of role as stated |
| `term` | string or null | LLM | Season/year, e.g. "Summer 2027" |
| `locations` | list of {city, state, country} | LLM | All listed locations; empty list if none stated |
| `work_mode` | enum: `onsite`, `hybrid`, `remote`, `unknown` | LLM | Work arrangement as stated |
| `required_skills` | list of strings | LLM | Skills listed as required, in normalized form (see Open Questions) |
| `preferred_skills` | list of strings | LLM | Skills listed as preferred / nice-to-have |
| `degree_levels` | list of enum: `bachelors`, `masters`, `phd` | LLM | Eligible degree levels; empty list if not stated |
| `grad_date_earliest` | date or null | LLM | Earliest graduation date accepted, if stated |
| `grad_date_latest` | date or null | LLM | Latest graduation date accepted, if stated |
| `requires_work_authorization` | boolean or null | LLM | Posting says candidates must already be authorized to work in the US |
| `sponsorship_available` | boolean or null | LLM | Posting says whether visa sponsorship is offered |
| `accepts_cpt_opt` | boolean or null | LLM | Posting explicitly says CPT/OPT candidates are eligible |
| `raw_text` | string | code | Full posting text (kept locally, not committed); lets extraction be re-run and evaluated |
| `extracted_at` | datetime | code | When the LLM extraction ran |
| `extraction_model` | string | code | Which model/prompt version produced the extraction |

### Table: `applications`
My own actions. At most one row per posting.

| Field | Type | Description |
|---|---|---|
| `id` | integer | Primary key |
| `posting_id` | integer, unique | Foreign key → `postings.id` |
| `status` | enum: `planned`, `applied`, `online_assessment`, `interviewing`, `offer`, `rejected`, `withdrawn` | Current stage |
| `applied_date` | date or null | Date submitted; null while `planned` |
| `resume_version` | string or null | Which version of my resume I used |
| `notes` | string or null | Free-form notes (referral, recruiter name, etc.) |
| `updated_at` | datetime | Last time this row changed |

## 5. Architecture

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

**Division of work: the LLM extracts, code decides.**
- **The LLM** is used only where understanding natural language is necessary: turning posting text into a structured record, judging resume fit, and choosing which tool to call next in the agent loop.
- **Plain code** handles everything that has a correct answer: scheduling, duplicate detection (via `source_url` / `external_id`), database writes, and eligibility checks (e.g. comparing my graduation date to `grad_date_earliest` / `grad_date_latest`).
- **Why:** code is predictable and testable with pytest; LLM output varies between runs. Keeping hard rules in code means an eligibility decision never depends on the model's mood.

**Validation:** every LLM extraction is validated against a Pydantic model that mirrors Section 4. Invalid output (a wrong type, an enum value not in the allowed list) is rejected, not stored.

**Swappable provider:** all LLM calls go through one function, `extract_requirements(text) -> Posting`, so providers can be compared and swapped by changing one module.

## 6. Evaluation plan

**Dataset:** 20–30 real internship postings, labeled by hand using the Section 4 fields. Labels are written *before* running any extractor, so they aren't influenced by model output.

**Split:** about one-third *dev set* (used while writing and tuning prompts) and two-thirds *test set* (only used to report final results). Tuning on the same postings used for reporting would overstate accuracy.

**Metrics:**
- **Required-skill precision:** of the skills the extractor listed, what fraction are in my labels
- **Required-skill recall:** of the skills in my labels, what fraction the extractor found
- **Field accuracy:** exact-match rate for enum, boolean, and date fields
- **Invented values:** how often the extractor fills a field that my label says is `null` (not stated in the posting)

Skills are normalized (see Section 7) before comparison, so "Python 3" and "python" count as a match.

**Comparison:** Week 2 runs the same test set through two providers (see Section 7) and compares these metrics.

**Failure analysis:** for each wrong extraction, record which kind of posting caused it (e.g. skills buried in paragraphs, multiple roles in one posting) to guide prompt changes.

## 7. Open questions

- **LLM provider:** Week 2 compares Gemini free tier (Flash) vs. a local model via Ollama on the hand-labeled set; pick the one with better required-skill precision/recall.
- **Skill normalization:** how "Python", "Python 3", and "python programming" become one skill (alias list in code vs. LLM told to use canonical names). Decide in Week 2.
- **Storing lists in SQLite:** SQLite has no list type. Options: JSON text columns, or a separate `posting_skills` table. A separate table makes "most-requested skills" a simple `GROUP BY` query.
- **Posting sources:** which target companies' job boards allow automated access (check each site's terms and robots.txt), and whether any offer a public API or feed.
- **Scheduler:** how scheduled checks will run (e.g. a cron job on my Mac vs. a hosted scheduler). Decide in Week 6.
- **Alert channel:** how alerts reach me (email, desktop notification, etc.).