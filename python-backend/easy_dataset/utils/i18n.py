"""
Internationalization (i18n) utilities for Easy Dataset.

This module provides language detection, translation loading, and language switching
functionality for the Easy Dataset application.
"""

import json
import os
from pathlib import Path
from typing import Dict, Optional, Any
from threading import Lock


class I18n:
    """
    Internationalization manager for Easy Dataset.
    
    Supports multiple languages with JSON-based translation files.
    Thread-safe singleton implementation.
    """
    
    _instance: Optional['I18n'] = None
    _lock: Lock = Lock()
    
    # Supported languages
    SUPPORTED_LANGUAGES = ['en', 'zh-CN', 'tr']
    DEFAULT_LANGUAGE = 'en'
    
    def __new__(cls):
        """Ensure singleton pattern."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the i18n manager."""
        if not hasattr(self, '_initialized'):
            self._translations: Dict[str, Dict[str, Any]] = {}
            self._current_language: str = self.DEFAULT_LANGUAGE
            self._locales_dir: Optional[Path] = None
            self._initialized = True
            self._load_translations()
    
    def _find_locales_directory(self) -> Path:
        """
        Find the locales directory.
        
        Searches in multiple locations:
        1. python-backend/locales/
        2. locales/ (relative to package)
        3. ../locales/ (parent directory)
        
        Returns:
            Path to locales directory
            
        Raises:
            FileNotFoundError: If locales directory cannot be found
        """
        # Get the package root directory
        package_root = Path(__file__).parent.parent.parent
        
        # Try multiple possible locations
        possible_locations = [
            package_root / 'locales',  # python-backend/locales
            Path.cwd() / 'locales',     # Current working directory
            package_root.parent / 'locales',  # Parent directory (for development)
        ]
        
        for location in possible_locations:
            if location.exists() and location.is_dir():
                return location
        
        # If not found, create default location
        default_location = package_root / 'locales'
        default_location.mkdir(parents=True, exist_ok=True)
        return default_location
    
    def _load_translations(self):
        """Load all translation files from the locales directory."""
        try:
            self._locales_dir = self._find_locales_directory()
            
            for lang in self.SUPPORTED_LANGUAGES:
                translation_file = self._locales_dir / lang / 'messages.json'
                
                if translation_file.exists():
                    with open(translation_file, 'r', encoding='utf-8') as f:
                        self._translations[lang] = json.load(f)
                else:
                    # Create empty translation dict if file doesn't exist
                    self._translations[lang] = {}
                    
        except Exception as e:
            print(f"Warning: Failed to load translations: {e}")
            # Initialize with empty translations
            for lang in self.SUPPORTED_LANGUAGES:
                self._translations[lang] = {}
    
    def set_language(self, language: str) -> bool:
        """
        Set the current language.
        
        Args:
            language: Language code (e.g., 'en', 'zh-CN', 'tr')
            
        Returns:
            True if language was set successfully, False otherwise
        """
        if language in self.SUPPORTED_LANGUAGES:
            self._current_language = language
            return True
        return False
    
    def get_language(self) -> str:
        """
        Get the current language.
        
        Returns:
            Current language code
        """
        return self._current_language
    
    def get_supported_languages(self) -> list:
        """
        Get list of supported languages.
        
        Returns:
            List of supported language codes
        """
        return self.SUPPORTED_LANGUAGES.copy()
    
    def translate(self, key: str, language: Optional[str] = None, **kwargs) -> str:
        """
        Translate a key to the specified language.
        
        Args:
            key: Translation key in dot notation (e.g., 'common.save')
            language: Language code (uses current language if not specified)
            **kwargs: Variables for string interpolation
            
        Returns:
            Translated string, or the key itself if translation not found
        """
        lang = language or self._current_language
        
        # Get translation dict for language
        translations = self._translations.get(lang, {})
        
        # Navigate through nested dict using dot notation
        keys = key.split('.')
        value = translations
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    # Fallback to English if translation not found
                    if lang != self.DEFAULT_LANGUAGE:
                        return self.translate(key, self.DEFAULT_LANGUAGE, **kwargs)
                    return key
            else:
                return key
        
        # If value is not a string, return the key
        if not isinstance(value, str):
            return key
        
        # Perform string interpolation if kwargs provided
        if kwargs:
            try:
                # Support both {{var}} and {var} syntax
                result = value
                for var_key, var_value in kwargs.items():
                    result = result.replace(f'{{{{{var_key}}}}}', str(var_value))
                    result = result.replace(f'{{{var_key}}}', str(var_value))
                return result
            except Exception:
                return value
        
        return value
    
    def t(self, key: str, **kwargs) -> str:
        """
        Shorthand for translate().
        
        Args:
            key: Translation key
            **kwargs: Variables for string interpolation
            
        Returns:
            Translated string
        """
        return self.translate(key, **kwargs)
    
    def detect_language(self, accept_language: Optional[str] = None) -> str:
        """
        Detect language from Accept-Language header or other sources.
        
        Args:
            accept_language: Accept-Language header value
            
        Returns:
            Detected language code
        """
        if not accept_language:
            return self.DEFAULT_LANGUAGE
        
        # Parse Accept-Language header
        # Format: "en-US,en;q=0.9,zh-CN;q=0.8"
        languages = []
        for lang_part in accept_language.split(','):
            lang_part = lang_part.strip()
            if ';' in lang_part:
                lang, quality = lang_part.split(';', 1)
                try:
                    q = float(quality.split('=')[1])
                except (IndexError, ValueError):
                    q = 1.0
            else:
                lang = lang_part
                q = 1.0
            
            languages.append((lang.strip(), q))
        
        # Sort by quality
        languages.sort(key=lambda x: x[1], reverse=True)
        
        # Find first supported language
        for lang, _ in languages:
            # Try exact match first
            if lang in self.SUPPORTED_LANGUAGES:
                return lang
            
            # Try language without region (e.g., 'zh' from 'zh-CN')
            base_lang = lang.split('-')[0]
            for supported in self.SUPPORTED_LANGUAGES:
                if supported.startswith(base_lang):
                    return supported
        
        return self.DEFAULT_LANGUAGE
    
    def add_translation(self, language: str, key: str, value: str):
        """
        Add or update a translation dynamically.
        
        Args:
            language: Language code
            key: Translation key in dot notation
            value: Translation value
        """
        if language not in self._translations:
            self._translations[language] = {}
        
        # Navigate and create nested structure
        keys = key.split('.')
        current = self._translations[language]
        
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        
        current[keys[-1]] = value
    
    def reload_translations(self):
        """Reload all translation files from disk."""
        self._translations.clear()
        self._load_translations()


# Global instance
_i18n_instance = I18n()


def get_i18n() -> I18n:
    """
    Get the global i18n instance.
    
    Returns:
        I18n instance
    """
    return _i18n_instance


def t(key: str, **kwargs) -> str:
    """
    Global translation function.
    
    Args:
        key: Translation key
        **kwargs: Variables for string interpolation
        
    Returns:
        Translated string
    """
    return _i18n_instance.translate(key, **kwargs)


def set_language(language: str) -> bool:
    """
    Set the global language.
    
    Args:
        language: Language code
        
    Returns:
        True if successful
    """
    return _i18n_instance.set_language(language)


def get_language() -> str:
    """
    Get the current global language.
    
    Returns:
        Current language code
    """
    return _i18n_instance.get_language()


def detect_language(accept_language: Optional[str] = None) -> str:
    """
    Detect language from Accept-Language header.
    
    Args:
        accept_language: Accept-Language header value
        
    Returns:
        Detected language code
    """
    return _i18n_instance.detect_language(accept_language)
