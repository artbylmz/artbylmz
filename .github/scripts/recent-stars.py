import html
import json
import os
import sys
import urllib.request

GITHUB_USER = "artbylmz"
COUNT = 5
DESC_MAX = 140
START = "<!-- RECENT_STARS:START -->"
END = "<!-- RECENT_STARS:END -->"
README = "README.md"


def fetch_starred():
    req = urllib.request.Request(
        f"https://api.github.com/users/{GITHUB_USER}/starred"
        "?per_page=100&sort=created&direction=desc",
        headers={
            "Accept": "application/vnd.github.star+json",
            "User-Agent": f"{GITHUB_USER}-readme-stars",
        },
    )
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=30) as res:
        return json.load(res)


def render(entry):
    repo = entry["repo"]
    desc = " ".join((repo.get("description") or "").split())[:DESC_MAX]
    if len(repo.get("description") or "") > DESC_MAX:
        desc = desc.rstrip() + "..."
    line = f"- [{repo['full_name']}]({repo['html_url']})"
    if desc:
        line += f" - {html.escape(desc, quote=False)}"
    return line


def main():
    lines = [render(entry) for entry in fetch_starred()[:COUNT]]
    with open(README, encoding="utf-8") as f:
        text = f.read()
    try:
        idx_start = text.index(START)
        idx_end = text.index(END)
    except ValueError:
        sys.exit(f"{START}/{END} markers missing from {README}")
    if idx_end < idx_start:
        sys.exit(f"{END} appears before {START} in {README}")
    middle = "\n" + "\n".join(lines) + "\n" if lines else "\n"
    new_text = text[: idx_start + len(START)] + middle + text[idx_end:]
    with open(README, encoding="utf-8", mode="w") as f:
        f.write(new_text)
    print("README.md updated" if new_text != text else "README.md unchanged")


if __name__ == "__main__":
    main()
