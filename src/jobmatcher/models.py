from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict


class Location(BaseModel):
    model_config = ConfigDict(extra="forbid")

    city: str | None
    state: str | None
    country: str | None


class ExtractedPosting(BaseModel):
    model_config = ConfigDict(extra="forbid")

    company: str
    title: str
    date_posted: date | None
    employment_type: Literal["internship", "full_time", "part_time", "co_op", "unknown"]
    term: str | None
    locations: list[Location]
    work_mode: Literal["onsite", "hybrid", "remote", "unknown"]
    required_skills: list[str]
    preferred_skills: list[str]
    degree_levels: list[Literal["bachelors", "masters", "phd"]]
    grad_date_earliest: date | None
    grad_date_latest: date | None
    min_years_experience: float | None
    requires_work_authorization: bool | None
    sponsorship_available: bool | None
    accepts_cpt_opt: bool | None


class Label(ExtractedPosting):
    posting_id: str
    source_url: str