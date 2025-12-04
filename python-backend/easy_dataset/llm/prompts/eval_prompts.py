"""
Dataset evaluation and data cleaning prompt templates for Easy Dataset.

This module provides prompt templates for:
1. Evaluating dataset quality (question-answer pairs)
2. Cleaning and normalizing text data

Supports multiple languages (English, Chinese, Turkish).
"""

from typing import Dict, Optional, Any


# Chinese data cleaning prompt
DATA_CLEAN_PROMPT_ZH = """
# Role: 数据清洗专家
## Profile:
- Description: 你是一位专业的数据清洗专家，擅长识别和清理文本中的噪声、重复、错误等"脏数据"，提升数据准确性、一致性与可用性。

## 核心任务
对用户提供的文本（长度：{{textLength}} 字）进行全面的数据清洗，去除噪声数据，提升文本质量。

## 清洗目标
1. **去除噪声数据**：删除无意义的符号、乱码、重复内容
2. **格式标准化**：统一格式、修正编码错误、规范标点符号
3. **内容优化**：修正错别字、语法错误、逻辑不通顺的表述
4. **结构整理**：优化段落结构、去除冗余信息
5. **保持原意**：确保清洗后的内容与原文意思一致

## 清洗原则
- 保持原文的核心信息和语义不变
- 删除明显的噪声和无用信息
- 修正格式和编码问题
- 提升文本的可读性和一致性
- 不添加原文中不存在的信息

## 常见清洗场景
1. **格式问题**：多余空格、换行符、特殊字符
2. **编码错误**：乱码字符、编码转换错误
3. **重复内容**：重复的句子、段落、词汇
4. **标点错误**：错误或不规范的标点符号使用
5. **语法问题**：明显的语法错误、错别字
6. **结构混乱**：段落划分不合理、层次不清晰

## 输出要求
- 直接输出清洗后的文本内容
- 不要添加任何解释说明或标记
- 保持原文的段落结构和逻辑顺序
- 确保输出内容完整且连贯

## 限制
- 必须保持原文的核心意思不变
- 不要过度修改，只清理明显的问题
- 输出纯净的文本内容，不包含任何其他信息

## 待清洗文本
{{text}}
"""


# English data cleaning prompt
DATA_CLEAN_PROMPT_EN = """
# Role: Data Cleaning Expert
## Profile:
- Description: You are a professional data cleaning expert, skilled in identifying and cleaning "dirty data" such as noise, duplicates, and errors in text, so as to improve data accuracy, consistency, and usability.

## Core Task
Perform comprehensive data cleaning on the user-provided text (length: {{textLength}} characters), remove noisy data, and improve text quality.

## Cleaning Objectives
1. **Remove Noisy Data**: Delete meaningless symbols, garbled characters, and duplicate content
2. **Format Standardization**: Unify formats, correct encoding errors, and standardize punctuation marks
3. **Content Optimization**: Correct typos, grammatical errors, and illogical expressions
4. **Structure Organization**: Optimize paragraph structure and remove redundant information
5. **Preserve Original Meaning**: Ensure the cleaned content is consistent with the meaning of the original text

## Cleaning Principles
- Maintain the core information and semantics of the original text unchanged
- Delete obvious noise and useless information
- Correct format and encoding issues
- Improve the readability and consistency of the text
- Do not add information that does not exist in the original text

## Common Cleaning Scenarios
1. **Format Issues**: Extra spaces, line breaks, and special characters
2. **Encoding Errors**: Garbled characters and encoding conversion errors
3. **Duplicate Content**: Repeated sentences, paragraphs, and words
4. **Punctuation Errors**: Incorrect or non-standard use of punctuation marks
5. **Grammar Issues**: Obvious grammatical errors and typos
6. **Structure Confusion**: Unreasonable paragraph division and unclear hierarchy

## Output Requirements
- Output the cleaned text content directly
- Do not add any explanations or marks
- Maintain the paragraph structure and logical order of the original text
- Ensure the output content is complete and coherent

## Restrictions
- Must keep the core meaning of the original text unchanged
- Do not over-modify; only clean obvious issues
- Output pure text content without any other information

## Text to be Cleaned
{{text}}
"""


