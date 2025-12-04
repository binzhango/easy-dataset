"""
Answer generation prompt templates for Easy Dataset.

This module provides prompt templates for generating answers to questions
based on reference text chunks, with support for multiple languages,
chain-of-thought reasoning, and custom output formats.
"""

from typing import Dict, Optional, Any


# Chinese answer generation prompt
ANSWER_PROMPT_ZH = """
# Role: 微调数据集生成专家
## Profile:
- Description: 你是一名微调数据集生成专家，擅长从给定的内容中生成准确的问题答案，确保答案的准确性和相关性，你要直接回答用户问题，所有信息已内化为你的专业知识。

## Skills:
1. 答案必须基于给定的内容
2. 答案必须准确，不能胡编乱造
3. 答案必须与问题相关
4. 答案必须符合逻辑
5. 基于给定参考内容，用自然流畅的语言整合成一个完整答案，不需要提及文献来源或引用标记
   
## Workflow:
1. Take a deep breath and work on this problem step-by-step.
2. 首先，分析给定的文件内容
3. 然后，从内容中提取关键信息
4. 接着，生成与问题相关的准确答案
5. 最后，确保答案的准确性和相关性

## 参考内容：

------ 参考内容 Start ------
{{text}}
------ 参考内容 End ------

## 问题
{{question}}

## Constrains:
1. 答案必须基于给定的内容
2. 答案必须准确，必须与问题相关，不能胡编乱造
3. 答案必须充分、详细、包含所有必要的信息、适合微调大模型训练使用
4. 答案中不得出现 ' 参考 / 依据 / 文献中提到 ' 等任何引用性表述，只需呈现最终结论
{{templatePrompt}}
{{outputFormatPrompt}}
"""


# English answer generation prompt
ANSWER_PROMPT_EN = """
# Role: Fine-tuning Dataset Generation Expert
## Profile:
- Description: You are an expert in generating fine-tuning datasets, skilled at generating accurate answers to questions from the given content, ensuring the accuracy and relevance of the answers.

## Skills:
1. The answer must be based on the given content.
2. The answer must be accurate and not fabricated.
3. The answer must be relevant to the question.
4. The answer must be logical.

## Workflow:
1. Take a deep breath and work on this problem step-by-step.
2. First, analyze the given file content.
3. Then, extract key information from the content.
4. Next, generate an accurate answer related to the question.
5. Finally, ensure the accuracy and relevance of the answer.

## Reference Content:

------ Reference Content Start ------
{{text}}
------ Reference Content End ------

## Question
{{question}}

## Constrains:
1. The answer must be based on the given content.
2. The answer must be accurate and relevant to the question, and no fabricated information is allowed.
3. The answer must be comprehensive and detailed, containing all necessary information, and it is suitable for use in the training of fine-tuning large language models.
{{templatePrompt}}
{{outputFormatPrompt}}
"""


# Turkish answer generation prompt
ANSWER_PROMPT_TR = """
# Rol: İnce Ayar Veri Seti Üretim Uzmanı
## Profil:
- Açıklama: İnce ayar veri setleri oluşturmada uzman, verilen içerikten sorulara doğru cevaplar üretmede yetenekli, cevapların doğruluğunu ve alaka düzeyini sağlayan bir uzmansınız.

## Yetenekler:
1. Cevap verilen içeriğe dayanmalıdır.
2. Cevap doğru ve uydurma olmamalıdır.
3. Cevap soruyla alakalı olmalıdır.
4. Cevap mantıklı olmalıdır.

## İş Akışı:
1. Derin bir nefes alın ve bu problem üzerinde adım adım çalışın.
2. İlk olarak, verilen dosya içeriğini analiz edin.
3. Ardından, içerikten temel bilgileri çıkarın.
4. Sonra, soruyla ilgili doğru bir cevap oluşturun.
5. Son olarak, cevabın doğruluğunu ve alaka düzeyini sağlayın.

## Referans İçerik:

------ Referans İçerik Başlangıç ------
{{text}}
------ Referans İçerik Bitiş ------

## Soru
{{question}}

## Kısıtlamalar:
1. Cevap verilen içeriğe dayanmalıdır.
2. Cevap doğru ve soruyla alakalı olmalı, uydurma bilgiye izin verilmez.
3. Cevap kapsamlı ve detaylı olmalı, tüm gerekli bilgileri içermeli ve büyük dil modellerinin ince ayar eğitiminde kullanıma uygun olmalıdır.
{{templatePrompt}}
{{outputFormatPrompt}}
"""


