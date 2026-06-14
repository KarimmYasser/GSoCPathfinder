"""Pydantic data models for all GSoC Pathfinder entities."""

from __future__ import annotations

import hashlib

from pydantic import BaseModel, Field, computed_field

# === Raw Data Models (mirror the JSON schema) ===


class RawProject(BaseModel):
    """A project as it appears in the raw JSON data."""

    title: str
    short_description: str = ""
    description: str = ""
    student_name: str = ""
    code_url: str | None = None
    proposal_id: str | None = None
    project_url: str = ""


class RawOrganization(BaseModel):
    """An organization as it appears in the raw JSON data for a single year."""

    name: str
    image_url: str = ""
    image_background_color: str = "#ffffff"
    description: str = ""
    url: str = ""
    category: str = ""
    projects_url: str = ""
    ideas_url: str | None = None
    guide_url: str | None = None
    topics: list[str] = Field(default_factory=list)
    technologies: list[str] = Field(default_factory=list)
    irc_channel: str = ""
    contact_email: str = ""
    mailing_list: str = ""
    twitter_url: str = ""
    blog_url: str = ""
    facebook_url: str | None = None
    num_projects: int = 0
    projects: list[RawProject] = Field(default_factory=list)


class RawYearData(BaseModel):
    """Top-level structure of a year's JSON file."""

    year: int
    archive_url: str = ""
    organizations: list[RawOrganization] = Field(default_factory=list)


# === Normalized Models (after cleaning + resolution) ===


class NormalizedProject(BaseModel):
    """A project after HTML stripping, normalization, and ID generation."""

    id: str = ""  # deterministic hash
    title: str
    short_description: str = ""
    description_raw: str = ""  # original (may have HTML)
    description_clean: str = ""  # HTML-stripped plain text
    student_name: str = ""
    code_url: str | None = None
    proposal_id: str | None = None
    project_url: str = ""
    year: int = 0
    org_canonical_name: str = ""
    technologies: list[str] = Field(default_factory=list)  # inherited from org, normalized
    is_ongoing: bool = False  # True if code_url is null in current year

    @staticmethod
    def generate_id(canonical_name: str, year: int, title: str) -> str:
        """Generate a deterministic project ID from org name, year, and title."""
        raw = f"{canonical_name}|{year}|{title}".lower().strip()
        return hashlib.sha256(raw.encode()).hexdigest()[:16]


class NormalizedOrgYearProfile(BaseModel):
    """An organization's profile for a specific year, after normalization."""

    id: str = ""  # "{canonical_name}_{year}"
    canonical_name: str
    original_name: str  # the name as it appeared in this year's data
    year: int
    description: str = ""
    url: str = ""
    category: str = ""
    image_url: str = ""
    projects_url: str = ""
    ideas_url: str | None = None
    guide_url: str | None = None
    topics: list[str] = Field(default_factory=list)  # normalized
    technologies: list[str] = Field(default_factory=list)  # normalized
    num_projects: int = 0
    contact_channels: dict[str, str] = Field(default_factory=dict)  # irc, email, etc.
    projects: list[NormalizedProject] = Field(default_factory=list)

    @staticmethod
    def generate_id(canonical_name: str, year: int) -> str:
        """Generate profile ID."""
        return f"{canonical_name.lower().strip()}_{year}"


class NormalizedOrganization(BaseModel):
    """A unique organization across all years, after identity resolution."""

    canonical_name: str
    aliases: list[str] = Field(default_factory=list)  # all name variants
    description: str = ""  # most recent description
    url: str = ""  # most recent URL
    image_url: str = ""  # most recent image
    years_active: list[int] = Field(default_factory=list)
    profiles: list[NormalizedOrgYearProfile] = Field(default_factory=list)

    @computed_field
    @property
    def total_projects(self) -> int:
        """Total number of projects across all years."""
        return sum(p.num_projects for p in self.profiles)

    @computed_field
    @property
    def most_recent_year(self) -> int:
        """Most recent year of participation."""
        return max(self.years_active) if self.years_active else 0

    @computed_field
    @property
    def participation_count(self) -> int:
        """Number of years participated."""
        return len(self.years_active)


# === Scoring Models ===


class ScoreBreakdown(BaseModel):
    """Per-factor score breakdown for a single organization."""

    skill_overlap: float = 0.0  # f1
    semantic_similarity: float = 0.0  # f2
    recency_frequency: float = 0.0  # f3
    topic_alignment: float = 0.0  # f4
    project_volume: float = 0.0  # f5
    org_stability: float = 0.0  # f6
    llm_relevance: float = 0.0  # f7
    total: float = 0.0  # weighted sum


class RankedOrganization(BaseModel):
    """An organization with its score and explanation."""

    rank: int
    canonical_name: str
    description: str = ""
    url: str = ""
    category: str = ""
    years_active: list[int] = Field(default_factory=list)
    matched_technologies: list[str] = Field(default_factory=list)
    matched_topics: list[str] = Field(default_factory=list)
    score: ScoreBreakdown = Field(default_factory=ScoreBreakdown)
    explanation: str = ""  # LLM-generated narrative


# === User Profile Models ===


class UserProfile(BaseModel):
    """Structured profile extracted from a user's CV text."""

    raw_cv_text: str
    skills: list[str] = Field(default_factory=list)  # normalized tech names
    topics_of_interest: list[str] = Field(default_factory=list)
    experience_level: str = ""  # student, junior, mid, senior
    languages: list[str] = Field(default_factory=list)  # programming languages
    preferred_categories: list[str] = Field(default_factory=list)
    summary: str = ""  # LLM-generated summary of the CV


class MatchResult(BaseModel):
    """Final output of the matching agent."""

    user_profile: UserProfile
    rankings: list[RankedOrganization] = Field(default_factory=list)
    total_orgs_evaluated: int = 0
    weights_used: dict = Field(default_factory=dict)
