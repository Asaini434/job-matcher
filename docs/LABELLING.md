# Labeling Guidelines

Labels are the answer key for evaluating extraction. Follow these rules for every posting.

## Files
- Raw text: `data/postings/pNNN.txt` (copy the full posting text; not committed)
- Label: `data/labels/pNNN.json` (committed)

## Template

```json
{
  "posting_id": "p001",
  "source_url": "",
  "company": "",
  "title": "",
  "date_posted": null,
  "employment_type": "unknown",
  "term": null,
  "locations": [],
  "work_mode": "unknown",
  "required_skills": [],
  "preferred_skills": [],
  "degree_levels": [],
  "grad_date_earliest": null,
  "grad_date_latest": null,
  "requires_work_authorization": null,
  "sponsorship_available": null,
  "accepts_cpt_opt": null
}
```

Each entry in `locations`: `{"city": "Seattle", "state": "WA", "country": "US"}` (use `null` for any part not stated).

## General rules
1. **Label only what the posting states.** Don't use outside knowledge about the company. If it isn't stated, use `null` (or `[]` for lists, `unknown` for enums).
2. **Don't look at any model output before labeling.**

## Field rules
- **date_posted:** only if an absolute date is shown (`YYYY-MM-DD`). Relative dates ("3 days ago") → `null`.
- **term:** format `"Summer 2027"`, `"Fall 2026"`, etc.
- **required vs. preferred skills:**
  - Under "required", "minimum qualifications", "must have" → `required_skills`
  - Under "preferred", "nice to have", "bonus", "a plus" → `preferred_skills`
  - A section with no qualifier (e.g. "What you'll bring") → `required_skills`
- **What counts as a skill:** concrete languages, tools, frameworks, platforms, and technical areas (e.g. Python, SQL, AWS, React, machine learning, distributed systems). **Not** soft skills (communication, teamwork) and **not** degrees.
- **Skill names:** use the most common name, written the same way every time (`Python`, `C++`, `JavaScript`, `AWS`, `machine learning`). Add every new name to the Skill Vocabulary below and reuse it after that.
- **degree_levels:** "pursuing a BS or MS" → `["bachelors", "masters"]`.
- **Grad dates:** month-only dates use the first day of the month for `grad_date_earliest` and the last day for `grad_date_latest`. "Graduating between Dec 2027 and Jun 2028" → `2027-12-01`, `2028-06-30`. Only one date given ("graduating by June 2028") → fill only `grad_date_latest`.
- **Work authorization:**
  - "Must be authorized to work in the US" → `requires_work_authorization: true`
  - "We will not sponsor" / "without sponsorship now or in the future" → `sponsorship_available: false`
  - "Sponsorship available" → `sponsorship_available: true`
  - CPT/OPT only set if explicitly mentioned
  - Anything vague → `null`, and note it in the Tricky Cases log
- **min_years_experience:** the minimum stated, as a number ("6+ years" → 6, "6 months" → 0.5). If a range, use the lower end. Not a skill; never put it in the skills lists.
- **"e.g." examples:** label the category ("BI tools"), not the examples in parentheses (Tableau, Metabase).

## Skill vocabulary
(Add names here as you use them.)

## Tricky cases log

