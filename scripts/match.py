"""CLI entry point for testing the matching agent."""

import asyncio
import sys
from pathlib import Path

# Add src to Python path
src_dir = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_dir))

from agent.state import AgentState
from agent.workflow import create_matching_workflow


async def main():
    print("=== GSoC Pathfinder Matching Agent ===")

    # Default CV if none provided via arguments
    cv_text = """
    I am a 3rd year Computer Science student. I love writing Python and Go.
    I have experience building web applications with React and Node.js.
    I am very interested in Machine Learning, Natural Language Processing, 
    and open source contribution. I have worked with Docker and Kubernetes for deployments.
    """

    # Determine advanced and ultra flags from CLI arguments
    advanced = "--advanced" in sys.argv or "--ultra" in sys.argv
    ultra = "--ultra" in sys.argv

    # Filter out CLI option flags from file path check
    file_args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if file_args:
        cv_file = Path(file_args[0])
        if cv_file.exists():
            with open(cv_file, encoding="utf-8") as f:
                cv_text = f.read()
                print(f"Loaded CV from {cv_file.name}")
    else:
        print("Using default hardcoded CV for testing.")

    print(f"\nStarting Matching Workflow (advanced: {advanced}, ultra: {ultra})...\n")

    app = create_matching_workflow()

    initial_state = AgentState(
        raw_cv_text=cv_text,
        advanced=advanced,
        ultra=ultra,
        user_profile=None,
        graph_results=[],
        vector_results=[],
        ranked_organizations=[],
        match_result=None,
    )

    try:
        # Run the workflow
        result = await app.ainvoke(initial_state)

        match_data = result.get("match_result")
        if not match_data:
            print("Workflow completed but no results were returned.")
            return

        print("\n=== MATCHING COMPLETE ===")
        print("\nYour Profile:")
        profile = match_data["user_profile"]
        print(f"Level: {profile['experience_level']}")
        print(f"Skills: {', '.join(profile['skills'])}")
        print(f"Interests: {', '.join(profile['topics_of_interest'])}")

        print("\n=== TOP ORGANIZATIONS ===")
        for i, org in enumerate(match_data["rankings"][:5]):
            score = org["score"]["total"]
            print(f"\n{i + 1}. {org['canonical_name']} (Score: {score:.2f})")
            print(f"   Matched Skills: {', '.join(org['matched_technologies'])}")
            print(f"   Matched Topics: {', '.join(org['matched_topics'])}")
            print(f"   AI Explanation: {org['explanation']}")
            print(f"   URL: {org['url']}")

    except Exception as e:
        print(f"\n[!] Error during matching workflow: {e}")


if __name__ == "__main__":
    # Ensure Windows asyncio works properly with httpx/aiohttp
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
