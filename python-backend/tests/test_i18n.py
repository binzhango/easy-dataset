"""
Tests for internationalization (i18n) functionality.
"""

import pytest
from easy_dataset.utils.i18n import I18n, get_i18n, t, set_language, get_language, detect_language


class TestI18n:
    """Test cases for I18n class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.i18n = I18n()
        # Reset to default language
        self.i18n.set_language('en')
    
    def test_singleton_pattern(self):
        """Test that I18n follows singleton pattern."""
        i18n1 = I18n()
        i18n2 = I18n()
        assert i18n1 is i18n2
    
    def test_get_i18n(self):
        """Test get_i18n() returns the global instance."""
        i18n = get_i18n()
        assert isinstance(i18n, I18n)
        assert i18n is I18n()
    
    def test_supported_languages(self):
        """Test that all expected languages are supported."""
        languages = self.i18n.get_supported_languages()
        assert 'en' in languages
        assert 'zh-CN' in languages
        assert 'tr' in languages
    
    def test_set_language_valid(self):
        """Test setting a valid language."""
        assert self.i18n.set_language('zh-CN') is True
        assert self.i18n.get_language() == 'zh-CN'
    
    def test_set_language_invalid(self):
        """Test setting an invalid language."""
        assert self.i18n.set_language('invalid') is False
        # Should remain at current language
        assert self.i18n.get_language() == 'en'
    
    def test_translate_simple_key(self):
        """Test translating a simple key."""
        # English
        self.i18n.set_language('en')
        assert self.i18n.translate('common.success') == 'Success'
        
        # Chinese
        self.i18n.set_language('zh-CN')
        assert self.i18n.translate('common.success') == '成功'
        
        # Turkish
        self.i18n.set_language('tr')
        assert self.i18n.translate('common.success') == 'Başarılı'
    
    def test_translate_nested_key(self):
        """Test translating a nested key."""
        self.i18n.set_language('en')
        assert self.i18n.translate('tasks.status.pending') == 'Pending'
        
        self.i18n.set_language('zh-CN')
        assert self.i18n.translate('tasks.status.pending') == '待处理'
    
    def test_translate_with_interpolation(self):
        """Test translation with variable interpolation."""
        self.i18n.set_language('en')
        result = self.i18n.translate('errors.file_not_found', path='/test/file.txt')
        assert 'File not found: /test/file.txt' == result
    
    def test_translate_missing_key(self):
        """Test translating a missing key returns the key itself."""
        result = self.i18n.translate('nonexistent.key')
        assert result == 'nonexistent.key'
    
    def test_translate_fallback_to_english(self):
        """Test that missing translations fall back to English."""
        # Add a key only in English
        self.i18n.add_translation('en', 'test.only_english', 'English only')
        
        # Try to get it in Chinese (should fallback to English)
        self.i18n.set_language('zh-CN')
        result = self.i18n.translate('test.only_english')
        assert result == 'English only'
    
    def test_shorthand_t_function(self):
        """Test the shorthand t() function."""
        self.i18n.set_language('en')
        assert self.i18n.t('common.loading') == 'Loading...'
    
    def test_global_t_function(self):
        """Test the global t() function."""
        set_language('en')
        assert t('common.error') == 'Error'
    
    def test_detect_language_from_header(self):
        """Test language detection from Accept-Language header."""
        # English
        lang = detect_language('en-US,en;q=0.9')
        assert lang == 'en'
        
        # Chinese
        lang = detect_language('zh-CN,zh;q=0.9,en;q=0.8')
        assert lang == 'zh-CN'
        
        # Turkish
        lang = detect_language('tr-TR,tr;q=0.9')
        assert lang == 'tr'
    
    def test_detect_language_with_quality(self):
        """Test language detection respects quality values."""
        # Higher quality for Chinese
        lang = detect_language('en;q=0.5,zh-CN;q=0.9')
        assert lang == 'zh-CN'
    
    def test_detect_language_fallback(self):
        """Test language detection falls back to default."""
        lang = detect_language('fr-FR,de-DE')
        assert lang == 'en'  # Default language
    
    def test_detect_language_no_header(self):
        """Test language detection with no header."""
        lang = detect_language(None)
        assert lang == 'en'
    
    def test_add_translation_dynamically(self):
        """Test adding translations dynamically."""
        self.i18n.add_translation('en', 'dynamic.test', 'Dynamic value')
        assert self.i18n.translate('dynamic.test') == 'Dynamic value'
    
    def test_interpolation_with_multiple_variables(self):
        """Test interpolation with multiple variables."""
        self.i18n.set_language('en')
        result = self.i18n.translate(
            'tasks.messages.task_progress',
            completed=5,
            total=10,
            percentage=50
        )
        assert '5' in result
        assert '10' in result
        assert '50' in result
    
    def test_translation_files_loaded(self):
        """Test that translation files are loaded."""
        # Check that some translations exist
        self.i18n.set_language('en')
        assert self.i18n.translate('common.success') != 'common.success'
        
        self.i18n.set_language('zh-CN')
        assert self.i18n.translate('common.success') != 'common.success'
        
        self.i18n.set_language('tr')
        assert self.i18n.translate('common.success') != 'common.success'


class TestI18nGlobalFunctions:
    """Test global i18n functions."""
    
    def test_set_and_get_language(self):
        """Test global set_language and get_language functions."""
        set_language('zh-CN')
        assert get_language() == 'zh-CN'
        
        set_language('en')
        assert get_language() == 'en'
    
    def test_global_translate(self):
        """Test global translate function."""
        set_language('en')
        assert t('common.processing') == 'Processing...'
        
        set_language('zh-CN')
        assert t('common.processing') == '处理中...'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
