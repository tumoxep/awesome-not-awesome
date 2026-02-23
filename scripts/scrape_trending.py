import requests
from bs4 import BeautifulSoup

TRENDING_URLS = [
    "https://github.com/trending?since=daily",
    "https://github.com/trending?since=weekly",
    "https://github.com/trending?since=monthly"
]
README_PATH = "README.md"

def scrape_trending(url):
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, 'html.parser')
    repos = []
    for repo in soup.select('article.Box-row'):
        title = repo.select_one('h2 a').text.strip()
        repo_url = 'https://github.com' + repo.select_one('h2 a')['href']
        description = repo.select_one('p')
        description = description.text.strip() if description else "No description"
        repos.append((title, repo_url, description))
    return repos

def update_readme(trending_repos):
    README_PATH = "README.md"
    marker = "<!-- trending start -->"
    with open(README_PATH, "r", encoding="utf-8") as f:
        readme = f.read()

    # Ensure only one marker, find insertion point
    if readme.count(marker) > 1:
        # Remove extra markers
        lines = readme.splitlines()
        new_lines = []
        marker_found = False
        for line in lines:
            if marker in line:
                if not marker_found:
                    new_lines.append(marker)
                    marker_found = True
            else:
                new_lines.append(line)
        readme = "\n".join(new_lines)

    # Find marker position
    marker_index = readme.find(marker)
    if marker_index == -1:
        # Marker missing, append at end
        readme = readme.rstrip() + "\n\n" + marker + "\n"
        marker_index = readme.find(marker)

    # Split head and tail
    head = readme[:marker_index + len(marker)]
    tail = readme[marker_index + len(marker):]
    # Optionally, clear anything after marker (or preserve content as needed)
    # Here, we overwrite everything after marker.
    new_entries = "\n"
    for repo in trending_repos:
        # Clean repo[0]: single line only, just author/repo
        name = ''.join(repo[0].split())  # Remove weird newlines/tabs from scraping
        new_entries += f"- {name}\n"
    updated = head + new_entries

    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(updated)

if __name__ == "__main__":
    all_repos = []
    for url in TRENDING_URLS:
        all_repos.extend(scrape_trending(url))
    update_readme(all_repos)