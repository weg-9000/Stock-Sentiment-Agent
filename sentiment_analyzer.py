"""
1️⃣ 경량 모델 → 2️⃣ HyperCLOVA X 의 두 단계 감정 분석
"""
from transformers import pipeline
from hyperclova_client import HyperClovaX
from typing import List

_light = pipeline("sentiment-analysis",
                  model="klue/roberta-base-sentiment", device=-1)
_clova = HyperClovaX()

def quick_sentiment(text: str) -> dict:
    try:
        res = _light(text)[0]
        return {"label": res["label"].lower(), "score": res["score"]}
    except Exception:
        return {"label": "neutral", "score": .5}

async def clova_sentiment(texts: List[str], meta: dict) -> dict:
    prompt = "\n".join(texts[:10])
    system = "You are a financial sentiment analysis model."
    functions = [{
        "name": "return_sentiment",
        "parameters": {
            "type": "object",
            "properties": {
              "sentiment_score": {"type": "number"},
              "sentiment_label": {"type": "string"},
              "confidence": {"type": "number"},
              "key_factors": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["sentiment_score","sentiment_label","confidence"]
        }
    }]
    result = await _clova.chat(system, prompt, functions)
    # TODO: 함수 출력 parse
    return result
