"""Data validation and identity resolution for GSoC organizations."""

from collections import defaultdict

from models import NormalizedOrganization, NormalizedOrgYearProfile


class DataValidator:
    """Aggregates profiles and resolves organizations across years."""

    def __init__(self):
        # canonical_name -> list of profiles
        self.org_profiles: dict[str, list[NormalizedOrgYearProfile]] = defaultdict(list)

    def add_profiles(self, profiles: list[NormalizedOrgYearProfile]):
        """Add a batch of year profiles to the validator."""
        for p in profiles:
            self.org_profiles[p.canonical_name].append(p)

    def get_organizations(self) -> list[NormalizedOrganization]:
        """Resolve all profiles into unique organizations."""
        orgs = []

        for canonical_name, profiles in self.org_profiles.items():
            # Sort profiles by year ascending
            profiles.sort(key=lambda p: p.year)

            # The most recent profile usually has the best description/URL/image
            latest = profiles[-1]

            # Collect all known aliases for this org
            aliases = set()
            for p in profiles:
                if p.original_name != canonical_name:
                    aliases.add(p.original_name)

            years_active = [p.year for p in profiles]

            org = NormalizedOrganization(
                canonical_name=canonical_name,
                aliases=sorted(list(aliases)),
                description=latest.description,
                url=latest.url,
                image_url=latest.image_url,
                years_active=years_active,
                profiles=profiles,
            )
            orgs.append(org)

        return orgs

    def get_quality_report(self) -> dict:
        """Generate a basic data quality report."""
        orgs = self.get_organizations()

        total_orgs = len(orgs)
        total_profiles = sum(len(o.profiles) for o in orgs)
        total_projects = sum(o.total_projects for o in orgs)

        # Distribution of participation
        participation_counts = defaultdict(int)
        for o in orgs:
            participation_counts[o.participation_count] += 1

        return {
            "total_unique_orgs": total_orgs,
            "total_org_year_profiles": total_profiles,
            "total_projects": total_projects,
            "participation_distribution": dict(participation_counts),
        }
