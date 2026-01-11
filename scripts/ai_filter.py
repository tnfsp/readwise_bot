"""
AI 篩選模組 - 使用 Claude 進行文章篩選與摘要
"""
import json
from typing import List, Dict, Optional
import anthropic
from config import ANTHROPIC_API_KEY, USER_INTERESTS, DOMAINS


def get_client():
    """取得 Anthropic 客戶端"""
    return anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


def classify_domain(title: str, summary: str, source: str) -> str:
    """
    根據標題和摘要簡單分類領域

    Args:
        title: 文章標題
        summary: 文章摘要
        source: 來源名稱

    Returns:
        領域名稱
    """
    text = f"{title} {summary} {source}".lower()

    for domain, keywords in DOMAINS.items():
        for keyword in keywords:
            if keyword.lower() in text:
                return domain

    return "其他"


def filter_and_summarize_batch(articles: List[Dict], max_articles: int = 10) -> List[Dict]:
    """
    批量篩選與摘要文章

    Args:
        articles: 原始文章列表
        max_articles: 最多返回幾篇

    Returns:
        篩選後的文章列表，包含 AI 生成的摘要
    """
    if not articles:
        return []

    client = get_client()

    # 準備文章資訊
    articles_text = []
    for i, article in enumerate(articles[:30]):  # 最多處理 30 篇
        title = article.get("title", "")
        summary = article.get("summary", "")[:200] if article.get("summary") else ""
        source = article.get("site_name", "") or article.get("source", "")

        articles_text.append(f"""
文章 {i+1}:
- 標題: {title}
- 來源: {source}
- 摘要: {summary}
""")

    prompt = f"""你是一個資訊篩選助手。請根據用戶的關注領域，評估以下文章的重要性。

{USER_INTERESTS}

以下是今日的文章列表：

{"".join(articles_text)}

請完成以下任務：
1. 為每篇文章評分 (1-5)：5=必讀，4=值得看，3=可看可不看，2=可略過，1=不相關
2. 為評分 >= 4 的文章產生一句話中文摘要（15-25字）
3. 分類每篇文章的領域（醫學/AI/國際/知識/生產力/生活/其他）

請用 JSON 格式回覆，格式如下：
```json
{{
  "results": [
    {{"index": 1, "importance": 5, "domain": "醫學", "summary": "一句話摘要"}},
    {{"index": 2, "importance": 3, "domain": "AI", "summary": null}},
    ...
  ]
}}
```

只回覆 JSON，不要其他說明。"""

    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = message.content[0].text

        # 解析 JSON
        # 找到 JSON 部分
        if "```json" in response_text:
            json_str = response_text.split("```json")[1].split("```")[0]
        elif "```" in response_text:
            json_str = response_text.split("```")[1].split("```")[0]
        else:
            json_str = response_text

        data = json.loads(json_str.strip())
        results = data.get("results", [])

        # 合併結果
        filtered = []
        for result in results:
            idx = result.get("index", 0) - 1
            if idx < 0 or idx >= len(articles):
                continue

            importance = result.get("importance", 1)
            if importance >= 4:
                article = articles[idx].copy()
                article["importance"] = importance
                article["domain"] = result.get("domain", "其他")
                article["ai_summary"] = result.get("summary", "")
                filtered.append(article)

        # 按重要性排序，取前 N 篇
        filtered.sort(key=lambda x: x.get("importance", 0), reverse=True)
        return filtered[:max_articles]

    except Exception as e:
        print(f"AI filter error: {e}")
        # 降級處理：使用簡單規則篩選
        return simple_filter(articles, max_articles)


def simple_filter(articles: List[Dict], max_articles: int = 10) -> List[Dict]:
    """
    簡單規則篩選（當 AI 不可用時的降級方案）

    Args:
        articles: 原始文章列表
        max_articles: 最多返回幾篇

    Returns:
        篩選後的文章列表
    """
    filtered = []

    for article in articles:
        title = article.get("title", "")
        summary = article.get("summary", "")
        source = article.get("site_name", "") or article.get("source", "")

        # 簡單分類
        domain = classify_domain(title, summary, source)

        # 優先領域
        priority_domains = ["醫學", "AI", "國際"]
        importance = 4 if domain in priority_domains else 3

        article_copy = article.copy()
        article_copy["domain"] = domain
        article_copy["importance"] = importance
        article_copy["ai_summary"] = ""

        filtered.append(article_copy)

    # 優先領域排前面
    filtered.sort(key=lambda x: (
        -x.get("importance", 0),
        x.get("domain") not in ["醫學", "AI", "國際"]
    ))

    return filtered[:max_articles]


