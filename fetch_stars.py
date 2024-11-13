import requests
import csv
import time
from datetime import datetime
from config import load_config

class GitHubStarsFetcher:
    def __init__(self):
        config = load_config()
        self.token = config['github']['token']
        self.headers = {
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        self.base_url = "https://api.github.com"
        # Consider GitHub API rate limits (5000 requests per hour), set appropriate delay
        self.rate_limit_delay = 0.5  # 500ms between requests

    def get_starred_repos(self):
        page = 1
        all_repos = []
        
        while True:
            url = f"{self.base_url}/user/starred"
            params = {
                'page': page,
                'per_page': 100  # Maximum items per page
            }
            
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code == 200:
                repos = response.json()
                if not repos:  # If no more repositories
                    break
                
                for repo in repos:
                    # Get repository description
                    description = self.fetch_repo_info(repo['owner']['login'], repo['name'])
                    
                    repo_info = {
                        'full_name': repo['full_name'],
                        'description': description,
                        'html_url': repo['html_url'],
                        'stars': repo['stargazers_count'],
                        'language': repo['language'] or '',
                        'created_at': repo['created_at'],
                        'updated_at': repo['updated_at'],
                        'unstar': '0'  # Default: 0 = keep star, 1 = unstar
                    }
                    all_repos.append(repo_info)
                    time.sleep(self.rate_limit_delay)
                
                print(f"Fetched page {page}, got {len(repos)} repositories")
                page += 1
            else:
                print(f"Error fetching page {page}: {response.status_code}")
                break
            
            # Check API rate limits
            self.check_rate_limit()
        
        return all_repos

    def fetch_repo_info(self, owner, repo):
        url = f"https://api.github.com/repos/{owner}/{repo}"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            repo_data = response.json()
            # Return repository description
            return repo_data.get('description', '')
        return None

    def check_rate_limit(self):
        url = f"{self.base_url}/rate_limit"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            data = response.json()
            remaining = data['resources']['core']['remaining']
            reset_time = datetime.fromtimestamp(data['resources']['core']['reset'])
            
            if remaining < 100:  # If remaining requests are less than 100
                wait_time = (reset_time - datetime.now()).total_seconds()
                if wait_time > 0:
                    print(f"Rate limit low. Waiting for {wait_time:.2f} seconds...")
                    time.sleep(wait_time + 1)

    def save_to_csv(self, repos, filename='starred_repos.csv'):
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'full_name', 'description', 'html_url', 'stars', 
                'language', 'created_at', 'updated_at', 'unstar'
            ])
            writer.writeheader()
            writer.writerows(repos)

def main():
    fetcher = GitHubStarsFetcher()
    print("Starting to fetch starred repositories...")
    
    repos = fetcher.get_starred_repos()
    fetcher.save_to_csv(repos)
    
    print(f"Completed! Saved {len(repos)} repositories to starred_repos.csv")

if __name__ == "__main__":
    main() 