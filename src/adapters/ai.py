"""AI adapters. BudgetBot uses direct InvokeModel — no KB / no RAG.

Interface:
    categorize(description, amount, date) -> {"category": str, "confidence": "high|medium|low"}
"""
import json
import re
from typing import Any


CATEGORIES = [
    "Food", "Transport", "Shopping", "Utilities", "Entertainment",
    "Health", "Subscriptions", "Income", "Transfer", "Other",
]


CATEGORIZE_PROMPT = """Categorize the following bank transaction into exactly one category.
Categories: {categories}

Transaction: "{description}"
Amount: {amount}
Date: {date}

Respond with JSON only. No explanation.
{{"category": "<category>", "confidence": "high|medium|low"}}"""


BATCH_CATEGORIZE_PROMPT = """Categorize each bank transaction into exactly one category.
Categories: {categories}

Transactions JSON:
{transactions}

Respond with JSON only. No explanation.
{{"items":[{{"row_id":"<same row_id>","category":"<category>","confidence":"high|medium|low"}}]}}"""


def _parse_json_response(text: str) -> dict:
    """Extract first JSON object from LLM response. Falls back to Other if invalid."""
    text = text.strip()
    # Strip markdown code fences if present
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\n?|```$", "", text, flags=re.MULTILINE).strip()
    match = re.search(r"\{[^}]+\}", text, re.DOTALL)
    if match:
        try:
            obj = json.loads(match.group())
            if obj.get("category") in CATEGORIES:
                return {
                    "category": obj["category"],
                    "confidence": obj.get("confidence", "medium"),
                }
        except json.JSONDecodeError:
            pass
    return {"category": "Other", "confidence": "low"}


def _extract_json(text: str) -> Any:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\n?|```$", "", text, flags=re.MULTILINE).strip()
    match = re.search(r"(\{.*\}|\[.*\])", text, re.DOTALL)
    if not match:
        return {}
    try:
        return json.loads(match.group())
    except json.JSONDecodeError:
        return {}


class BedrockAI:
    def __init__(self, region: str, model_id: str):
        import boto3
        self.runtime = boto3.client("bedrock-runtime", region_name=region)
        self.model_id = model_id

    def _invoke_text(self, prompt: str) -> str:
        if "nova" in self.model_id:
            body = {
                "schemaVersion": "messages-v1",
                "messages": [{"role": "user", "content": [{"text": prompt}]}],
                "inferenceConfig": {"maxTokens": 2500, "temperature": 0.0},
            }
        else:
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 2500,
                "temperature": 0.0,
                "messages": [{"role": "user", "content": [{"type": "text", "text": prompt}]}],
            }
        resp = self.runtime.invoke_model(
            modelId=self.model_id,
            body=json.dumps(body),
            contentType="application/json",
            accept="application/json",
        )
        payload = json.loads(resp["body"].read())
        if "nova" in self.model_id:
            return payload["output"]["message"]["content"][0]["text"]
        return payload["content"][0]["text"]

    def categorize(self, description: str, amount: float, date: str) -> dict:
        prompt = CATEGORIZE_PROMPT.format(
            categories=", ".join(CATEGORIES),
            description=description,
            amount=amount,
            date=date,
        )
        text = self._invoke_text(prompt)
        return _parse_json_response(text)

    def categorize_many(self, rows: list[dict]) -> list[dict]:
        if not rows:
            return []
        by_id = self._categorize_batch(rows)

        missing = [row for row in rows if str(row.get("row_id")) not in by_id]
        for i in range(0, len(missing), 20):
            by_id.update(self._categorize_batch(missing[i:i + 20]))

        local_fallback = LocalAI()
        return [
            by_id.get(
                str(row.get("row_id")),
                local_fallback.categorize(
                    description=row["description"],
                    amount=row["amount"],
                    date=row["date"],
                ),
            )
            for row in rows
        ]

    def _categorize_batch(self, rows: list[dict]) -> dict[str, dict]:
        prompt = BATCH_CATEGORIZE_PROMPT.format(
            categories=", ".join(CATEGORIES),
            transactions=json.dumps(rows, ensure_ascii=False),
        )
        payload = _extract_json(self._invoke_text(prompt))
        by_id: dict[str, dict] = {}
        items = payload if isinstance(payload, list) else payload.get("items", [])
        for item in items:
            if not isinstance(item, dict):
                continue
            category = item.get("category")
            if category not in CATEGORIES:
                category = "Other"
            by_id[str(item.get("row_id"))] = {
                "category": category,
                "confidence": item.get("confidence", "medium"),
            }
        return by_id


class LocalAI:
    """Rule-based categorizer. Keyword matching only. Use for development."""

    # Order matters: first match wins. Subscriptions BEFORE Entertainment so
    # "Netflix monthly subscription" → Subscriptions (subscription keyword fires).
    KEYWORDS = {
        "Income": ["salary", "deposit credit", "payroll", "incoming transfer"],
        "Transfer": ["transfer to", "transfer from", "moved to savings"],
        "Subscriptions": ["subscription", "netflix", "spotify", "openai", "chatgpt", "anthropic",
                          "claude", "github", "icloud", "google one"],
        "Food": ["restaurant", "cafe", "coffee", "starbucks", "highlands", "phở", "pho", "food",
                 "grab food", "shopee food", "lunch", "dinner", "bakery"],
        "Transport": ["grab", "uber", " be ", "xanh sm", "taxi", "metro", "bus", "petrol", "shell",
                      "vinfast", "fuel"],
        "Shopping": ["shopee", "lazada", "tiki", "amazon", "store", "mall", "vincom", "shop"],
        "Utilities": ["electric", "evn", "water", "internet", "viettel", "vnpt", "fpt", "utility"],
        "Entertainment": ["cinema", "cgv", "lotte cinema", "concert", "game"],
        "Health": ["pharmacy", "hospital", "clinic", "guardian", "long chau", "medlatec"],
    }

    def categorize(self, description: str, amount: float, date: str) -> dict:
        desc_lower = description.lower()
        for category, keywords in self.KEYWORDS.items():
            for kw in keywords:
                if kw in desc_lower:
                    return {"category": category, "confidence": "medium"}
        # Positive amount → income heuristic
        try:
            if float(amount) > 0:
                return {"category": "Income", "confidence": "low"}
        except (TypeError, ValueError):
            pass
        return {"category": "Other", "confidence": "low"}

    def categorize_many(self, rows: list[dict]) -> list[dict]:
        return [
            self.categorize(
                description=row["description"],
                amount=row["amount"],
                date=row["date"],
            )
            for row in rows
        ]
