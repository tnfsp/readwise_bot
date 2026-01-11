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
