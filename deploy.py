import subprocess
import sys
from datetime import datetime
from pathlib import Path


def run(args, cwd=None):
    result = subprocess.run(args, cwd=cwd, text=True, capture_output=True)
    if result.stdout.strip():
        print(result.stdout.strip())
    if result.stderr.strip():
        print(result.stderr.strip())
    if result.returncode != 0:
        print("Something went wrong. Please check the message above.")
        sys.exit(result.returncode)
    return result


def main():
    repo = Path(__file__).resolve().parent
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
