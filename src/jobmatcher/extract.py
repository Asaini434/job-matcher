from dotenv import load_dotenv
from google import genai

from jobmatcher.models import ExtractedPosting

load_dotenv()

MODEL = "gemini-3.8-flash"

PROMPT = """You extract structured data from a single job posting. Fill in every field of
the JSON schema using only what the posting says.

GENERAL
- Use only information stated in the posting. Do not use outside knowledge about the
  company, and do not guess.
- If something is not stated, use null. Use an empty list [] for list fields, and
  "unknown" for employment_type and work_mode.
- Questions in an application form (for example "Do you require sponsorship?") are not
  a statement of policy. Ignore them when filling in fields.

COMPANY AND TITLE
- company: the company name as the posting writes it.
- title: the job title exactly as written.

DATES
- All dates use YYYY-MM-DD.
- date_posted: only if an exact date is shown. Relative dates like "3 days ago" are null.

ROLE
- employment_type: "internship" for any internship or co-op style role, even if the
  posting also says "full time" (that describes the hours, not the role type). Use
  "full_time" or "part_time" only for non-internship roles that state it. If nothing is
  stated, use "unknown".
- term: season and year, like "Summer 2027". If only start and end dates are given,
  use the season they fall in.

LOCATION
- locations: the locations officially listed for the job (for example in the job
  details or header). Do not include a long list of other places applicants "may be
  considered" for. Use two-letter US state codes and "US" for the country.
- work_mode: "onsite" if the posting says in-person or in-office work is required,
  "hybrid" if it describes a hybrid model or some days in the office, "remote" if
  remote, otherwise "unknown".

SKILLS
- Take skills only from qualification sections (required, minimum, basic, preferred,
  nice to have, "what you need", "what you'll bring"). Never take skills from the
  responsibilities or "what you'll do" section.
- Skills under required, minimum, basic, must have, or a section with no qualifier go
  in required_skills. Skills under preferred, nice to have, bonus, or "a plus" go in
  preferred_skills. If a single bullet inside the required list says "preferred",
  that skill goes in preferred_skills.
- A skill is a concrete language, tool, framework, platform, or technical area
  (for example Python, SQL, AWS, React, machine learning, distributed systems).
- Do not list soft skills (communication, teamwork, problem solving, analytical
  ability), degrees, years of experience, or security clearances as skills.
- "such as" / "e.g." / examples in parentheses: list each named example as its own
  skill. Also keep the category if it is a real technical area (for example
  "BI tools (e.g. Tableau)" gives "BI tools" and "Tableau"). Skip vague parts like
  "and others" or "etc.".
- "At least one of A, B, C" or "either A or B": list every option.
- "C/C++" is two skills: "C" and "C++".
- Use standard spellings: Python, Java, C, C++, C#, Go, Rust, TypeScript, JavaScript,
  SQL, NoSQL, R, AWS, Power BI, Microsoft Office, Copilot, Snowflake, Databricks,
  machine learning, large language models, data structures, algorithms.
- Write each skill as a short name, usually one to three words. Drop filler words
  like "experience with", "knowledge of", "techniques", "skills", "concepts".

EDUCATION AND EXPERIENCE
- degree_levels: the degree levels the posting accepts. "Bachelor's or above" means
  ["bachelors", "masters", "phd"]. An MBA counts as "masters".
- Graduation dates: for a range like "between December 2027 and August 2028", set
  grad_date_earliest to the first day of the first month and grad_date_latest to the
  last day of the last month. "December 2027 or May 2028" is treated the same way.
  A single deadline like "by June 2028" sets only grad_date_latest.
- min_years_experience: the minimum stated, as a number. "6+ years" is 6, "6 months"
  is 0.5. For a range use the lower end. "No prior experience required" is 0.

WORK AUTHORIZATION (describe this role only, not a later full-time role)
- requires_work_authorization: true if the posting says candidates must be authorized
  to work in the US. Otherwise null.
- sponsorship_available: false if the posting says it will not sponsor; true if it says
  sponsorship is offered; otherwise null.
- accepts_cpt_opt: only set if CPT or OPT is mentioned explicitly. true if those
  candidates are eligible, false if the posting says it will not support CPT/OPT.
  Otherwise null.
"""
COUNTRY_ALIASES = {"united states": "US", "usa": "US", "u.s.": "US", "us": "US"}


def normalize(posting: ExtractedPosting) -> ExtractedPosting:
    for loc in posting.locations:
        if loc.country and loc.country.lower() in COUNTRY_ALIASES:
            loc.country = COUNTRY_ALIASES[loc.country.lower()]
    return posting

def extract_requirements(text: str) -> ExtractedPosting:
    client = genai.Client()
    interaction = client.interactions.create(
        model=MODEL,
        input=PROMPT + "\n\nPOSTING:\n" + text,
        response_format={
            "type": "text",
            "mime_type": "application/json",
            "schema": ExtractedPosting.model_json_schema(),
        },
    )
    return normalize(ExtractedPosting.model_validate_json(interaction.output_text))

    