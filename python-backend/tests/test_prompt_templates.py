"""
Tests for prompt template system.

This module tests the prompt generation functions for:
- Question generation
- Answer generation
- Data cleaning
- Dataset evaluation
"""

import pytest
from easy_dataset.llm.prompts import (
    get_question_prompt,
    get_answer_prompt,
    get_data_clean_prompt,
    get_dataset_evaluation_prompt,
    get_ga_prompt,
    get_question_template_prompts,
)


class TestQuestionPrompts:
    """Tests for question generation prompts"""
    
    def test_basic_question_prompt_english(self):
        """Test basic English question prompt generation"""
        text = "This is a sample text for testing."
        prompt = get_question_prompt(language='en', text=text, number=3)
        
        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert text in prompt
        assert '3' in prompt  # Number of questions
        assert 'Question' in prompt
    
    def test_basic_question_prompt_chinese(self):
        """Test basic Chinese question prompt generation"""
        text = "这是一个测试文本。"
        prompt = get_question_prompt(language='zh', text=text, number=2)
        
        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert text in prompt
        assert '2' in prompt
        assert '问题' in prompt
    
    def test_basic_question_prompt_turkish(self):
        """Test basic Turkish question prompt generation"""
        text = "Bu bir test metnidir."
        prompt = get_question_prompt(language='tr', text=text, number=4)
        
        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert text in prompt
        assert '4' in prompt
        assert 'Soru' in prompt
    
    def test_question_prompt_with_ga_pair(self):
        """Test question prompt with Genre-Audience pair"""
        text = "Sample text"
        ga_pair = {
            'active': True,
            'genre': 'Technical',
            'audience': 'Engineers'
        }
        
        prompt = get_question_prompt(
            language='en',
            text=text,
            active_ga_pair=ga_pair
        )
        
        assert 'Technical' in prompt
        assert 'Engineers' in prompt
        assert 'genre' in prompt.lower()
    
    def test_question_prompt_without_ga_pair(self):
        """Test question prompt without GA pair"""
        text = "Sample text"
        prompt = get_question_prompt(language='en', text=text)
        
        # Should not contain GA-specific content
        assert 'Genre' not in prompt or 'Optional' in prompt
    
    def test_question_prompt_default_number(self):
        """Test that default number is calculated from text length"""
        text = "a" * 1000  # 1000 characters
        prompt = get_question_prompt(language='en', text=text)
        
        # Should calculate number as len(text) // 240 = 4
        assert '4' in prompt or 'at least 4' in prompt.lower()
    
    def test_custom_question_prompt(self):
        """Test custom question prompt template"""
        custom = "Custom template with {{text}} and {{number}}"
        text = "test"
        
        prompt = get_question_prompt(
            language='en',
            text=text,
            number=5,
            custom_prompt=custom
        )
        
        assert prompt == "Custom template with test and 5"


class TestAnswerPrompts:
    """Tests for answer generation prompts"""
    
    def test_basic_answer_prompt_english(self):
        """Test basic English answer prompt generation"""
        text = "Python is a programming language."
        question = "What is Python?"
        
        prompt = get_answer_prompt(language='en', text=text, question=question)
        
        assert isinstance(prompt, str)
        assert text in prompt
        assert question in prompt
        assert 'answer' in prompt.lower()
    
    def test_basic_answer_prompt_chinese(self):
        """Test basic Chinese answer prompt generation"""
        text = "Python是一种编程语言。"
        question = "什么是Python？"
        
        prompt = get_answer_prompt(language='zh', text=text, question=question)
        
        assert text in prompt
        assert question in prompt
        assert '答案' in prompt
    
    def test_answer_prompt_with_label_template(self):
        """Test answer prompt with label-based template"""
        text = "Python is interpreted."
        question = "What type is Python?"
        template = {
            'answerType': 'label',
            'labels': ['Compiled', 'Interpreted', 'Other']
        }
        
        prompt = get_answer_prompt(
            language='en',
            text=text,
            question=question,
            question_template=template
        )
        
        assert 'Compiled' in prompt
        assert 'Interpreted' in prompt
        assert 'array' in prompt.lower()
    
    def test_answer_prompt_with_custom_format_template(self):
        """Test answer prompt with custom format template"""
        text = "Test content"
        question = "Test question"
        template = {
            'answerType': 'custom_format',
            'customFormat': '{"key": "value"}'
        }
        
        prompt = get_answer_prompt(
            language='en',
            text=text,
            question=question,
            question_template=template
        )
        
        assert '{"key": "value"}' in prompt
        assert 'format' in prompt.lower()
    
    def test_answer_prompt_with_description(self):
        """Test answer prompt with template description"""
        text = "Test"
        question = "Test?"
        template = {
            'answerType': 'text',
            'description': 'Custom description here'
        }
        
        prompt = get_answer_prompt(
            language='en',
            text=text,
            question=question,
            question_template=template
        )
        
        assert 'Custom description here' in prompt
    
    def test_custom_answer_prompt(self):
        """Test custom answer prompt template"""
        custom = "Q: {{question}} A: based on {{text}}"
        
        prompt = get_answer_prompt(
            language='en',
            text='context',
            question='query',
            custom_prompt=custom
        )
        
        assert prompt == "Q: query A: based on context"


