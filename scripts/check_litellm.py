import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from config import LITELLM_API_KEY, LITELLM_MODEL, LITELLM_BASE_URL
from llm_extractor import LLMEntityExtractor


def main():
    extractor = LLMEntityExtractor(
        provider="litellm",
        api_key=LITELLM_API_KEY,
        model=LITELLM_MODEL,
        base_url=LITELLM_BASE_URL,
        temperature=0.1,
        use_job=False,
    )

    status = {"client_initialized": bool(extractor.client)}

    if not extractor.client:
        print(json.dumps(status))
        return

    response = extractor._query_litellm('Return JSON {"status": "ok"}.')
    status["sample_response"] = response
    print(json.dumps(status))


if __name__ == "__main__":
    main()