### p001 (Amazon SDE Intern, Summer 2027)
- **"One of these" skills:** Basic Qualifications say "at least one general-purpose language such as Java, Python, C++, C#, Go, Rust, or TypeScript." The data model can't express "any one of." **Decision:** listed all seven in `required_skills`. Added to DESIGN.md Open Questions.
- **Locations:** Job details list Seattle, WA and Arlington, VA, but the description says applicants are considered at all US intern locations (long list). **Decision:** label only the official job-detail locations. Apply this rule to all postings.
- **Other seasons:** Posting is for Summer 2027 but mentions possible Winter 2027 and Fall 2027 openings. **Decision:** `term` = "Summer 2027" (the posting's stated term).
- **"Bachelor's degree or above":** The posting names only the minimum degree level, not a list. **Decision:** "or above" means all higher levels are eligible, so `degree_levels` = ["bachelors", "masters", "phd"].

### p002 (Capital One, Current Master's Data Science Internship, Summer 2027)
- **Claude-labeled.** Labeled by an LLM, not by hand. Keep in the dev set, not the test set.
- **Source URL tracking parameters:** the link had tracking parameters (`utm_source`, `p_sid`, etc.). The same posting reached from a different link would have a different URL. **Decision:** store the URL without query parameters. Added to DESIGN.md Open Questions.
- **Vague required skill:** "open source programming languages for data analysis" names no specific language. **Decision:** labeled as "open-source programming languages" plus "data analysis".
- **"One of these" skills again:** "Direct experience with either Python, R or SQL" (preferred). **Decision:** listed all three, same as p001.
- **MBA counts as masters:** degree can be a quantitative Master's or an MBA with a quantitative concentration. **Decision:** `degree_levels` = ["masters"].
- **Only a latest grad date:** "degree obtained by August 2028 or earlier." **Decision:** `grad_date_latest` = 2028-08-31, earliest = null.
- **Hybrid wording:** "in-person attendance... in accordance with Capital One's hybrid working model." **Decision:** `work_mode` = "hybrid".
- **Sponsorship split:** no sponsorship for the internship, but the full-time role afterward is eligible for sponsorship. **Decision:** `sponsorship_available` = false (the field describes this posting's role). `requires_work_authorization` = null, because the posting doesn't explicitly say candidates must already be authorized.

### p003 (BigBear.ai, Senior E&D Technology Analyst)
- **Full-time not stated:** a senior salaried role, but the posting never says "full-time." **Decision:** `employment_type` = "unknown" (rule 1: label only what's stated). Good test of whether the extractor invents a value.
- **Responsibilities vs. qualifications:** "What you will do" mentions structured analytic techniques, briefings, etc. **Decision:** skills come only from qualification sections ("What you need to have" / "What we'd like you to have"), not from responsibilities. New general rule.
- **Non-skill requirements:** TS/SCI clearance, US residency, 8+ years of experience, CI poly, DoW/IC experience. None fit a Section 4 field. **Decision:** not labeled. Added to DESIGN.md Open Questions.
- **Work authorization:** the posting requires US residency and a TS/SCI clearance but says nothing explicit about work authorization or sponsorship. Clearances generally come with citizenship requirements, but that's outside knowledge. **Decision:** all three fields = null.
- **Degree meaning differs:** here "Bachelor's degree" means a degree already completed, not one being pursued, and it's a minimum. Master's is only preferred. **Decision:** `degree_levels` = ["bachelors"]. Added to Open Questions.
- **Location wording:** listed as "Washington, Washington, DC"; the overview also says "or the greater National Capital Region." **Decision:** one location, Washington, DC.
- **Date posted:** not shown on the page. **Decision:** null.

### p004 (Scale AI, Senior Data Analyst, Public Sector) — hand-labeled
- **Section naming:** requirements are under "Ideally you'd have" and preferred items under "Nice to haves." "Ideally" sounds optional, but that list includes an item marked "required." **Decision:** "Ideally you'd have" = required, "Nice to haves" = preferred.
- **Years of experience listed as a skill:** "6+ years of relevant work experience" appeared in the qualifications list. **Decision:** added a `min_years_experience` field (6) instead of labeling it as a skill. Back-filled p001 (null), p002 (0.5), p003 (8).
- **"e.g." examples:** "BI tools (e.g. Tableau, Metabase)," "data modeling tools (e.g. DBT)." **Decision:** label the category only.
- **Work mode only in the application form:** the description doesn't state the arrangement, but the form asks about working in the DC office 3 times a week. **Decision:** `work_mode` = "hybrid". The extractor may not see form text, so this may count as a hard case in failure analysis.
- **Form questions aren't policy:** the application asks "Are you legally authorized…" and "Will you require sponsorship…" Asking the question doesn't say what the policy is. **Decision:** all three work-authorization fields = null.
- **Clearance:** Secret required, Top Secret preferred. No field yet (see Open Questions).