# ============================================================
# Quick Capture 功能 - AI 輔助
# ============================================================

def generate_title(content: str, max_length: int = 30) -> str:
    """
    使用 AI 生成標題

    Args:
        content: 內容文字
        max_length: 標題最大長度

    Returns:
        生成的標題
    """
    if not content or len(content.strip()) < 10:
        return "TG 筆記"

    client = get_client()

    prompt = f"""根據以下內容生成一個簡潔的中文標題（{max_length}字以內）：

規則：
- 如果是觀點/分析，標題應反映核心論點
- 如果是隨手記/感想，標題應反映主題
- 不要使用引號
- 直接返回標題文字，不要其他說明

內容：
{content[:500]}"""

    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=100,
            messages=[{"role": "user", "content": prompt}]
        )

        title = message.content[0].text.strip()
        # 清理可能的引號
        title = title.strip('"\'')
        # 限制長度
        if len(title) > max_length:
            title = title[:max_length-1] + "..."

        return title

    except Exception as e:
        print(f"AI title generation error: {e}")
        # 降級：使用內容開頭
        return content[:20].replace("\n", " ") + "..."


def detect_domain(content: str) -> str:
    """
    使用 AI 判斷內容領域

    Args:
        content: 內容文字

    Returns:
        領域名稱
    """
    if not content:
        return "其他"

    # 先用簡單規則判斷
    text = content.lower()
    for domain, keywords in DOMAINS.items():
        for keyword in keywords:
            if keyword.lower() in text:
                return domain

    # 如果簡單規則無法判斷，使用 AI
    client = get_client()

    prompt = f"""判斷以下內容屬於哪個領域，只回覆領域名稱：
- 醫學
- AI
- 國際
- 知識
- 生產力
- 生活
- 其他

內容：
{content[:300]}

領域："""

    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=20,
            messages=[{"role": "user", "content": prompt}]
        )

        domain = message.content[0].text.strip()

        # 驗證返回值
        valid_domains = ["醫學", "AI", "國際", "知識", "生產力", "生活", "其他"]
        if domain in valid_domains:
            return domain
        else:
            return "其他"

    except Exception as e:
        print(f"AI domain detection error: {e}")
        return "其他"


def process_capture_content(content: str, is_forward: bool = False) -> Dict:
    """
    處理 Quick Capture 的內容（生成標題 + 判斷領域）

    Args:
        content: 內容文字
        is_forward: 是否為轉發內容

    Returns:
        包含 title 和 domain 的字典
    """
    title = generate_title(content)
    domain = detect_domain(content)

    # 領域對應的 Tag
    domain_tags = {
        "醫學": "@醫學",
        "AI": "@AI",
        "國際": "@國際",
        "知識": "@知識",
        "生產力": "@生產力",
        "生活": "@生活",
        "其他": "@其他"
    }

    return {
        "title": title,
        "domain": domain,
        "domain_tag": domain_tags.get(domain, "@其他")
    }


if __name__ == "__main__":
    # 測試
    test_articles = [
        {"title": "New ECMO guidelines for cardiac surgery", "summary": "Updated recommendations...", "site_name": "NEJM"},
        {"title": "Claude 3.5 Sonnet released", "summary": "Anthropic announces...", "site_name": "TechCrunch"},
        {"title": "Best coffee makers 2024", "summary": "Our top picks...", "site_name": "Wirecutter"},
    ]

    print("Testing AI filter...")
    results = filter_and_summarize_batch(test_articles)
    print(f"Filtered to {len(results)} articles")
    for r in results:
        print(f"  - [{r.get('domain')}] {r.get('title')[:40]}")

    # 測試 Quick Capture 功能
    print("\n" + "="*50)
    print("Testing Quick Capture AI functions...")

    test_content = "今天看了一百公尺這部電影，我覺得挺有趣的，很青春"
    result = process_capture_content(test_content)
    print(f"Content: {test_content}")
    print(f"Generated title: {result['title']}")
    print(f"Detected domain: {result['domain']}")