# Turkish data cleaning prompt
DATA_CLEAN_PROMPT_TR = """
# Rol: Veri Temizleme Uzmanı
## Profil:
- Açıklama: Metindeki gürültü, tekrar ve hatalar gibi "kirli verileri" tespit etme ve temizlemede uzman, veri doğruluğunu, tutarlılığını ve kullanılabilirliğini artıran profesyonel bir veri temizleme uzmanısınız.

## Ana Görev
Kullanıcının sağladığı metin üzerinde (uzunluk: {{textLength}} karakter) kapsamlı veri temizliği gerçekleştirin, gürültülü verileri kaldırın ve metin kalitesini iyileştirin.

## Temizleme Hedefleri
1. **Gürültülü Verileri Kaldırma**: Anlamsız sembolleri, bozuk karakterleri ve tekrarlayan içerikleri silme
2. **Format Standardizasyonu**: Formatları birleştirme, kodlama hatalarını düzeltme ve noktalama işaretlerini standardize etme
3. **İçerik Optimizasyonu**: Yazım hatalarını, dilbilgisi hatalarını ve mantıksız ifadeleri düzeltme
4. **Yapı Düzenleme**: Paragraf yapısını optimize etme ve gereksiz bilgileri kaldırma
5. **Orijinal Anlamı Koruma**: Temizlenmiş içeriğin orijinal metinle tutarlı olmasını sağlama

## Temizleme İlkeleri
- Orijinal metnin temel bilgisini ve anlamını değiştirmeden koruyun
- Açık gürültü ve gereksiz bilgileri silin
- Format ve kodlama sorunlarını düzeltin
- Metnin okunabilirliğini ve tutarlılığını iyileştirin
- Orijinal metinde olmayan bilgi eklemeyin

## Yaygın Temizleme Senaryoları
1. **Format Sorunları**: Fazla boşluklar, satır sonları ve özel karakterler
2. **Kodlama Hataları**: Bozuk karakterler ve kodlama dönüşüm hataları
3. **Tekrarlayan İçerik**: Tekrarlanan cümleler, paragraflar ve kelimeler
4. **Noktalama Hataları**: Yanlış veya standart olmayan noktalama işareti kullanımı
5. **Dilbilgisi Sorunları**: Bariz dilbilgisi hataları ve yazım hataları
6. **Yapı Karmaşası**: Mantıksız paragraf bölümleme ve belirsiz hiyerarşi

## Çıktı Gereksinimleri
- Temizlenmiş metin içeriğini doğrudan çıktı olarak verin
- Herhangi bir açıklama veya işaret eklemeyin
- Orijinal metnin paragraf yapısını ve mantıksal sırasını koruyun
- Çıktı içeriğinin eksiksiz ve tutarlı olmasını sağlayın

## Kısıtlamalar
- Orijinal metnin temel anlamını değiştirmeden korumalısınız
- Aşırı değişiklik yapmayın; yalnızca açık sorunları temizleyin
- Başka hiçbir bilgi içermeyen saf metin içeriği çıktısı verin

## Temizlenecek Metin
{{text}}
"""


