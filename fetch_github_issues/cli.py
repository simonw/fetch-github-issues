import argparse
import os
import json
import http.client
from typing import List, Optional, Tuple, Dict


def create_connection() -> http.client.HTTPSConnection:
    return http.client.HTTPSConnection("api.github.com")


def make_request(
    conn: http.client.HTTPSConnection, method: str, url: str, headers: Dict[str, str]
) -> Tuple[Dict, Optional[str]]:
    conn.request(method, url, headers=headers)
    response = conn.getresponse()
    data = json.loads(response.read().decode())
    next_url = None
    for link in response.getheader("Link", "").split(", "):
        if 'rel="next"' in link:
            next_url = link[link.index("<") + 1 : link.index(">")]
    return data, next_url


def fetch_all_pages(
    conn: http.client.HTTPSConnection, url: str, headers: Dict[str, str]
) -> List[Dict]:
    results = []
    while url:
        data, next_url = make_request(conn, "GET", url, headers)
        results.extend(data if isinstance(data, list) else [data])
        url = next_url
    return results


def save_issue_data(issue_data: Dict, comments: List[Dict], output_dir: str):
    full_data = {"issue": issue_data, "comments": comments}
    filename = os.path.join(output_dir, f"{issue_data['number']}.json")
    with open(filename, "w") as f:
        json.dump(full_data, f, indent=2)


def fetch_github_issues(
    repo: str,
    issue_numbers: Optional[List[int]],
    output_dir: str,
    api_key: Optional[str],
):
    if not api_key:
        api_key = os.environ.get("GITHUB_TOKEN")
        if not api_key:
            raise ValueError(
                "GitHub API key not provided. Use --key or set GITHUB_TOKEN environment variable."
            )

    headers = {
        "Authorization": f"token {api_key}",
        "User-Agent": "Python-GitHub-Issues-Fetcher",
    }

    conn = create_connection()
    base_path = f"/repos/{repo}/issues"

    if issue_numbers:
        for number in issue_numbers:
            issue_data, _ = make_request(conn, "GET", f"{base_path}/{number}", headers)
            comments = fetch_all_pages(conn, issue_data["comments_url"], headers)
            save_issue_data(issue_data, comments, output_dir)
    else:
        all_issues = fetch_all_pages(conn, base_path, headers)
        for issue in all_issues:
            comments = fetch_all_pages(conn, issue["comments_url"], headers)
            save_issue_data(issue, comments, output_dir)

    conn.close()


def main():
    parser = argparse.ArgumentParser(
        description="Fetch all GitHub issues for a repository and save them as JSON"
    )
    parser.add_argument("repo", help="GitHub repository in the format owner/repo")
    parser.add_argument(
        "issues", nargs="*", type=int, help="Specific issue numbers to fetch"
    )
    parser.add_argument("--all", action="store_true", help="Fetch all issues")
    parser.add_argument("--key", help="GitHub API key")
    parser.add_argument("--output", default=".", help="Output directory for JSON files")

    args = parser.parse_args()

    if not args.issues and not args.all:
        parser.error("Either specify issue numbers or use --all to fetch all issues.")

    issue_numbers = None if args.all else args.issues
    os.makedirs(args.output, exist_ok=True)

    try:
        fetch_github_issues(args.repo, issue_numbers, args.output, args.key)
        print(f"Issues fetched successfully. JSON files saved in {args.output}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main()
