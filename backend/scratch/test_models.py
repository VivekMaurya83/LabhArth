import os
from dotenv import load_dotenv
from google.genai import Client

load_dotenv()

raw_keys = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEYS") or ""
keys = [k.strip() for k in raw_keys.split(",") if k.strip()]

models_to_test = [
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-2.0-flash",
    "gemini-3.1-flash-lite"
]

print(f"Testing {len(keys)} keys against {len(models_to_test)} models...\n")

for idx, key in enumerate(keys):
    print(f"Key {idx + 1}/{len(keys)} ({key[:10]}...):")
    client = Client(api_key=key)
    any_success = False
    for model in models_to_test:
        try:
            client.models.generate_content(
                model=model,
                contents="ping"
            )
            print(f"  - {model}: VALID")
            any_success = True
        except Exception as e:
            err_msg = str(e).split("\n")[0]
            print(f"  - {model}: EXHAUSTED ({err_msg[:60]})")
    if not any_success:
        print("  - No models succeeded for this key.")
    print()
