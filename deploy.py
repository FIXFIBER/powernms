import subprocess
import sys
from datetime import datetime
from pathlib import Path


REPO_URL = "https://github.com/FIXFIBER/powernms.git"
CNAME = "power.fob.net.ng"


def run(args, cwd=None, check=True):
    result = subprocess.run(args, cwd=cwd, text=True, capture_output=True)
    if result.stdout.strip():
        print(result.stdout.strip())
    if result.stderr.strip():
        print(result.stderr.strip())
    if check and result.returncode != 0:
        print("Something went wrong. Please check the message above.")
        sys.exit(result.returncode)
    return result


def ensure_repo(repo):
    git_dir = repo / ".git"
    if git_dir.exists():
        return
    if repo.exists() and any(repo.iterdir()):
        print(f"Folder {repo} exists but is not a git repo. Please use an empty folder or the cloned repo.")
        sys.exit(1)
    print("Downloading the project folder...")
    result = subprocess.run(["git", "clone", REPO_URL, str(repo)], text=True, capture_output=True)
    if result.stdout.strip():
        print(result.stdout.strip())
    if result.stderr.strip():
        print(result.stderr.strip())
    if result.returncode != 0:
        print("Could not download the project. Make sure Git is installed and you have access to the repo.")
        sys.exit(result.returncode)


def ensure_cname(repo):
    cname_file = repo / "CNAME"
    if not cname_file.exists():
        cname_file.write_text(CNAME + "\n", encoding="utf-8")
        print(f"Added {CNAME} settings.")


def main():
    script_dir = Path(__file__).resolve().parent
    if (script_dir / ".git").exists() or (script_dir / "main.py").exists():
        repo = script_dir
    else:
        repo = script_dir / "powernms"

    ensure_repo(repo)
    ensure_cname(repo)

    print("Preparing to upload your changes...")

    status = subprocess.run(["git", "status", "--porcelain"], cwd=repo, text=True, capture_output=True)
    if status.returncode != 0:
        print(status.stderr.strip() or "Git is not ready in this folder.")
        sys.exit(1)

    if not status.stdout.strip():
        print("No changes found. Nothing to upload.")
        return

    message = " ".join(sys.argv[1:]).strip()
    if not message:
        message = f"Update {datetime.now().strftime('%Y-%m-%d %H:%M')}"

    run(["git", "add", "-A"], cwd=repo)
    run(["git", "commit", "-m", message], cwd=repo)
    run(["git", "push"], cwd=repo)
    print("Done. Your changes are on GitHub.")


if __name__ == "__main__":
    main()