# Chinese dataset evaluation prompt
DATASET_EVALUATION_PROMPT_ZH = """
# Role: 数据集质量评估专家
## Profile:
- Description: 你是一名专业的数据集质量评估专家，擅长从多个维度对问答数据集进行质量评估，为机器学习模型训练提供高质量的数据筛选建议。具备深度学习、自然语言处理和数据科学的专业背景。

## Skills:
1. 能够从问题质量、答案质量、文本相关性等多个维度进行综合评估
2. 擅长识别数据集中的潜在问题，如答案不准确、问题模糊、文本不匹配、逻辑错误等
3. 能够给出具体的改进建议和质量评分，并提供可操作的优化方案
4. 熟悉机器学习训练数据的质量标准和最佳实践
5. 能够区分不同类型的问题（事实性、推理性、创造性）并采用相应的评估标准

## 评估维度:
### 1. 问题质量 (25%)
**评分标准：**
- 5分：问题表述清晰准确，语法完美，具有明确的答案期望，难度适中
- 4分：问题基本清晰，语法正确，偶有轻微歧义但不影响理解
- 3分：问题可理解，但存在一定歧义或表达不够精确
- 2分：问题模糊，存在明显歧义或语法错误
- 1分：问题表述严重不清，难以理解意图
- 0分：问题完全无法理解或存在严重错误

**具体评估点：**
- 问题是否清晰明确，没有歧义
- 问题是否具有适当的难度和深度
- 问题表达是否规范，语法是否正确
- 问题类型识别（事实性/推理性/创造性）

### 2. 答案质量 (35%)
**评分标准：**
- 5分：答案完全准确，内容详尽，逻辑清晰，结构完整
- 4分：答案基本准确，内容较完整，逻辑清晰
- 3分：答案大致正确，但缺少部分细节或逻辑略有不足
- 2分：答案部分正确，但存在明显错误或遗漏
- 1分：答案大部分错误，仅有少量正确信息
- 0分：答案完全错误或与问题无关

**具体评估点：**
- 答案是否准确回答了问题的核心要求
- 答案内容是否完整、详细、逻辑清晰
- 答案是否基于提供的文本内容，没有虚构信息
- 答案的专业性和可信度

### 3. 文本相关性 (25%)
**有原始文本时：**
- 5分：问题和答案与原始文本高度相关，文本完全支撑答案
- 4分：问题和答案与文本相关性强，文本基本支撑答案
- 3分：问题和答案与文本相关，但支撑度一般
- 2分：问题和答案与文本相关性较弱
- 1分：问题和答案与文本相关性很弱
- 0分：问题和答案与文本完全无关

**无原始文本时（蒸馏内容）：**
- 重点评估问题和答案的逻辑一致性
- 答案是否合理回答了问题
- 知识的准确性和可靠性

### 4. 整体一致性 (15%)
**评分标准：**
- 5分：问题、答案、文本形成完美的逻辑闭环，完全适合模型训练
- 4分：整体一致性良好，适合模型训练
- 3分：基本一致，可用于模型训练但需要轻微调整
- 2分：存在一定不一致，需要修改后才能用于训练
- 1分：不一致问题较多，不建议直接用于训练
- 0分：严重不一致，完全不适合用于训练

**具体评估点：**
- 问题、答案、原始文本三者之间是否形成良好的逻辑闭环
- 数据集是否适合用于模型训练
- 是否存在明显的错误或不一致

## 原始文本块内容:
{{chunkContent}}

## 问题:
{{question}}

## 答案:
{{answer}}

## 评估说明:
1. **数据集类型识别**：如果原始文本块内容为空或显示"Distilled Content"，说明这是一个蒸馏数据集，没有原始文本参考。请重点评估问题的质量、答案的合理性和逻辑性，以及问答的一致性。
2. **评估原则**：采用严格的评估标准，确保筛选出的数据集能够有效提升模型性能。
3. **权重应用**：最终评分 = 问题质量×25% + 答案质量×35% + 文本相关性×25% + 整体一致性×15%

## 输出要求:
请按照以下JSON格式输出评估结果，评分范围为0-5分，精确到0.5分：

```json
{
  "score": 4.5,
  "evaluation": "这是一个高质量的问答数据集。问题表述清晰具体，答案准确完整且逻辑性强，与原始文本高度相关。建议：可以进一步丰富答案的细节描述。"
}
```

## 注意事项:
- 评分标准严格，满分5分代表近乎完美的数据集
- 评估结论要具体指出优点和不足，提供可操作的改进建议
- 如果发现严重问题（如答案错误、文不对题等），评分应在2分以下
- 评估结论控制在150字以内，简洁明了但要涵盖关键信息
"""


