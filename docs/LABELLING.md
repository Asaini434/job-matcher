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

## Skill vocabulary
(Add names here as you use them.)

## Tricky cases log
### p001 (Amazon SDE Intern, Summer 2027)
- **"One of these" skills:** Basic Qualifications say "at least one general-purpose language such as Java, Python, C++, C#, Go, Rust, or TypeScript." The data model can't express "any one of." **Decision:** listed all seven in `required_skills`. Added to DESIGN.md Open Questions.
- **Locations:** Job details list Seattle, WA and Arlington, VA, but the description says applicants are considered at all US intern locations (long list). **Decision:** label only the official job-detail locations. Apply this rule to all postings.
- **Other seasons:** Posting is for Summer 2027 but mentions possible Winter 2027 and Fall 2027 openings. **Decision:** `term` = "Summer 2027" (the posting's stated term).
- **"Bachelor's degree or above":** The posting names only the minimum degree level, not a list. **Decision:** "or above" means all higher levels are eligible, so `degree_levels` = ["bachelors", "masters", "phd"].