class TestDataCleaningPrompts:
    """Tests for data cleaning prompts"""
    
    def test_basic_clean_prompt_english(self):
        """Test basic English cleaning prompt"""
        text = "Text with   extra  spaces"
        prompt = get_data_clean_prompt(language='en', text=text)
        
        assert isinstance(prompt, str)
        assert text in prompt
        assert 'clean' in prompt.lower()
        assert str(len(text)) in prompt
    
    def test_basic_clean_prompt_chinese(self):
        """Test basic Chinese cleaning prompt"""
        text = "需要清洗的文本"
        prompt = get_data_clean_prompt(language='zh', text=text)
        
        assert text in prompt
        assert '清洗' in prompt
    
    def test_basic_clean_prompt_turkish(self):
        """Test basic Turkish cleaning prompt"""
        text = "Temizlenecek metin"
        prompt = get_data_clean_prompt(language='tr', text=text)
        
        assert text in prompt
        assert 'Temizle' in prompt or 'temizle' in prompt.lower()
    
    def test_clean_prompt_includes_length(self):
        """Test that cleaning prompt includes text length"""
        text = "a" * 500
        prompt = get_data_clean_prompt(language='en', text=text)
        
        assert '500' in prompt
    
    def test_custom_clean_prompt(self):
        """Test custom cleaning prompt template"""
        custom = "Clean this: {{text}} ({{textLength}} chars)"
        text = "test"
        
        prompt = get_data_clean_prompt(
            language='en',
            text=text,
            custom_prompt=custom
        )
        
        assert prompt == "Clean this: test (4 chars)"


class TestDatasetEvaluationPrompts:
    """Tests for dataset evaluation prompts"""
    
    def test_basic_evaluation_prompt_english(self):
        """Test basic English evaluation prompt"""
        chunk = "Context text"
        question = "What is this?"
        answer = "This is context."
        
        prompt = get_dataset_evaluation_prompt(
            language='en',
            chunk_content=chunk,
            question=question,
            answer=answer
        )
        
        assert chunk in prompt
        assert question in prompt
        assert answer in prompt
        assert 'quality' in prompt.lower()
        assert 'score' in prompt.lower()
    
    def test_evaluation_prompt_distilled_content(self):
        """Test evaluation prompt with empty chunk (distilled dataset)"""
        prompt = get_dataset_evaluation_prompt(
            language='en',
            chunk_content='',
            question='What is AI?',
            answer='AI is artificial intelligence.'
        )
        
        assert 'Distilled Content' in prompt
    
    def test_evaluation_prompt_chinese(self):
        """Test Chinese evaluation prompt"""
        prompt = get_dataset_evaluation_prompt(
            language='zh',
            chunk_content='上下文',
            question='问题',
            answer='答案'
        )
        
        assert '上下文' in prompt
        assert '问题' in prompt
        assert '答案' in prompt
        assert '评估' in prompt
    
    def test_evaluation_prompt_includes_dimensions(self):
        """Test that evaluation prompt includes all dimensions"""
        prompt = get_dataset_evaluation_prompt(
            language='en',
            chunk_content='test',
            question='q',
            answer='a'
        )
        
        # Check for evaluation dimensions
        assert 'Question Quality' in prompt or 'question quality' in prompt.lower()
        assert 'Answer Quality' in prompt or 'answer quality' in prompt.lower()
        assert 'Relevance' in prompt or 'relevance' in prompt.lower()
        assert 'Consistency' in prompt or 'consistency' in prompt.lower()
    
    def test_custom_evaluation_prompt(self):
        """Test custom evaluation prompt template"""
        custom = "Evaluate: Q={{question}} A={{answer}} Context={{chunkContent}}"
        
        prompt = get_dataset_evaluation_prompt(
            language='en',
            chunk_content='ctx',
            question='q',
            answer='a',
            custom_prompt=custom
        )
        
        assert prompt == "Evaluate: Q=q A=a Context=ctx"


class TestUtilityFunctions:
    """Tests for utility functions"""
    
    def test_get_ga_prompt_active(self):
        """Test GA prompt generation when active"""
        ga_pair = {
            'active': True,
            'genre': 'Technical',
            'audience': 'Developers'
        }
        
        prompt = get_ga_prompt('en', ga_pair)
        
        assert 'Technical' in prompt
        assert 'Developers' in prompt
        assert len(prompt) > 0
    
    def test_get_ga_prompt_inactive(self):
        """Test GA prompt generation when inactive"""
        ga_pair = {
            'active': False,
            'genre': 'Technical',
            'audience': 'Developers'
        }
        
        prompt = get_ga_prompt('en', ga_pair)
        
        assert prompt == ''
    
    def test_get_ga_prompt_none(self):
        """Test GA prompt generation with None"""
        prompt = get_ga_prompt('en', None)
        assert prompt == ''
    
    def test_get_question_template_prompts_label(self):
        """Test question template prompts for label type"""
        template = {
            'answerType': 'label',
            'labels': ['A', 'B', 'C']
        }
        
        result = get_question_template_prompts(template, 'en')
        
        assert 'templatePrompt' in result
        assert 'outputFormatPrompt' in result
        assert 'A' in result['outputFormatPrompt']
        assert 'array' in result['outputFormatPrompt'].lower()
    
    def test_get_question_template_prompts_custom_format(self):
        """Test question template prompts for custom format"""
        template = {
            'answerType': 'custom_format',
            'customFormat': '{"format": "json"}'
        }
        
        result = get_question_template_prompts(template, 'en')
        
        assert '{"format": "json"}' in result['outputFormatPrompt']
    
    def test_get_question_template_prompts_with_description(self):
        """Test question template prompts with description"""
        template = {
            'answerType': 'text',
            'description': 'Test description'
        }
        
        result = get_question_template_prompts(template, 'en')
        
        assert 'Test description' in result['templatePrompt']
    
    def test_get_question_template_prompts_none(self):
        """Test question template prompts with None"""
        result = get_question_template_prompts(None, 'en')
        
        assert result['templatePrompt'] == ''
        assert result['outputFormatPrompt'] == ''


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