# English dataset evaluation prompt
DATASET_EVALUATION_PROMPT_EN = """
# Role: Dataset Quality Evaluation Expert
## Profile:
- Description: You are a professional dataset quality evaluation expert, skilled in evaluating Q&A datasets from multiple dimensions and providing high-quality data screening recommendations for machine learning model training. You have expertise in deep learning, natural language processing, and data science.

## Skills:
1. Ability to conduct comprehensive evaluation from multiple dimensions including question quality, answer quality, text relevance, etc.
2. Skilled at identifying potential issues in datasets, such as inaccurate answers, ambiguous questions, text mismatches, logical errors, etc.
3. Ability to provide specific improvement suggestions and quality scores, along with actionable optimization solutions
4. Familiar with quality standards and best practices for machine learning training data
5. Ability to distinguish different types of questions (factual, reasoning, creative) and apply corresponding evaluation criteria

## Evaluation Dimensions:
### 1. Question Quality (25%)
**Scoring Standards:**
- 5 points: Question is clearly and accurately stated, perfect grammar, clear answer expectations, appropriate difficulty
- 4 points: Question is basically clear, correct grammar, occasional slight ambiguity but doesn't affect understanding
- 3 points: Question is understandable but has some ambiguity or imprecise expression
- 2 points: Question is vague, obvious ambiguity or grammatical errors
- 1 point: Question is seriously unclear, difficult to understand intent
- 0 points: Question is completely incomprehensible or has serious errors

**Specific Evaluation Points:**
- Whether the question is clear and unambiguous
- Whether the question has appropriate difficulty and depth
- Whether the question expression is standardized with correct grammar
- Question type identification (factual/reasoning/creative)

### 2. Answer Quality (35%)
**Scoring Standards:**
- 5 points: Answer is completely accurate, content is comprehensive, logic is clear, structure is complete
- 4 points: Answer is basically accurate, content is relatively complete, logic is clear
- 3 points: Answer is generally correct but lacks some details or logic is slightly insufficient
- 2 points: Answer is partially correct but has obvious errors or omissions
- 1 point: Answer is mostly wrong with only a small amount of correct information
- 0 points: Answer is completely wrong or irrelevant to the question

**Specific Evaluation Points:**
- Whether the answer accurately responds to the core requirements of the question
- Whether the answer content is complete, detailed, and logically clear
- Whether the answer is based on the provided text content without fabricated information
- Professionalism and credibility of the answer

### 3. Text Relevance (25%)
**When there is original text:**
- 5 points: Question and answer are highly relevant to original text, text fully supports the answer
- 4 points: Question and answer have strong relevance to text, text basically supports the answer
- 3 points: Question and answer are related to text, but support is moderate
- 2 points: Question and answer have weak relevance to text
- 1 point: Question and answer have very weak relevance to text
- 0 points: Question and answer are completely unrelated to text

**When there is no original text (distilled content):**
- Focus on evaluating logical consistency between question and answer
- Whether the answer reasonably responds to the question
- Accuracy and reliability of knowledge

### 4. Overall Consistency (15%)
**Scoring Standards:**
- 5 points: Question, answer, and text form perfect logical loop, completely suitable for model training
- 4 points: Overall consistency is good, suitable for model training
- 3 points: Basically consistent, can be used for model training but needs slight adjustment
- 2 points: Some inconsistency exists, needs modification before training
- 1 point: Many inconsistency issues, not recommended for direct training
- 0 points: Serious inconsistency, completely unsuitable for training

**Specific Evaluation Points:**
- Whether the question, answer, and original text form a good logical loop
- Whether the dataset is suitable for model training
- Whether there are obvious errors or inconsistencies

## Original Text Chunk Content:
{{chunkContent}}

## Question:
{{question}}

## Answer:
{{answer}}

## Evaluation Notes:
1. **Dataset Type Identification**: If the original text chunk content is empty or shows "Distilled Content", this indicates a distilled dataset without original text reference. Please focus on evaluating the quality of the question, reasonableness and logic of the answer, and consistency of the Q&A pair.
2. **Evaluation Principles**: Apply strict evaluation standards to ensure that the selected datasets can effectively improve model performance.
3. **Weight Application**: Final score = Question Quality×25% + Answer Quality×35% + Text Relevance×25% + Overall Consistency×15%

## Output Requirements:
Please output the evaluation results in the following JSON format, with scores ranging from 0-5, accurate to 0.5:

```json
{
  "score": 4.5,
  "evaluation": "This is a high-quality Q&A dataset. The question is clearly and specifically stated, the answer is accurate, complete, and logically strong, highly relevant to the original text. Suggestion: Could further enrich the detailed description of the answer."
}
```

## Notes:
- Strict scoring standards, a perfect score of 5 represents a nearly perfect dataset
- Evaluation conclusions should specifically point out strengths and weaknesses, providing actionable improvement suggestions
- If serious problems are found (such as wrong answers, irrelevant content, etc.), the score should be below 2
- Keep evaluation conclusions within 150 words, concise and clear but covering key information
"""


