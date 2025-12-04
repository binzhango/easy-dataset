"""
Question generation prompt templates for Easy Dataset.

This module provides prompt templates for generating questions from text chunks
in multiple languages (English, Chinese, Turkish).
"""

from typing import Dict, Optional, Any


# Chinese question generation prompt
QUESTION_PROMPT_ZH = """
# Role: 文本问题生成专家
## Profile:
- Description: 你是一名专业的文本分析与问题设计专家，能够从复杂文本中提炼关键信息并产出可用于模型微调的高质量问题集合。
- Input Length: {{textLength}} 字
- Output Goal: 生成不少于 {{number}} 个高质量问题，用于构建问答训练数据集。

## Skills:
1. 能够全面理解原文内容，识别核心概念、事实与逻辑结构。
2. 擅长设计具有明确答案指向性的问题，覆盖文本多个侧面。
3. 善于控制问题难度与类型，保证多样性与代表性。
4. 严格遵守格式规范，确保输出可直接用于程序化处理。

## Workflow:
1. **文本解析**：通读全文，分段识别关键实体、事件、数值与结论。
2. **问题设计**：基于信息密度和重要性选择最佳提问切入点{{gaPromptNote}}。
3. **质量检查**：逐条校验问题，确保：
   - 问题答案可在原文中直接找到依据。
   - 问题之间主题不重复、角度不雷同。
   - 语言表述准确、无歧义且符合常规问句形式。
   {{gaPromptCheck}}

## Constraints:
1. 所有问题必须严格依据原文内容，不得添加外部信息或假设情境。
2. 问题需覆盖文本的不同主题、层级或视角，避免集中于单一片段。
3. 禁止输出与材料元信息相关的问题（如作者、章节、目录等）。
4. 问题不得包含"报告/文章/文献/表格中提到"等表述，需自然流畅。
5. 输出不少于 {{number}} 个问题，且保持格式一致。

## Output Format:
- 使用合法的 JSON 数组，仅包含字符串元素。
- 字段必须使用英文双引号。
- 严格遵循以下结构：
```
["问题1", "问题2", "..."]
```

## Output Example:
```
["人工智能伦理框架应包含哪些核心要素？", "民法典对个人数据保护有哪些新规定？"]
```

## Text to Analyze:
{{text}}

## GA Instruction (Optional):
{{gaPrompt}}
"""


# English question generation prompt
QUESTION_PROMPT_EN = """
# Role: Text Question Generation Expert
## Profile:
- Description: You are an expert in text analysis and question design, capable of extracting key information from complex passages and producing high-quality questions for fine-tuning datasets.
- Input Length: {{textLength}} characters
- Output Goal: Generate at least {{number}} high-quality questions suitable for training data.

## Skills:
1. Comprehend the source text thoroughly and identify core concepts, facts, and logical structures.
2. Design questions with clear answer orientation that cover multiple aspects of the text.
3. Balance difficulty and variety to ensure representative coverage of the content.
4. Enforce strict formatting so the output can be consumed programmatically.

## Workflow:
1. **Text Parsing**: Read the entire passage, segment it, and capture key entities, events, metrics, and conclusions.
2. **Question Design**: Select the most informative focal points to craft questions{{gaPromptNote}}.
3. **Quality Check**: Validate each question to ensure:
   - The answer can be located directly in the original text.
   - Questions do not duplicate topics or angles.
   - Wording is precise, unambiguous, and uses natural interrogative phrasing.
   {{gaPromptCheck}}

## Constraints:
1. Every question must be grounded strictly in the provided text; no external information or hypothetical scenarios.
2. Cover diverse themes, layers, or perspectives from the passage; avoid clustering around one segment.
3. Do not include questions about meta information (author, chapters, table of contents, etc.).
4. Avoid phrases such as "in the report/article/literature/table"; questions must read naturally.
5. Produce at least {{number}} questions with consistent formatting.

## Output Format:
- Return a valid JSON array containing only strings.
- Use double quotes for all strings.
- Follow this exact structure:
```
["Question 1", "Question 2", "..."]
```

## Output Example:
```
["What core elements should an AI ethics framework include?", "What new regulations does the Civil Code have for personal data protection?"]
```

## Text to Analyze:
{{text}}

## GA Instruction (Optional):
{{gaPrompt}}
"""


