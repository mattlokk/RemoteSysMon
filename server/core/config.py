"""
Configuration Manager
Handles loading, saving, and managing application settings
"""

import json
import os
from typing import Any, Dict, Optional


class Config:
    """Manage application configuration"""
    
    DEFAULT_CONFIG = {
        "appearance": {
            "background_color": "#1e1e1e",
            "text_color": "#ffffff",
            "tile_background_color": "#0078d4",
            "tile_text_color": "#ffffff",
            "font_size": 14,
            "show_graphs": True,
            "refresh_rate_ms": 1000
        },
        "adb": {
            "device_id": None,
            "auto_connect": True,
            "target_path": "/data/local/tmp/system_stats.json"
        },
        "monitoring": {
            "auto_start": True,
            "minimize_to_tray": True,
            "start_minimized": False
        }
    }
    
    def __init__(self, config_path: str = "config.json"):
        """
        Initialize configuration manager
        
        Args:
            config_path: Path to configuration file
        """
        self.config_path = config_path
        self.config = self.load()
    
    def load(self) -> Dict[str, Any]:
        """
        Load configuration from file
        
        Returns:
            Configuration dictionary
        """
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    loaded_config = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    return self._migrate_config(self._merge_configs(self.DEFAULT_CONFIG, loaded_config))
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading config: {e}. Using defaults.")
                return self._migrate_config(self.DEFAULT_CONFIG.copy())
        return self._migrate_config(self.DEFAULT_CONFIG.copy())

    def _migrate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize config keys for backwards compatibility

        Args:
            config: Loaded configuration

        Returns:
            Config with new keys applied
        """
        appearance = config.get('appearance')
        if isinstance(appearance, dict):
            if 'tile_background_color' not in appearance and 'accent_color' in appearance:
                appearance['tile_background_color'] = appearance['accent_color']
                appearance.pop('accent_color', None)
            if 'tile_text_color' not in appearance:
                appearance['tile_text_color'] = appearance.get('text_color', '#ffffff')
        return config
    
    def _merge_configs(self, default: Dict, loaded: Dict) -> Dict:
        """
        Recursively merge loaded config with defaults
        
        Args:
            default: Default configuration
            loaded: Loaded configuration
            
        Returns:
            Merged configuration
        """
        result = default.copy()
        for key, value in loaded.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        return result
    
    def save(self) -> bool:
        """
        Save configuration to file
        
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
            return True
        except IOError as e:
            print(f"Error saving config: {e}")
            return False
    
    def get(self, section: str, key: Optional[str] = None) -> Any:
        """
        Get configuration value
        
        Args:
            section: Configuration section
            key: Optional key within section
            
        Returns:
            Configuration value
        """
        if key:
            return self.config.get(section, {}).get(key)
        return self.config.get(section, {})
    
    def set(self, section: str, key: str, value: Any) -> None:
        """
        Set configuration value and save
        
        Args:
            section: Configuration section
            key: Key within section
            value: Value to set
        """
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value
        self.save()
    
    def get_appearance(self) -> Dict[str, Any]:
        """Get all appearance settings"""
        return self.config.get("appearance", {})
    
    def get_adb_settings(self) -> Dict[str, Any]:
        """Get all ADB settings"""
        return self.config.get("adb", {})
    
    def get_monitoring_settings(self) -> Dict[str, Any]:
        """Get all monitoring settings"""
        return self.config.get("monitoring", {})
    
    def reset_to_defaults(self) -> None:
        """Reset configuration to defaults"""
        self.config = self.DEFAULT_CONFIG.copy()
        self.save()