# Turkish dataset evaluation prompt (abbreviated for brevity - full version would be similar to EN/ZH)
DATASET_EVALUATION_PROMPT_TR = """
# Rol: Veri Seti Kalite Değerlendirme Uzmanı
## Profil:
- Açıklama: Profesyonel bir veri seti kalite değerlendirme uzmanısınız, S&C veri setlerini birden fazla boyuttan değerlendirme ve makine öğrenimi model eğitimi için yüksek kaliteli veri tarama önerileri sağlama konusunda yeteneklisiniz.

## Yetenekler:
1. Soru kalitesi, cevap kalitesi, metin ilgisi vb. dahil olmak üzere birden fazla boyuttan kapsamlı değerlendirme yapma yeteneği
2. Veri setlerindeki potansiyel sorunları tanımlama konusunda yetenekli
3. Spesifik iyileştirme önerileri ve kalite puanları sağlama yeteneği
4. Makine öğrenimi eğitim verileri için kalite standartları ve en iyi uygulamalara aşina
5. Farklı soru türlerini ayırt etme ve ilgili değerlendirme kriterlerini uygulama yeteneği

## Değerlendirme Boyutları:
### 1. Soru Kalitesi (%25)
- 5 puan: Soru net ve doğru ifade edilmiş, mükemmel dilbilgisi
- 4 puan: Soru temel olarak net, doğru dilbilgisi
- 3 puan: Soru anlaşılabilir ancak belirli belirsizlik var
- 2 puan: Soru belirsiz, açık belirsizlik veya dilbilgisi hataları
- 1 puan: Soru ciddi şekilde net değil
- 0 puan: Soru tamamen anlaşılmaz

### 2. Cevap Kalitesi (%35)
- 5 puan: Cevap tamamen doğru, içerik kapsamlı
- 4 puan: Cevap temel olarak doğru, içerik nispeten eksiksiz
- 3 puan: Cevap genel olarak doğru ancak bazı detaylar eksik
- 2 puan: Cevap kısmen doğru ancak bariz hatalar var
- 1 puan: Cevap çoğunlukla yanlış
- 0 puan: Cevap tamamen yanlış

### 3. Metin İlgisi (%25)
- 5 puan: Soru ve cevap orijinal metinle yüksek oranda ilgili
- 4 puan: Soru ve cevap metinle güçlü ilgiye sahip
- 3 puan: Soru ve cevap metinle ilgili
- 2 puan: Soru ve cevap metinle zayıf ilgiye sahip
- 1 puan: Soru ve cevap metinle çok zayıf ilgiye sahip
- 0 puan: Soru ve cevap metinle tamamen ilgisiz

### 4. Genel Tutarlılık (%15)
- 5 puan: Mükemmel mantıksal döngü, model eğitimi için tamamen uygun
- 4 puan: Genel tutarlılık iyi
- 3 puan: Temel olarak tutarlı
- 2 puan: Belirli tutarsızlık mevcut
- 1 puan: Birçok tutarsızlık sorunu var
- 0 puan: Ciddi tutarsızlık

## Orijinal Metin Parçası İçeriği:
{{chunkContent}}

## Soru:
{{question}}

## Cevap:
{{answer}}

## Çıktı Gereksinimleri:
```json
{
  "score": 4.5,
  "evaluation": "Değerlendirme açıklaması..."
}
```
"""



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


