import requests
import csv
import time
from datetime import datetime
import base64
from pathlib import Path
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
        # 考虑到GitHub API的限制(每小时5000次请求)，设置适当的延迟
        self.rate_limit_delay = 0.5  # 500ms between requests

    def get_starred_repos(self):
        page = 1
        all_repos = []
        
        while True:
            url = f"{self.base_url}/user/starred"
            params = {
                'page': page,
                'per_page': 100  # 每页最大数量
            }
            
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code == 200:
                repos = response.json()
                if not repos:  # 如果没有更多仓库了
                    break
                
                for repo in repos:
                    # 获取README内容
                    readme_content = self.get_readme(repo['full_name'])
                    
                    repo_info = {
                        'full_name': repo['full_name'],
                        'description': repo['description'] or '',
                        'html_url': repo['html_url'],
                        'stars': repo['stargazers_count'],
                        'language': repo['language'] or '',
                        'created_at': repo['created_at'],
                        'updated_at': repo['updated_at'],
                        'readme': readme_content,
                        'unstar': 'No'  # 默认不取消star
                    }
                    all_repos.append(repo_info)
                    time.sleep(self.rate_limit_delay)
                
                print(f"Fetched page {page}, got {len(repos)} repositories")
                page += 1
            else:
                print(f"Error fetching page {page}: {response.status_code}")
                break
            
            # 检查API限制
            self.check_rate_limit()
        
        return all_repos

    def get_readme(self, repo_full_name):
        url = f"{self.base_url}/repos/{repo_full_name}/readme"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            try:
                content = response.json()['content']
                return base64.b64decode(content).decode('utf-8')
            except:
                return "Unable to decode README"
        return "No README found"

    def check_rate_limit(self):
        url = f"{self.base_url}/rate_limit"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            data = response.json()
            remaining = data['resources']['core']['remaining']
            reset_time = datetime.fromtimestamp(data['resources']['core']['reset'])
            
            if remaining < 100:  # 如果剩余请求数小于100
                wait_time = (reset_time - datetime.now()).total_seconds()
                if wait_time > 0:
                    print(f"Rate limit low. Waiting for {wait_time:.2f} seconds...")
                    time.sleep(wait_time + 1)

    def save_to_csv(self, repos, filename='starred_repos.csv'):
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'full_name', 'description', 'html_url', 'stars', 
                'language', 'created_at', 'updated_at', 'readme', 'unstar'
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