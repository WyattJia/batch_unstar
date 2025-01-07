"""Configuration loader for GitHub star management tools."""

from pathlib import Path
import yaml


def load_config():
    """Load configuration from config.yaml file.
    
    Returns:
        dict: Configuration dictionary containing GitHub credentials
        
    Raises:
        FileNotFoundError: If config.yaml is not found
        ValueError: If GitHub token is missing from config
    """
    config_path = Path(__file__).parent / 'config.yaml'
    
    if not config_path.exists():
        raise FileNotFoundError("config.yaml not found. Please create it from config.yaml.example")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    if not config.get('github', {}).get('token'):
        raise ValueError("GitHub token not found in config.yaml")
    
    return config 