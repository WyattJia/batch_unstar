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

    def process_csv(self, filename='starred_repos.csv', skip_rows=382):
        """Process CSV file to unstar repositories.
        
        Args:
            filename (str): Path to CSV file containing repository data
            skip_rows (int): Number of initial rows to skip and mark as processed
            
        Returns:
            int: Number of repositories successfully unstarred
        """
        unstarred_count = 0
        processed_rows = []
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                fieldnames = reader.fieldnames
                
                # Validate required columns exist
                if not {'full_name', 'unstar'}.issubset(set(fieldnames)):
                    raise ValueError("CSV must contain 'full_name' and 'unstar' columns")
                
                for i, row in enumerate(reader):
                    if i < skip_rows:  # Already processed rows
                        row['unstar'] = '1'
                        processed_rows.append(row)
                        continue
                        
                    if row['unstar'] == '0':
                        try:
                            if self.unstar_repository(row['full_name']):
                                unstarred_count += 1
                                row['unstar'] = '1'
                        except Exception as e:
                            print(f"Error processing {row['full_name']}: {str(e)}")
                        finally:
                            time.sleep(self.rate_limit_delay)
                            
                    processed_rows.append(row)
            
            # Write back all rows with updated unstar status
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(processed_rows)
                
            return unstarred_count
            
        except FileNotFoundError:
            print(f"Error: Could not find file {filename}")
            return 0
        except Exception as e:
            print(f"Unexpected error processing CSV: {str(e)}")
            return 0

def main():
    remover = GitHubStarRemover()
    print("Starting to process unstar requests...")
    
    unstarred_count = remover.process_csv()
    print(f"Completed! Unstarred {unstarred_count} repositories")

if __name__ == "__main__":
    main() 