def get_question_template_prompts(
    question_template: Optional[Dict[str, Any]],
    language: str
) -> Dict[str, str]:
    """
    Generate template-specific prompts for answer generation.
    
    This function handles custom answer formats including:
    - Label-based answers (select from predefined options)
    - Custom format answers (follow specific structure)
    - Free-form text answers (default)
    
    Args:
        question_template: Dictionary containing template configuration:
            - answerType: 'text', 'label', or 'custom_format'
            - description: Optional description to add to prompt
            - labels: List of valid labels (for answerType='label')
            - customFormat: Custom format specification (for answerType='custom_format')
        language: Language code ('en', 'zh', 'tr')
        
    Returns:
        Dictionary with 'templatePrompt' and 'outputFormatPrompt' keys
    """
    template_prompt = ''
    output_format_prompt = ''
    
    if not question_template:
        return {
            'templatePrompt': template_prompt,
            'outputFormatPrompt': output_format_prompt
        }
    
    # Add description if provided
    description = question_template.get('description', '')
    if description:
        template_prompt = f"\n\n{description}"
    
    answer_type = question_template.get('answerType', 'text')
    
    # Handle label-based answers
    if answer_type == 'label':
        labels = question_template.get('labels', [])
        labels_str = str(labels) if isinstance(labels, list) else labels
        
        if language == 'en':
            output_format_prompt = (
                f"\n\n ## Output Format \n\n "
                f"Final output must be a string array, and must be selected from the following array, "
                f"if the answer is not in the target array, return: [\"other\"] "
                f"No additional information can be added: \n\n{labels_str}"
            )
        elif language == 'tr':
            output_format_prompt = (
                f"\n\n ## Çıktı Formatı \n\n "
                f"Nihai çıktı bir dize dizisi olmalı ve aşağıdaki diziden seçilmelidir, "
                f"cevap hedef dizide değilse, şunu döndürün: [\"diğer\"] "
                f"Ek bilgi eklenemez: \n\n{labels_str}"
            )
        else:  # Chinese
            output_format_prompt = (
                f"\n\n ## 输出格式 \n\n "
                f"最终输出必须是一个字符串数组，而且必须在以下数组中选择，"
                f"如果答案不在目标数组中，返回：[\"其他\"] "
                f"不得额外添加任何其他信息：\n\n{labels_str}"
            )
    
    # Handle custom format answers
    elif answer_type == 'custom_format':
        custom_format = question_template.get('customFormat', '')
        
        if language == 'en':
            output_format_prompt = (
                f"\n\n ## Output Format \n\n "
                f"Final output must strictly follow the following structure, "
                f"no additional information can be added: \n\n{custom_format}"
            )
        elif language == 'tr':
            output_format_prompt = (
                f"\n\n ## Çıktı Formatı \n\n "
                f"Nihai çıktı aşağıdaki yapıyı kesinlikle takip etmelidir, "
                f"ek bilgi eklenemez: \n\n{custom_format}"
            )
        else:  # Chinese
            output_format_prompt = (
                f"\n\n ## 输出格式 \n\n "
                f"最终输出必须严格遵循以下结构，"
                f"不得额外添加任何其他信息：\n\n{custom_format}"
            )
    
    return {
        'templatePrompt': template_prompt,
        'outputFormatPrompt': output_format_prompt
    }


def substitute_variables(template: str, variables: Dict[str, Any]) -> str:
    """
    Substitute template variables with actual values.
    
    Args:
        template: Template string with {{variable}} placeholders
        variables: Dictionary of variable names to values
        
    Returns:
        Template with all variables substituted
    """
    result = template
    for key, value in variables.items():
        placeholder = f"{{{{{key}}}}}"
        result = result.replace(placeholder, str(value))
    return result


def get_answer_prompt(
    language: str,
    text: str,
    question: str,
    question_template: Optional[Dict[str, Any]] = None,
    custom_prompt: Optional[str] = None
) -> str:
    """
    Generate answer generation prompt with context injection.
    
    This function creates a complete prompt for generating answers by:
    1. Including the reference text (chunk) as context
    2. Including the question to be answered
    3. Applying any custom formatting requirements from question templates
    4. Supporting chain-of-thought and detailed explanation modes
    
    Args:
        language: Language code ('en', 'zh', 'tr')
        text: Reference text chunk containing the answer
        question: Question to be answered
        question_template: Optional template configuration for custom answer formats
        custom_prompt: Optional custom prompt template to use instead of default
        
    Returns:
        Complete prompt ready for LLM
    """
    # Select base prompt template
    if custom_prompt:
        base_prompt = custom_prompt
    else:
        if language == 'en':
            base_prompt = ANSWER_PROMPT_EN
        elif language == 'tr':
            base_prompt = ANSWER_PROMPT_TR
        else:
            base_prompt = ANSWER_PROMPT_ZH
    
    # Get template-specific prompts
    template_prompts = get_question_template_prompts(question_template, language)
    
    # Prepare variables for substitution
    variables = {
        'text': text,
        'question': question,
        'templatePrompt': template_prompts['templatePrompt'],
        'outputFormatPrompt': template_prompts['outputFormatPrompt']
    }
    
    # Substitute all variables
    return substitute_variables(base_prompt, variables)


__all__ = [
    'ANSWER_PROMPT_ZH',
    'ANSWER_PROMPT_EN',
    'ANSWER_PROMPT_TR',
    'get_question_template_prompts',
    'substitute_variables',
    'get_answer_prompt'
]
