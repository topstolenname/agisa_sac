"""
Utility functions for [PROJECT_NAME].
"""
import logging
from pathlib import Path
from typing import Optional


def setup_logging(verbose: bool = False) -> logging.Logger:
    """
    Configure logging for the application.
    
    Args:
        verbose: If True, set log level to DEBUG
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(__name__)
    level = logging.DEBUG if verbose else logging.INFO
    
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    return logger


def ensure_directory(path: Path) -> Path:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        path: Directory path to check/create
    
    Returns:
        Path object of the directory
    
    Raises:
        PermissionError: If directory cannot be created
    """
    path = Path(path)
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
    return path


def read_config(config_path: Optional[Path] = None) -> dict:
    """
    Read configuration from file.
    
    Args:
        config_path: Path to config file (defaults to ~/.config/PROJECT_NAME/config.json)
    
    Returns:
        Configuration dictionary
    """
    if config_path is None:
        config_path = Path.home() / ".config" / "PROJECT_NAME" / "config.json"
    
    if not config_path.exists():
        # Return default config
        return {
            "version": "1.0.0",
            "settings": {}
        }
    
    import json
    with open(config_path, 'r') as f:
        return json.load(f)


def save_config(config: dict, config_path: Optional[Path] = None) -> None:
    """
    Save configuration to file.
    
    Args:
        config: Configuration dictionary to save
        config_path: Path to config file
    """
    if config_path is None:
        config_path = Path.home() / ".config" / "PROJECT_NAME" / "config.json"
    
    ensure_directory(config_path.parent)
    
    import json
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