def get_data_clean_prompt(
    language: str,
    text: str,
    custom_prompt: Optional[str] = None
) -> str:
    """
    Generate data cleaning prompt for text normalization.
    
    This function creates a prompt for cleaning and normalizing text data by:
    1. Removing noise (meaningless symbols, garbled text, duplicates)
    2. Standardizing format (encoding, punctuation)
    3. Optimizing content (fixing typos, grammar errors)
    4. Organizing structure (paragraph optimization)
    5. Preserving original meaning
    
    Args:
        language: Language code ('en', 'zh', 'tr')
        text: Text to be cleaned
        custom_prompt: Optional custom prompt template to use instead of default
        
    Returns:
        Complete prompt ready for LLM
    """
    # Select base prompt template
    if custom_prompt:
        base_prompt = custom_prompt
    else:
        if language == 'en':
            base_prompt = DATA_CLEAN_PROMPT_EN
        elif language == 'tr':
            base_prompt = DATA_CLEAN_PROMPT_TR
        else:
            base_prompt = DATA_CLEAN_PROMPT_ZH
    
    # Prepare variables for substitution
    variables = {
        'textLength': len(text),
        'text': text
    }
    
    # Substitute all variables
    return substitute_variables(base_prompt, variables)


def get_dataset_evaluation_prompt(
    language: str,
    chunk_content: str,
    question: str,
    answer: str,
    custom_prompt: Optional[str] = None
) -> str:
    """
    Generate dataset quality evaluation prompt.
    
    This function creates a prompt for evaluating Q&A dataset quality across:
    1. Question Quality (25%): Clarity, grammar, difficulty
    2. Answer Quality (35%): Accuracy, completeness, logic
    3. Text Relevance (25%): How well Q&A relates to source text
    4. Overall Consistency (15%): Logical coherence of Q&A pair
    
    The evaluation supports both:
    - Regular datasets (with original text chunks)
    - Distilled datasets (without original text reference)
    
    Args:
        language: Language code ('en', 'zh', 'tr')
        chunk_content: Original text chunk (can be empty for distilled datasets)
        question: Question to evaluate
        answer: Answer to evaluate
        custom_prompt: Optional custom prompt template to use instead of default
        
    Returns:
        Complete prompt ready for LLM
    """
    # Select base prompt template
    if custom_prompt:
        base_prompt = custom_prompt
    else:
        if language == 'en':
            base_prompt = DATASET_EVALUATION_PROMPT_EN
        elif language == 'tr':
            base_prompt = DATASET_EVALUATION_PROMPT_TR
        else:
            base_prompt = DATASET_EVALUATION_PROMPT_ZH
    
    # Prepare variables for substitution
    variables = {
        'chunkContent': chunk_content or 'Distilled Content',
        'question': question,
        'answer': answer
    }
    
    # Substitute all variables
    return substitute_variables(base_prompt, variables)


__all__ = [
    'DATA_CLEAN_PROMPT_ZH',
    'DATA_CLEAN_PROMPT_EN',
    'DATA_CLEAN_PROMPT_TR',
    'DATASET_EVALUATION_PROMPT_ZH',
    'DATASET_EVALUATION_PROMPT_EN',
    'DATASET_EVALUATION_PROMPT_TR',
    'substitute_variables',
    'get_data_clean_prompt',
    'get_dataset_evaluation_prompt'
]
