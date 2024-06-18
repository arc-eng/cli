import subprocess
import re
from typing import Optional


def is_git_repo():
    """Check if the current directory is a git repository."""
    try:
        subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return True
    except subprocess.CalledProcessError:
        return False


def get_remote_origin_url():
    """Get the remote origin URL of the git repository."""
    try:
        result = subprocess.run(
            ["git", "config", "--get", "remote.origin.url"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return result.stdout.decode("utf-8").strip()
    except subprocess.CalledProcessError:
        return None


def extract_owner_repo(url):
    """Extract the owner/repo from a GitHub URL."""
    match = re.match(r"(?:git@github\.com:|https://github\.com/)([^/]+)/([^/]+)(?:\.git)?", url)
    if match:
        return f"{match.group(1)}/{match.group(2)}".replace(".git", "")
    return None


def detect_repository() -> Optional[str]:
    """Detect the Github repository of the current directory, if any."""
    if is_git_repo():
        repo_url = get_remote_origin_url()
        if repo_url:
            owner_repo = extract_owner_repo(repo_url)
            if owner_repo:
                return owner_repo
    return None


if __name__ == "__main__":
    if is_git_repo():
        repo_url = get_remote_origin_url()
        if repo_url:
            owner_repo = extract_owner_repo(repo_url)
            if owner_repo:
                print(f"This directory is a clone of the repository: {owner_repo}")
            else:
                print("Could not extract owner/repo from the remote origin URL.")
        else:
            print(
                "This directory is a git repository, "
                "but the remote origin URL could not be determined."
            )
    else:
        print("This directory is not a git repository.")
