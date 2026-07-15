"""Drop-in memory telemetry for your tracking loop (Part C1).

Records CPU RSS and, if CUDA is available, GPU memory at three layers:
    alloc_mb    - torch.cuda.memory_allocated(): your live tensors
    reserved_mb - torch.cuda.memory_reserved(): tensors + PyTorch's cache
    gpu_used_mb - from torch.cuda.mem_get_info(): everything the driver has
                  handed out on this GPU (all processes + the CUDA context).
                  This is the number nvidia-smi shows.

Usage in your loop:

    from mem_monitor import MemoryLog

    memlog = MemoryLog()
    for frame_idx, result in enumerate(results):
        ...  # your tracking code
        memlog.sample(frame_idx)
    memlog.save_csv("memory_log.csv")
    memlog.plot("memory_plot.png")
    memlog.print_peaks()

Standalone self-test (hoards memory on purpose so the plot has a shape):

    python mem_monitor.py
"""

import csv
import time

import psutil

try:
    import torch
    CUDA = torch.cuda.is_available()
except ImportError:
    CUDA = False


class MemoryLog:
    def __init__(self):
        self.proc = psutil.Process()
        self.rows = []
        self.t0 = time.time()

    def sample(self, tag=""):
        row = {
            "t": round(time.time() - self.t0, 3),
            "tag": tag,
            "rss_mb": round(self.proc.memory_info().rss / 2**20, 1),
        }
        if CUDA:
            free_b, total_b = torch.cuda.mem_get_info()
            row["alloc_mb"] = round(torch.cuda.memory_allocated() / 2**20, 1)
            row["reserved_mb"] = round(torch.cuda.memory_reserved() / 2**20, 1)
            row["gpu_used_mb"] = round((total_b - free_b) / 2**20, 1)
        self.rows.append(row)
        return row

    def save_csv(self, path="memory_log.csv"):
        with open(path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=self.rows[0].keys())
            writer.writeheader()
            writer.writerows(self.rows)
        print(f"[memlog] wrote {len(self.rows)} samples to {path}")

    def plot(self, path="memory_plot.png"):
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        xs = [r["t"] for r in self.rows]
        fig, ax = plt.subplots(figsize=(9, 4.5))
        ax.plot(xs, [r["rss_mb"] for r in self.rows], label="CPU RSS")
        if CUDA:
            ax.plot(xs, [r["alloc_mb"] for r in self.rows], label="VRAM allocated (torch)")
            ax.plot(xs, [r["reserved_mb"] for r in self.rows], label="VRAM reserved (torch cache)")
            ax.plot(xs, [r["gpu_used_mb"] for r in self.rows], label="GPU used (driver / nvidia-smi)")
        ax.set_xlabel("seconds")
        ax.set_ylabel("MB")
        ax.set_title("Memory over time")
        ax.legend()
        fig.tight_layout()
        fig.savefig(path, dpi=120)
        print(f"[memlog] wrote {path}")

    def print_peaks(self):
        print(f"[memlog] peak CPU RSS: {max(r['rss_mb'] for r in self.rows):.0f} MB")
        if CUDA:
            peak = torch.cuda.max_memory_allocated() / 2**20
            print(f"[memlog] peak VRAM allocated (torch): {peak:.0f} MB")


if __name__ == "__main__":
    import numpy as np

    memlog = MemoryLog()
    hoard = []
    for i in range(30):
        hoard.append(np.ones((64, 1024, 1024), dtype=np.uint8))     # +64 MB RAM
        if CUDA and i % 3 == 0:
            hoard.append(torch.ones(16 * 2**20, device="cuda"))     # +64 MB VRAM
        memlog.sample(tag=i)
        time.sleep(0.05)

    memlog.save_csv()
    memlog.plot()
    memlog.print_peaks()
