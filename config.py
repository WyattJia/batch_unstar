import yaml
from pathlib import Path

def load_config():
    config_path = Path(__file__).parent / 'config.yaml'
    
    if not config_path.exists():
        raise FileNotFoundError("config.yaml not found. Please create it from config.yaml.example")
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    if not config.get('github', {}).get('token'):
        raise ValueError("GitHub token not found in config.yaml")
        
    return config 