# Turkish question generation prompt
QUESTION_PROMPT_TR = """
# Rol: Metin Soru Üretim Uzmanı
## Profil:
- Açıklama: Karmaşık metinlerden temel bilgileri çıkarabilen ve ince ayar veri setleri için yüksek kaliteli sorular üretebilen bir metin analizi ve soru tasarımı uzmanısınız.
- Girdi Uzunluğu: {{textLength}} karakter
- Çıktı Hedefi: Eğitim verisi için uygun en az {{number}} yüksek kaliteli soru üretin.

## Yetenekler:
1. Kaynak metni tamamen anlayın ve temel kavramları, gerçekleri ve mantıksal yapıları tanımlayın.
2. Metnin birden fazla yönünü kapsayan net cevap yönlendirmeli sorular tasarlayın.
3. İçeriğin temsili kapsamını sağlamak için zorluk ve çeşitlilik dengesini kurun.
4. Çıktının programatik olarak tüketilebilmesi için katı biçimlendirme uygulayın.

## İş Akışı:
1. **Metin Ayrıştırma**: Tüm pasajı okuyun, bölümlere ayırın ve temel varlıkları, olayları, metrikleri ve sonuçları yakalayın.
2. **Soru Tasarımı**: Soru oluşturmak için en bilgilendirici odak noktalarını seçin{{gaPromptNote}}.
3. **Kalite Kontrolü**: Her soruyu doğrulayarak şunları sağlayın:
   - Cevap doğrudan orijinal metinde bulunabilir.
   - Sorular konuları veya açıları tekrar etmez.
   - İfade kesin, belirsiz değil ve doğal soru tümcecikleri kullanır.
   {{gaPromptCheck}}

## Kısıtlamalar:
1. Her soru yalnızca sağlanan metne dayanmalıdır; harici bilgi veya varsayımsal senaryolar olmamalıdır.
2. Pasajdan farklı temaları, katmanları veya bakış açılarını kapsayın; tek bir segment etrafında kümelenmekten kaçının.
3. Meta bilgilerle ilgili sorular eklemeyin (yazar, bölümler, içindekiler tablosu vb.).
4. "Raporda/makalede/literatürde/tabloda" gibi ifadelerden kaçının; sorular doğal okunmalıdır.
5. Tutarlı biçimlendirmeyle en az {{number}} soru üretin.

## Çıktı Formatı:
- Yalnızca string içeren geçerli bir JSON dizisi döndürün.
- Tüm stringler için çift tırnak kullanın.
- Bu yapıyı tam olarak takip edin:
```
["Soru 1", "Soru 2", "..."]
```

## Çıktı Örneği:
```
["Bir yapay zeka etik çerçevesi hangi temel unsurları içermelidir?", "Medeni Kanun kişisel veri koruma için hangi yeni düzenlemelere sahiptir?"]
```

## Analiz Edilecek Metin:
{{text}}

## GA Talimatı (Opsiyonel):
{{gaPrompt}}
"""


# Genre-Audience (GA) prompt templates
GA_QUESTION_PROMPT_ZH = """
**目标体裁**: {{genre}}
**目标受众**: {{audience}}

请确保：
1. 问题应完全符合「{{genre}}」所定义的风格、焦点和深度等等属性。
2. 问题应考虑到「{{audience}}」的知识水平、认知特点和潜在兴趣点。
3. 从该受众群体的视角和需求出发提出问题
4. 保持问题的针对性和实用性，确保问题-答案的风格一致性
5. 问题应具有一定的清晰度和具体性，避免过于宽泛或模糊。
"""


GA_QUESTION_PROMPT_EN = """
## Special Requirements - Genre & Audience Perspective Questioning:
Adjust your questioning approach and question style based on the following genre and audience combination:

**Target Genre**: {{genre}}
**Target Audience**: {{audience}}

Please ensure:
1. The question should fully conform to the style, focus, depth, and other attributes defined by "{{genre}}".
2. The question should consider the knowledge level, cognitive characteristics, and potential points of interest of "{{audience}}".
3. Propose questions from the perspective and needs of this audience group.
4. Maintain the specificity and practicality of the questions, ensuring consistency in the style of questions and answers.
5. The question should have a certain degree of clarity and specificity, avoiding being too broad or vague.
"""


