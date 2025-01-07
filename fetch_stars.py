"""GitHub starred repositories fetcher.

This module provides functionality to fetch and export all starred repositories
from a GitHub account to a CSV file.
"""

import csv
import time
from datetime import datetime

import requests

from config import load_config


class GitHubStarsFetcher:
    """Fetches starred repositories from GitHub and exports them to CSV."""

    def __init__(self):
        config = load_config()
        self.token = config['github']['token']
        self.headers = {
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        self.base_url = "https://api.github.com"
        self.rate_limit_delay = 0.5  # 500ms between requests
        self.per_page = 100  # Maximum items per page

    def get_starred_repos(self, start_page=1):
        """Fetch all starred repositories from GitHub.
        
        Args:
            start_page (int): Page number to start fetching from
            
        Returns:
            list: List of repository information dictionaries
        """
        all_repos = []
        page = start_page
        
        while True:
            try:
                repos = self._fetch_page(page)
                if not repos:  # No more repositories
                    break
                
                for repo in repos:
                    try:
                        # Get repository description
                        description = self.fetch_repo_info(
                            repo['owner']['login'], 
                            repo['name']
                        )
                        
                        repo_info = {
                            'full_name': repo['full_name'],
                            'description': description,
                            'html_url': repo['html_url'],
                            'stars': repo['stargazers_count'],
                            'language': repo['language'] or '',
                            'created_at': repo['created_at'],
                            'updated_at': repo['updated_at'],
                            'unstar': '0'  # Default: 0 = keep star
                        }
                        all_repos.append(repo_info)
                        time.sleep(self.rate_limit_delay)
                        
                    except Exception as e:
                        print(f"Error processing repo {repo['full_name']}: {str(e)}")
                        continue
                
                print(f"Fetched page {page}, got {len(repos)} repositories")
                page += 1
                
                # Check API rate limits
                self.check_rate_limit()
                
            except Exception as e:
                print(f"Error fetching page {page}: {str(e)}")
                break
        
        return all_repos

    def _fetch_page(self, page):
        """Fetch a single page of starred repositories.
        
        Args:
            page (int): Page number to fetch
            
        Returns:
            list: List of repositories from the API response
        """
        url = f"{self.base_url}/user/starred"
        params = {
            'page': page,
            'per_page': self.per_page
        }
        
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()  # Raise exception for error status codes
        return response.json()

    def fetch_repo_info(self, owner, repo):
        """Fetch additional repository information.
        
        Args:
            owner (str): Repository owner
            repo (str): Repository name
            
        Returns:
            str: Repository description or empty string
        """
        try:
            url = f"{self.base_url}/repos/{owner}/{repo}"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            repo_data = response.json()
            return repo_data.get('description', '')
        except Exception as e:
            print(f"Error fetching info for {owner}/{repo}: {str(e)}")
            return ''

    def check_rate_limit(self):
        """Check GitHub API rate limits and wait if necessary."""
        try:
            url = f"{self.base_url}/rate_limit"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            data = response.json()
            remaining = data['resources']['core']['remaining']
            reset_time = datetime.fromtimestamp(data['resources']['core']['reset'])
            
            if remaining < 100:  # If remaining requests are low
                wait_time = (reset_time - datetime.now()).total_seconds()
                if wait_time > 0:
                    print(f"Rate limit low. Waiting for {wait_time:.2f} seconds...")
                    time.sleep(wait_time + 1)
        except Exception as e:
            print(f"Error checking rate limit: {str(e)}")

    def save_to_csv(self, repos, filename='starred_repos.csv'):
        """Save repository information to CSV file.
        
        Args:
            repos (list): List of repository information dictionaries
            filename (str): Output CSV filename
        """
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                fieldnames = [
                    'full_name', 'description', 'html_url', 'stars', 
                    'language', 'created_at', 'updated_at', 'unstar'
                ]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(repos)
                print(f"Successfully saved {len(repos)} repositories to {filename}")
        except Exception as e:
            print(f"Error saving to CSV: {str(e)}")

def main():
    """Entry point for the GitHub stars fetcher."""
    try:
        fetcher = GitHubStarsFetcher()
        print("Starting to fetch starred repositories...")
        repos = fetcher.get_starred_repos()
        fetcher.save_to_csv(repos)
        print(f"Completed! Fetched {len(repos)} repositories")
    except requests.RequestException as e:
        print(f"API request error: {str(e)}")
    except IOError as e:
        print(f"File operation error: {str(e)}")
    except Exception as e:  # pylint: disable=broad-except
        print(f"Fatal error: {str(e)}")


if __name__ == "__main__":
    main() 