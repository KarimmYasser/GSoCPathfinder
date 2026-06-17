"""Tests for GitHub issue fetching."""

from api.github import GitHubIssue, parse_github_repo


def test_parse_github_repo_valid():
    assert parse_github_repo("https://github.com/owner/repo") == "owner/repo"


def test_parse_github_repo_with_git_suffix():
    result = parse_github_repo("https://github.com/owner/repo.git")
    assert result is not None
    assert "owner/repo" in result


def test_parse_github_repo_with_trailing_slash():
    assert parse_github_repo("https://github.com/owner/repo/") == "owner/repo"


def test_parse_github_repo_invalid():
    assert parse_github_repo("https://gitlab.com/owner/repo") is None


def test_parse_github_repo_empty():
    assert parse_github_repo("") is None


def test_parse_github_repo_none():
    assert parse_github_repo(None) is None


def test_github_issue_model():
    issue = GitHubIssue(
        title="Fix bug",
        url="https://github.com/owner/repo/issues/1",
        labels=["bug", "good first issue"],
        number=1,
    )
    assert issue.title == "Fix bug"
    assert len(issue.labels) == 2
