# Design doc: job-matcher

Ananya Saini, Sudeeksha Reddy Kontham

## 1. Problem

Internship postings open on a rolling basis across a lot of different company job boards, and applying early matters. Checking those boards by hand is slow. Comparing each posting to my resume one at a time, for example by pasting it into a chatbot, doesn't scale either: a chatbot doesn't watch for new postings, doesn't remember the postings I've already looked at, formats its answers differently every time, and gives me no idea how often it's wrong.

The goal is a tool that finds new internship postings from companies I'm targeting, turns each one into a consistent structured record, checks whether I'm eligible and how well I fit, and summarizes which skills come up most across the roles I care about. I also want to know how accurate the extraction step actually is, so it gets measured against postings I labeled myself.

## 2. Use cases

These are the questions I want the tool to answer:

1. Which new postings from my target companies showed up since the last check, and which ones am I eligible for?
2. For a given posting, how well does my resume match, which required skills am I missing, and which of my real experiences should I highlight?
3. Across everything I've saved, which skills are asked for most often, and which of those don't I have?
4. Can it hide postings where my degree level, graduation date, or work authorization obviously doesn't fit?
5. Which postings have I applied to, and where is each application right now?

## 3. Scope

In scope for the 8 weeks:

- Extracting requirements from posting text into the data model in section 4
- Resume matching and a gap report
- SQLite storage for postings and applications
- A skill trends report
- Scheduled checks of target companies' job boards, with alerts for new matching postings
- Measuring extraction accuracy on labeled postings

Out of scope:

- Auto-applying to jobs
- Generating resume content. Suggestions only point to experience I actually have.
- Scraping LinkedIn, Indeed, or any site whose terms don't allow automated access
- Multiple users. This is built for me.

## 4. Data model

If a posting doesn't state something, the field is `null` (or an empty list). Nothing gets guessed. Dates are stored as `YYYY-MM-DD` text, which sorts correctly and is what SQLite expects for dates.

The "Set by" column says whether the LLM fills the field in or my own code does. Only the LLM fields are part of the accuracy evaluation.

### postings

Facts about the company's posting.

| Field | Type | Set by | Description |
|---|---|---|---|
| `id` | integer | code | Primary key |
| `company` | string | LLM | Company name |
| `title` | string | LLM | Job title as written |
| `source_url` | string, unique | code | Link to the original posting, used to detect duplicates |
| `external_id` | string or null | code | The job board's own ID for the posting, if it has one |
| `source` | string | code | Where it was found, e.g. a company careers page |
| `first_seen_at` | datetime | code | When this tool first saw the posting. Used for new-posting alerts and trends |
| `last_seen_at` | datetime | code | Last check that still found it listed, to notice closed postings |
| `date_posted` | date or null | LLM | Posting date, only if an exact date is shown |
| `employment_type` | `internship`, `full_time`, `part_time`, `co_op`, `unknown` | LLM | Type of role |
| `term` | string or null | LLM | Season and year, e.g. "Summer 2027" |
| `locations` | list of {city, state, country} | LLM | Every listed location; empty if none |
| `work_mode` | `onsite`, `hybrid`, `remote`, `unknown` | LLM | Work arrangement, only if stated |
| `required_skills` | list of strings | LLM | Skills from the required qualifications |
| `preferred_skills` | list of strings | LLM | Skills from preferred / nice-to-have qualifications |
| `degree_levels` | list of `bachelors`, `masters`, `phd` | LLM | Eligible degree levels; empty if not stated |
| `grad_date_earliest` | date or null | LLM | Earliest graduation date accepted |
| `grad_date_latest` | date or null | LLM | Latest graduation date accepted |
| `min_years_experience` | number or null | LLM | Minimum experience stated. "6+ years" is 6, "6 months" is 0.5 |
| `requires_work_authorization` | boolean or null | LLM | Posting says candidates must already be authorized to work in the US |
| `sponsorship_available` | boolean or null | LLM | Posting says whether visa sponsorship is offered |
| `accepts_cpt_opt` | boolean or null | LLM | Posting explicitly says whether CPT/OPT candidates are eligible |
| `raw_text` | string | code | Full posting text, kept locally and not committed, so extraction can be re-run |
| `extracted_at` | datetime | code | When extraction ran |
| `extraction_model` | string | code | Which model and prompt version produced the record |

### applications

My own actions, kept separate from the posting so that re-fetching a posting never overwrites my application status. At most one row per posting.