GA_QUESTION_PROMPT_TR = """
## Özel Gereksinimler - Tür & Hedef Kitle Perspektifi Sorgulama:
Aşağıdaki tür ve hedef kitle kombinasyonuna göre sorgulama yaklaşımınızı ve soru stilinizi ayarlayın:

**Hedef Tür**: {{genre}}
**Hedef Kitle**: {{audience}}

Lütfen şunları sağlayın:
1. Soru, "{{genre}}" tarafından tanımlanan stil, odak, derinlik ve diğer özelliklere tam olarak uygun olmalıdır.
2. Soru, "{{audience}}" hedef kitlesinin bilgi seviyesini, bilişsel özelliklerini ve potansiyel ilgi noktalarını dikkate almalıdır.
3. Bu hedef kitle grubunun bakış açısından ve ihtiyaçlarından yola çıkarak sorular sorun.
4. Soruların özgüllüğünü ve pratikliğini koruyun, soru-cevap stilinde tutarlılık sağlayın.
5. Soru belirli bir netlik ve özgüllüğe sahip olmalı, çok geniş veya belirsiz olmaktan kaçınmalıdır.
"""


def get_ga_prompt(language: str, active_ga_pair: Optional[Dict[str, Any]] = None) -> str:
    """
    Build Genre-Audience (GA) prompt based on language and active GA pair.
    
    Args:
        language: Language code ('en', 'zh', 'tr')
        active_ga_pair: Dictionary containing 'genre', 'audience', and 'active' keys
        
    Returns:
        Formatted GA prompt string, or empty string if no active GA pair
    """
    if not active_ga_pair or not active_ga_pair.get('active'):
        return ''
    
    # Select appropriate GA prompt template based on language
    if language == 'en':
        prompt = GA_QUESTION_PROMPT_EN
    elif language == 'tr':
        prompt = GA_QUESTION_PROMPT_TR
    else:
        prompt = GA_QUESTION_PROMPT_ZH
    
    # Replace genre and audience placeholders
    genre = active_ga_pair.get('genre', '')
    audience = active_ga_pair.get('audience', '')
    
    return prompt.replace('{{genre}}', genre).replace('{{audience}}', audience)


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


def get_question_prompt(
    language: str,
    text: str,
    number: Optional[int] = None,
    active_ga_pair: Optional[Dict[str, Any]] = None,
    custom_prompt: Optional[str] = None
) -> str:
    """
    Generate question generation prompt with template variable substitution.
    
    Args:
        language: Language code ('en', 'zh', 'tr')
        text: Text to analyze and generate questions from
        number: Number of questions to generate (defaults to text_length / 240)
        active_ga_pair: Optional genre-audience pair for specialized questioning
        custom_prompt: Optional custom prompt template to use instead of default
        
    Returns:
        Complete prompt ready for LLM
    """
    # Calculate default number of questions based on text length
    if number is None:
        number = max(1, len(text) // 240)
    
    # Select base prompt template
    if custom_prompt:
        base_prompt = custom_prompt
    else:
        if language == 'en':
            base_prompt = QUESTION_PROMPT_EN
        elif language == 'tr':
            base_prompt = QUESTION_PROMPT_TR
        else:
            base_prompt = QUESTION_PROMPT_ZH
    
    # Build GA prompt if provided
    ga_prompt_text = get_ga_prompt(language, active_ga_pair)
    
    # Determine GA-related notes and checks
    if ga_prompt_text:
        if language == 'en':
            ga_prompt_note = ', and incorporate the specified genre-audience perspective'
            ga_prompt_check = '- Question style matches the specified genre and audience'
        elif language == 'tr':
            ga_prompt_note = ', ve belirtilen tür-hedef kitle perspektifini dahil edin'
            ga_prompt_check = '- Soru stili belirtilen tür ve hedef kitle ile eşleşir'
        else:
            ga_prompt_note = '，并结合指定的体裁受众视角'
            ga_prompt_check = '- 问题风格与指定的体裁受众匹配'
    else:
        ga_prompt_note = ''
        ga_prompt_check = ''
    
    # Prepare variables for substitution
    variables = {
        'textLength': len(text),
        'number': number,
        'text': text,
        'gaPrompt': ga_prompt_text,
        'gaPromptNote': ga_prompt_note,
        'gaPromptCheck': ga_prompt_check
    }
    
    # Substitute all variables
    return substitute_variables(base_prompt, variables)


__all__ = [
    'QUESTION_PROMPT_ZH',
    'QUESTION_PROMPT_EN',
    'QUESTION_PROMPT_TR',
    'GA_QUESTION_PROMPT_ZH',
    'GA_QUESTION_PROMPT_EN',
    'GA_QUESTION_PROMPT_TR',
    'get_ga_prompt',
    'substitute_variables',
    'get_question_prompt'
]
