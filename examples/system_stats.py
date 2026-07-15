"""CPU RAM + GPU VRAM stats — starter for the Resource monitoring requirement.

get_stats() returns exactly the JSON shape the assignment asks your /stats
endpoint to serve. Wire it into your backend (Flask example):

    from system_stats import get_stats

    @app.route("/stats")
    def stats():
        return jsonify(get_stats())

Note the three scopes, because they answer different questions:

  * process_rss_mb - memory of THIS python process only. If your LLM runs
    in a separate process (`ollama serve` does!), the model will NOT show
    up here, no matter how big it is.
  * ram_used_mb    - the whole machine. CPU-loaded models show up here.
  * gpus[...]      - whole-GPU numbers straight from the driver, so they
    include EVERY process using the GPU (ollama, your browser, games...).

Needs: pip install psutil
The GPU part shells out to nvidia-smi and returns [] if it isn't there,
so this file works unchanged on CPU-only machines and Macs.

Run standalone:
    python system_stats.py            # one JSON snapshot
    python system_stats.py --watch    # refresh every second, Ctrl-C to stop
"""

import json
import shutil
import subprocess
import sys
import time

import psutil


def gpu_stats():
    """Per-GPU memory dicts from nvidia-smi; [] if no NVIDIA GPU/driver."""
    if shutil.which("nvidia-smi") is None:
        return []
    try:
        out = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,memory.used,memory.total",
             "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=5, check=True,
        ).stdout
    except (subprocess.SubprocessError, OSError):
        return []
    gpus = []
    for line in out.strip().splitlines():
        name, used, total = [field.strip() for field in line.split(",")]
        gpus.append({"name": name,
                     "vram_used_mb": int(used),
                     "vram_total_mb": int(total)})
    return gpus


def get_stats():
    ram = psutil.virtual_memory()
    return {
        "process_rss_mb": round(psutil.Process().memory_info().rss / 2**20),
        "ram_used_mb": round((ram.total - ram.available) / 2**20),
        "ram_total_mb": round(ram.total / 2**20),
        "gpus": gpu_stats(),
    }


if __name__ == "__main__":
    if "--watch" in sys.argv:
        while True:
            s = get_stats()
            gpu_txt = " | ".join(
                f"{g['name']}: {g['vram_used_mb']}/{g['vram_total_mb']} MB"
                for g in s["gpus"]) or "no NVIDIA GPU"
            print(f"RAM {s['ram_used_mb']}/{s['ram_total_mb']} MB "
                  f"(this process: {s['process_rss_mb']} MB) | {gpu_txt}",
                  flush=True)
            time.sleep(1)
    else:
        print(json.dumps(get_stats(), indent=2))
