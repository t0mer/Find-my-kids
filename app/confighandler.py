"""
Configuration management module for the application.
Handles loading, saving, and copying of configuration files.
"""

import yaml
from typing import Any, Dict
import shutil
from pathlib import Path
from loguru import logger
from dataclasses import dataclass

@dataclass
class Config:
    """
    Configuration data class containing all application settings.
    Using dataclass for automatic initialization and better code organization.
    """
    wapi_base_url: str
    wapi_contacts_url: str
    wapi_qr_image_url: str
    wapi_session: str
    wapi_api_token: str
    ai_teach_url: str
    ai_detect_url: str
    contacts_update_interval: int
    chats_update_interval: int
    images_download_interval: int
    kids_detection_interval: int

class ConfigHandler:
    """
    Handles configuration file operations including loading, saving, and copying.
    """
    
    def __init__(self, config_dir: str = "config"):
        """
        Initialize the ConfigHandler.
        
        Args:
            config_dir (str): Directory where config files are stored
        """
        self.config_dir = Path(config_dir)
        self.config_file = self.config_dir / "config.yaml"
        self.source_config = Path("config.yaml")
        self.setup_config()

    def setup_config(self) -> None:
        """
        Set up the configuration directory and copy initial config if needed.
        Creates the config directory if it doesn't exist and copies the default config file.
        """
        try:
            # Create config directory if it doesn't exist
            self.config_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy config file if it doesn't exist
            if not self.config_file.exists() and self.source_config.exists():
                shutil.copy2(self.source_config, self.config_file)
                logger.info(f"Copied config file from {self.source_config} to {self.config_file}")
                
        except Exception as e:
            logger.error(f"Error setting up config: {e}")
            raise

    def load(self) -> Config:
        """
        Load configuration from YAML file.
        
        Returns:
            Config: Configuration object with loaded settings
            
        Raises:
            FileNotFoundError: If config file doesn't exist
            yaml.YAMLError: If config file is invalid
        """
        try:
            with open(self.config_file, 'r') as file:
                config_data = yaml.safe_load(file)
            return Config(**config_data)
            
        except FileNotFoundError:
            logger.error(f"Config file not found: {self.config_file}")
            raise
        except yaml.YAMLError as e:
            logger.error(f"Invalid YAML in config file: {e}")
            raise
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            raise

    def save(self, config: Config) -> None:
        """
        Save configuration to YAML file.
        
        Args:
            config (Config): Configuration object to save
            
        Raises:
            Exception: If there's an error saving the config
        """
        try:
            # Convert config object to dictionary
            config_data = {
                'wapi_base_url': config.wapi_base_url,
                'wapi_contacts_url': config.wapi_contacts_url,
                'wapi_qr_image_url': config.wapi_qr_image_url,
                'wapi_session': config.wapi_session,
                'wapi_api_token': config.wapi_api_token,
                'ai_teach_url': config.ai_teach_url,
                'ai_detect_url': config.ai_detect_url,
                'contacts_update_interval': config.contacts_update_interval,
                'chats_update_interval': config.chats_update_interval,
                'images_download_interval': config.images_download_interval,
                'kids_detection_interval': config.kids_detection_interval
            }
            
            # Save to file with proper formatting
            with open(self.config_file, 'w') as file:
                yaml.safe_dump(config_data, file, default_flow_style=False)
                
            logger.info(f"Configuration saved to {self.config_file}")
            
        except Exception as e:
            logger.error(f"Error saving config: {e}")
            raise

# Example usage:
# config_handler = ConfigHandler('config.yaml')
# config = config_handler.load()
# config_handler.save(config)