| Field | Type | Description |
|---|---|---|
| `id` | integer | Primary key |
| `posting_id` | integer, unique | Foreign key to `postings.id` |
| `status` | `planned`, `applied`, `online_assessment`, `interviewing`, `offer`, `rejected`, `withdrawn` | Current stage |
| `applied_date` | date or null | Date submitted; null while planned |
| `resume_version` | string or null | Which version of my resume I sent |
| `notes` | string or null | Referral, recruiter name, anything else |
| `updated_at` | datetime | Last change to this row |

The LLM-extracted fields are defined in code as the `ExtractedPosting` Pydantic model in `src/jobmatcher/models.py`. Hand labels use the same model plus `posting_id` and `source_url`, so the labels and the extractor output can't drift apart.

## 5. Architecture

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

The main rule is that the LLM extracts and the code decides.

The LLM is only used where understanding natural language is actually needed: turning posting text into a record, judging resume fit, and choosing the next tool in the agent loop. Everything that has a correct answer is plain code: scheduling, duplicate detection (by `source_url` or `external_id`), database writes, and eligibility checks like comparing my graduation date to the posting's window. Code is predictable and easy to test with pytest, while LLM output changes from run to run, so I don't want an eligibility decision to depend on the model.

Every extraction is validated against the Pydantic model before it's stored. Output with a wrong type or an enum value outside the allowed list is rejected.

All LLM calls go through one function, `extract_requirements(text) -> ExtractedPosting`, so I can compare providers and switch between them by changing one module.

API calls can fail for reasons outside my control. On the first test call, Gemini returned a 503 "high demand" error. The extractor will retry with increasing waits, use a timeout instead of hanging, and record which postings failed instead of stopping the whole run.

## 6. Evaluation

The dataset is 14 real postings labeled using the rules in `docs/LABELLING.md`. Every judgment call I made while labeling is written down in that file's tricky cases log.

The split is in `data/splits.json`:

- Dev set, 4 postings: used while writing and adjusting the prompt. These labels were first drafted with an LLM, then checked and corrected by hand against the posting text.
- Test set, 10 postings: labeled entirely by hand and only used to report final numbers. Adjusting the prompt on the same postings I report on would make the results look better than they are.

Ten test postings is small, so the results are a rough estimate, and the README will say that next to the numbers.

Metrics:

- Required-skill precision: of the skills the extractor lists, the fraction that are in my label
- Required-skill recall: of the skills in my label, the fraction the extractor found
- Field accuracy: exact match on enum, boolean, and date fields
- Invented values: how often the extractor fills a field my label says is null, meaning the posting never said it

Skills get normalized before comparing (see section 7), so "Python 3" and "Python" count as the same skill.

In week 2 the same test set goes through two providers, Gemini and a local model through Ollama, and I'll compare these numbers before picking one.

For every wrong extraction I'll note what kind of posting caused it (skills buried in paragraphs, several roles in one posting, requirements only in an application form) so the prompt changes are based on real failures.

## 7. Open questions

- LLM provider. Gemini free tier vs. a local Ollama model, decided by required-skill precision and recall on the test set.
- Skill normalization. How "Python", "Python 3", and "python programming" become one skill: an alias list in code, or telling the model to use standard names.
- Lists in SQLite. SQLite has no list type, so either JSON text columns or a separate `posting_skills` table. The separate table makes "most requested skills" a simple `GROUP BY`.
- "One of these" requirements. Some postings want any one skill from a list ("at least one of Java, Python, C++..."). Listing all of them as required overstates the requirement and hurts the gap report. Options are a separate `required_one_of` field or treating the group as one requirement.
- Duplicate URLs. Job links often include tracking parameters, so one posting can appear under several URLs. Either strip query parameters before checking for duplicates, or use the company's requisition ID (Capital One's `R244285`, for example) as `external_id`.
- Program pages. Some companies (JPMorganChase, for example) publish overview pages describing several role tracks with no locations or dates. The fetcher should skip those and only process individual postings.
- Pages rendered with JavaScript. Some careers sites (BigBear.ai's, for example) load the description with JavaScript, so a plain HTTP request gets an empty page. Options are an underlying data feed if the site has one, a headless browser, or skipping those sources. Each site's terms need checking first.
- Clearance requirements. p003 and p004 require security clearances. A `clearance_required` field would flag roles I can't apply to.
- Degree meaning. For internships the degree is one you're currently pursuing; for full-time roles it's usually one you've already finished, and often only a minimum is stated. A `min_degree_level` plus a pursuing/completed field might fit better than a list.
- Application deadlines. Several postings show a closing date, which matters more for applying early than the posting date. Worth adding an `application_deadline` field.
- Posting sources. Which target companies' job boards allow automated access (terms and robots.txt), and whether any offer a public API or feed.
- Scheduler. A cron job on my Mac or a hosted scheduler. Decide in week 6.
- Alerts. Email, desktop notification, or something else.
