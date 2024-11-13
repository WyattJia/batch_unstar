import csv
import requests
import time
from config import load_config

class GitHubStarRemover:
    def __init__(self):
        config = load_config()
        self.token = config['github']['token']
        self.headers = {
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        self.base_url = "https://api.github.com"
        # Set a conservative delay of 1 second between requests
        self.rate_limit_delay = 1

    def unstar_repository(self, repo_full_name):
        url = f"{self.base_url}/user/starred/{repo_full_name}"
        response = requests.delete(url, headers=self.headers)
        
        if response.status_code == 204:  # GitHub API returns 204 for successful unstar
            print(f"Successfully unstarred: {repo_full_name}")
            return True
        else:
            print(f"Failed to unstar {repo_full_name}: {response.status_code}")
            return False

    def process_csv(self, filename='starred_repos.csv'):
        unstarred_count = 0
        
        with open(filename, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['unstar'] == '1':
                    if self.unstar_repository(row['full_name']):
                        unstarred_count += 1
                    time.sleep(self.rate_limit_delay)
        
        return unstarred_count

def main():
    remover = GitHubStarRemover()
    print("Starting to process unstar requests...")
    
    unstarred_count = remover.process_csv()
    print(f"Completed! Unstarred {unstarred_count} repositories")

if __name__ == "__main__":
    main() 