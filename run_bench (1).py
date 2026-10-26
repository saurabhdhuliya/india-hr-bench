"""india-hr-bench runner. Standard library only.
Works with any OpenAI-compatible endpoint (Groq, OpenRouter, Gemini's OpenAI-compatible API, Ollama).
Your key stays in YOUR environment variable. Never share it.

Examples (check each provider's docs for the current base URL and model names):
  export API_KEY=...   (Windows PowerShell: $env:API_KEY="...")
  python run_bench.py --base-url https://api.groq.com/openai/v1 --model openai/gpt-oss-120b
  python run_bench.py --base-url https://openrouter.ai/api/v1 --model <a :free model>
  python run_bench.py --mock     # no network, tests the pipeline
Auto-scored: numeric, extract. Others (exact, clarify, behavior) are saved for manual review.
"""
import argparse, glob, json, os, re, time, urllib.request

SYSTEM = "You are an HR assistant in India. Answer concisely. If information is missing, ask for it instead of guessing."

def load_items(pattern="data/*.jsonl"):
    items = []
    for f in sorted(glob.glob(pattern)):
        items += [json.loads(l) for l in open(f, encoding="utf-8") if l.strip()]
    return items

def call(base_url, key, model, prompt):
    body = json.dumps({"model": model, "temperature": 0,
                       "messages": [{"role": "system", "content": SYSTEM},
                                    {"role": "user", "content": prompt}]}).encode()
    req = urllib.request.Request(base_url.rstrip("/") + "/chat/completions", body,
                                 {"Content-Type": "application/json", "Authorization": f"Bearer {key}"})
    with urllib.request.urlopen(req, timeout=240) as r:
        return json.load(r)["choices"][0]["message"]["content"]

def score(item, text):
    t = item["answer_type"]
    if t == "numeric":
        nums = re.findall(r"\d[\d,]*\.?\d*", text.replace("\u20b9", ""))
        vals = [float(n.replace(",", "")) for n in nums if n.replace(",", "").replace(".", "").isdigit()]
        return any(abs(v - item["expected"]) <= max(1, 0.001 * item["expected"]) for v in vals)
    if t == "extract":
        m = re.search(r"\{.*\}", text, re.S)
        if not m:
            return False
        try:
            got = json.loads(m.group(0))
        except Exception:
            return False
        return all(got.get(k) == v for k, v in item["expected"].items())
    return None  # manual review

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url"); ap.add_argument("--model", default="mock")
    ap.add_argument("--mock", action="store_true"); ap.add_argument("--sleep", type=float, default=2.5)
    a = ap.parse_args()
    key = os.environ.get("API_KEY", "")
    if not a.mock and not (a.base_url and key):
        raise SystemExit("Set API_KEY and pass --base-url and --model (or use --mock).")
    os.makedirs("results", exist_ok=True)
    out, tally = [], {}
    for it in load_items():
        try:
            text = "mock answer" if a.mock else None
            for attempt in range(3):
                if text is not None:
                    break
                try:
                    text = call(a.base_url, key, a.model, it["prompt"])
                except Exception as e:
                    text = None
                    err = f"ERROR: {e}"
                    time.sleep(8 * (attempt + 1))
            if text is None:
                text = err
        except Exception as e:
            text = f"ERROR: {e}"
        ok = None if text.startswith("ERROR:") else score(it, text)
        out.append({"id": it["id"], "track": it["track"], "type": it["answer_type"], "auto_correct": ok, "response": text})
        if ok is not None:
            s = tally.setdefault(it["track"], [0, 0]); s[0] += bool(ok); s[1] += 1
        if not a.mock:
            time.sleep(a.sleep)  # stay inside free-tier rate limits
    name = re.sub(r"[^\w.-]", "_", a.model)
    with open(f"results/{name}.jsonl", "w", encoding="utf-8") as f:
        for r in out:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"model={a.model}")
    for tr, (c, n) in tally.items():
        print(f"  {tr}: {c}/{n} auto-scored correct")
    errs = sum(1 for r in out if r["response"].startswith("ERROR:"))
    print(f"  {errs} items failed with errors (re-run to retry)")
    manual = sum(1 for r in out if r["auto_correct"] is None and not r["response"].startswith("ERROR:"))
    print(f"  {manual} items saved for manual review in results/{name}.jsonl")

if __name__ == "__main__":
    main()
