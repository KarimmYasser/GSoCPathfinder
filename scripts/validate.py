"""Validate the entire data ingestion pipeline locally."""

import sys
from pathlib import Path

# Add src to Python path so we can import modules
src_dir = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_dir))

from ingestion.parser import parse_directory
from ingestion.normalizer import DataNormalizer
from ingestion.validator import DataValidator

def main():
    data_dir = Path(__file__).parent.parent / "Data"
    config_dir = src_dir / "config"
    
    print("1. Parsing JSON files...")
    raw_years = parse_directory(data_dir)
    print(f"   Loaded {len(raw_years)} years of data.")
    
    print("\n2. Initializing Data Normalizer...")
    normalizer = DataNormalizer(config_dir)
    print(f"   Loaded {len(normalizer.org_aliases)} org aliases.")
    print(f"   Loaded {len(normalizer.tech_synonyms)} tech synonyms and {len(normalizer.tech_splits)} splits.")
    
    print("\n3. Processing and Normalizing Data...")
    validator = DataValidator()
    
    total_projects_raw = 0
    for year_data in raw_years:
        for org in year_data.organizations:
            total_projects_raw += len(org.projects)
            
        profiles = normalizer.process_year_data(year_data)
        validator.add_profiles(profiles)
        
    print(f"   Processed {total_projects_raw} raw projects.")
    
    print("\n4. Resolving Identity and Generating Quality Report...")
    report = validator.get_quality_report()
    
    print("\n=== DATA QUALITY REPORT ===")
    print(f"Total Unique Organizations: {report['total_unique_orgs']}")
    print(f"Total Org-Year Profiles:    {report['total_org_year_profiles']}")
    print(f"Total Projects:             {report['total_projects']}")
    
    print("\nParticipation Distribution (Years Active -> Number of Orgs):")
    for years, count in sorted(report['participation_distribution'].items()):
        print(f"   {years} years: {count} orgs")
        
    print("\nValidation complete. If the numbers look correct, the pipeline is ready for graph ingestion.")

if __name__ == "__main__":
    main()
