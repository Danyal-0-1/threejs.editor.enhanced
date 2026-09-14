"""Download model weights for the tokenizer_avoided experiment.

Downloads are recorded with wall-clock duration and resolved revision so that
`dependency/model download time` is a MEASURED number, not an estimate.
Failures are recorded, never swallowed: a model that does not download is
BLOCKED with its exact exception, and the script continues to the next one.
"""
import json, os, sys, time, traceback

MODELS = [
    ("Qwen/Qwen2.5-Coder-7B", "base"),
    ("Qwen/Qwen2.5-Coder-7B-Instruct", "instruct"),
]

def main():
    from huggingface_hub import snapshot_download, model_info
    out = []
    for repo, kind in MODELS:
        rec = {"repo": repo, "kind": kind, "status": "PENDING"}
        t0 = time.time()
        try:
            rec["revision"] = model_info(repo).sha
        except Exception as exc:
            rec["revision"] = "unresolved"
            rec["revision_error"] = f"{type(exc).__name__}: {exc}"[:200]
        try:
            path = snapshot_download(
                repo, allow_patterns=["*.json", "*.safetensors", "*.txt", "*.py",
                                      "merges.txt", "vocab.json", "tokenizer*"])
            rec["local_path"] = path
            size = sum(os.path.getsize(os.path.join(dp, f))
                       for dp, _, fs in os.walk(path) for f in fs
                       if os.path.exists(os.path.join(dp, f)))
            rec["bytes_on_disk"] = size
            rec["status"] = "VERIFIED"
        except Exception as exc:
            rec["status"] = "FAILED"
            rec["error"] = f"{type(exc).__name__}: {exc}"[:500]
            rec["traceback"] = traceback.format_exc()[-1500:]
        rec["download_seconds"] = round(time.time() - t0, 3)
        out.append(rec)
        print(json.dumps({k: v for k, v in rec.items() if k != "traceback"}), flush=True)
    dest = sys.argv[1]
    with open(dest, "w") as fh:
        json.dump(out, fh, indent=2)
    n_ok = sum(1 for r in out if r["status"] == "VERIFIED")
    print(f"DONE {n_ok}/{len(out)} downloaded", flush=True)
    return 0 if n_ok else 3

if __name__ == "__main__":
    raise SystemExit(main())
