"""Data normalization to handle tech synonyms and org aliases."""

import yaml
from pathlib import Path
from models import RawYearData, NormalizedProject, NormalizedOrgYearProfile, NormalizedOrganization

def load_yaml_config(filepath: Path | str) -> dict:
    """Load a YAML configuration file."""
    path = Path(filepath)
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}

class DataNormalizer:
    """Normalizes raw data using alias and synonym maps."""
    
    def __init__(self, config_dir: Path | str):
        self.config_dir = Path(config_dir)
        self.org_aliases = self._load_org_aliases()
        self.tech_synonyms, self.tech_splits = self._load_tech_synonyms()
        
    def _load_org_aliases(self) -> dict[str, str]:
        """Load org aliases mapping any variant to its canonical name."""
        config = load_yaml_config(self.config_dir / "org_aliases.yaml")
        alias_map = {}
        # Format: { "Canonical Name": ["Alias 1", "Alias 2"] }
        for canonical, aliases in config.get("aliases", {}).items():
            # Identity map for canonical
            alias_map[canonical.lower().strip()] = canonical
            for alias in aliases:
                alias_map[alias.lower().strip()] = canonical
        return alias_map

    def _load_tech_synonyms(self) -> tuple[dict[str, str], dict[str, list[str]]]:
        """Load technology synonyms and splits."""
        config = load_yaml_config(self.config_dir / "tech_synonyms.yaml")
        synonyms = config.get("synonyms", {})
        splits = config.get("split_mappings", {})
        
        # Format: { "alias": "canonical" }
        synonym_map = {k.lower().strip(): v.lower().strip() for k, v in synonyms.items()}
        split_map = {k.lower().strip(): [v_item.lower().strip() for v_item in v] for k, v in splits.items()}
        
        return synonym_map, split_map

    def get_canonical_org_name(self, raw_name: str) -> str:
        """Get the canonical organization name for a raw name."""
        key = raw_name.lower().strip()
        # If explicitly aliased, use canonical. Otherwise, use original (stripped).
        return self.org_aliases.get(key, raw_name.strip())

    def normalize_technologies(self, raw_techs: list[str]) -> list[str]:
        """Normalize a list of technologies, applying synonyms and splits."""
        normalized = set()
        for tech in raw_techs:
            tech = tech.lower().strip()
            if not tech:
                continue
                
            if tech in self.tech_splits:
                normalized.update(self.tech_splits[tech])
            elif tech in self.tech_synonyms:
                normalized.add(self.tech_synonyms[tech])
            else:
                normalized.add(tech)
                
        return sorted(list(normalized))

    def normalize_topics(self, raw_topics: list[str]) -> list[str]:
        """Normalize a list of topics (mostly lowercasing)."""
        return sorted(list(set(t.lower().strip() for t in raw_topics if t.strip())))

    def process_year_data(self, raw_data: RawYearData) -> list[NormalizedOrgYearProfile]:
        """Process a year's raw data into normalized profiles and projects."""
        profiles = []
        year = raw_data.year
        
        for raw_org in raw_data.organizations:
            canonical_name = self.get_canonical_org_name(raw_org.name)
            norm_techs = self.normalize_technologies(raw_org.technologies)
            norm_topics = self.normalize_topics(raw_org.topics)
            
            # Extract contact channels
            channels = {}
            if raw_org.irc_channel: channels["irc"] = raw_org.irc_channel
            if raw_org.contact_email: channels["email"] = raw_org.contact_email
            if raw_org.mailing_list: channels["mailing_list"] = raw_org.mailing_list
            if raw_org.twitter_url: channels["twitter"] = raw_org.twitter_url
            if raw_org.blog_url: channels["blog"] = raw_org.blog_url
            if raw_org.facebook_url: channels["facebook"] = raw_org.facebook_url
            
            from ingestion.parser import clean_html
            
            projects = []
            for raw_proj in raw_org.projects:
                proj = NormalizedProject(
                    id=NormalizedProject.generate_id(canonical_name, year, raw_proj.title),
                    title=raw_proj.title.strip(),
                    short_description=raw_proj.short_description.strip(),
                    description_raw=raw_proj.description,
                    description_clean=clean_html(raw_proj.description),
                    student_name=raw_proj.student_name.strip(),
                    code_url=raw_proj.code_url,
                    proposal_id=raw_proj.proposal_id,
                    project_url=raw_proj.project_url,
                    year=year,
                    org_canonical_name=canonical_name,
                    technologies=norm_techs,
                    is_ongoing=(not raw_proj.code_url and year == 2026) # Or similar logic
                )
                projects.append(proj)
                
            profile = NormalizedOrgYearProfile(
                id=NormalizedOrgYearProfile.generate_id(canonical_name, year),
                canonical_name=canonical_name,
                original_name=raw_org.name,
                year=year,
                description=clean_html(raw_org.description),
                url=raw_org.url,
                category=raw_org.category,
                image_url=raw_org.image_url,
                projects_url=raw_org.projects_url,
                ideas_url=raw_org.ideas_url,
                guide_url=raw_org.guide_url,
                topics=norm_topics,
                technologies=norm_techs,
                num_projects=raw_org.num_projects,
                contact_channels=channels,
                projects=projects
            )
            profiles.append(profile)
            
        return profiles
