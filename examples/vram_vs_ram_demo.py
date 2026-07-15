"""Guided tour for Part C3: how CPU RAM and GPU VRAM behave differently.

Run:
    python vram_vs_ram_demo.py            # pauses between acts
    python vram_vs_ram_demo.py --fast     # no pauses (for quick checks)

Runs without a GPU too (the GPU acts are skipped with a note).

While it runs, watch from the outside in two other terminals:
    ./watch_mem.sh <pid>        # the CPU side (PID is printed at startup)
    watch -n 0.5 nvidia-smi     # the GPU side

ACT 1  CPU RAM is virtual: asking for memory is not the same as using it.
ACT 2  VRAM is physical and layered: allocated vs reserved vs driver.
ACT 3  Freeing is not freeing: the caching allocator and empty_cache().
ACT 4  Hard OOM vs soft RAM: the GPU says no, the CPU says "sure, on paper".
"""

import os
import sys

import numpy as np
import psutil

try:
    import torch
    CUDA = torch.cuda.is_available()
except ImportError:
    torch = None
    CUDA = False

PROC = psutil.Process()
FAST = "--fast" in sys.argv


def rss_mb():
    return PROC.memory_info().rss / 2**20


def gpu_mb():
    """(allocated, reserved, driver_used) in MB."""
    free_b, total_b = torch.cuda.mem_get_info()
    return (torch.cuda.memory_allocated() / 2**20,
            torch.cuda.memory_reserved() / 2**20,
            (total_b - free_b) / 2**20)


def pause(msg):
    if not FAST:
        input(f"\n[paused] {msg} — press Enter to continue...")


def act1_cpu_virtual():
    print("\n=== ACT 1: CPU RAM is virtual ===")
    print(f"baseline RSS: {rss_mb():.0f} MB")

    big = np.zeros(2 * 2**30, dtype=np.uint8)  # ask the OS for 2 GB
    print(f"after np.zeros(2 GB):        RSS {rss_mb():.0f} MB   <- barely moved!")
    print("  The OS granted 2 GB of VIRTUAL address space, but physical pages")
    print("  are only assigned when you actually touch them (demand paging).")

    big[::4096] = 1  # write to every 4 KB page once
    print(f"after touching every page:   RSS {rss_mb():.0f} MB   <- NOW it's real")
    print("  And if RAM ran short, the OS could quietly swap these pages to")
    print("  disk and page them back on access. Slow, but nothing crashes.")

    del big
    print(f"after del:                   RSS {rss_mb():.0f} MB")
    pause("check watch_mem.sh — you just saw virtual vs resident")


def act2_vram_layers():
    print("\n=== ACT 2: VRAM is physical and layered ===")
    a0, r0, d0 = gpu_mb()
    print(f"baseline: allocated {a0:.0f} | reserved {r0:.0f} | driver-used {d0:.0f} MB")
    print("  (driver-used includes every process on this GPU plus this")
    print("   process's CUDA context — that context alone costs 100s of MB)")

    tensors = [torch.zeros(512 * 2**20 // 4, device="cuda") for _ in range(2)]  # 2 x 512 MB
    a, r, d = gpu_mb()
    print(f"after 2 x 512 MB tensors: allocated {a:.0f} | reserved {r:.0f} | driver-used {d:.0f} MB")
    print("  All three jumped ~1 GB IMMEDIATELY. No lazy paging here: CUDA")
    print("  memory is pinned physical VRAM from the moment you ask.")
    pause("compare these numbers with nvidia-smi")
    return tensors


def act3_empty_cache(tensors):
    print("\n=== ACT 3: freeing is not freeing ===")
    tensors.clear()
    del tensors
    a, r, d = gpu_mb()
    print(f"after del:           allocated {a:.0f} | reserved {r:.0f} | driver-used {d:.0f} MB")
    print("  allocated dropped ~1 GB, but reserved did NOT: PyTorch's caching")
    print("  allocator keeps the blocks to reuse them without asking the")
    print("  driver again. nvidia-smi still shows them as used.")
    pause("verify with nvidia-smi: the ~1 GB still looks used")

    torch.cuda.empty_cache()
    a, r, d = gpu_mb()
    print(f"after empty_cache(): allocated {a:.0f} | reserved {r:.0f} | driver-used {d:.0f} MB")
    print("  Only now did the memory go back to the driver. This is the")
    print("  explicit step the OS does implicitly for CPU RAM. Note: the")
    print("  cache exists because cudaMalloc/cudaFree are SLOW — emptying it")
    print("  every frame would make your tracker crawl.")
    pause("verify with nvidia-smi: now it's actually free")


def act4_hard_vs_soft():
    print("\n=== ACT 4: hard OOM vs soft RAM ===")
    total_mb = torch.cuda.mem_get_info()[1] / 2**20
    ask_mb = int(total_mb * 1.25)
    print(f"this GPU has {total_mb:.0f} MB total; asking it for {ask_mb} MB...")
    try:
        torch.empty(ask_mb * 2**20, dtype=torch.uint8, device="cuda")
        print("  ...somehow succeeded?! (are you on a unified-memory system?)")
    except torch.cuda.OutOfMemoryError:
        print("  -> torch.cuda.OutOfMemoryError, as promised. No paging, no")
        print("     mercy. But we CAUGHT it — the process lives, and after an")
        print("     empty_cache() we could retry smaller or fall back to CPU.")
        torch.cuda.empty_cache()

    print(f"\nnow asking the CPU for the same {ask_mb} MB with np.zeros...")
    big = np.zeros(ask_mb * 2**20, dtype=np.uint8)
    print(f"  -> 'succeeded' instantly. RSS is only {rss_mb():.0f} MB — the pages")
    print("     exist on paper until touched (ACT 1). The CPU can promise more")
    print("     than it has because swap is its safety net. The GPU can't.")
    del big
    print("\n(If your OS refused that np.zeros: it has strict overcommit")
    print(" settings — lower the size; the point stands.)")


def main():
    print(f"[demo] PID {os.getpid()} — watch me with: ./watch_mem.sh {os.getpid()}")
    act1_cpu_virtual()
    if CUDA:
        tensors = act2_vram_layers()
        act3_empty_cache(tensors)
        act4_hard_vs_soft()
    else:
        print("\n[no CUDA] Acts 2-4 need an NVIDIA GPU — run them on Google")
        print("Colab (free T4). Acts 2-4 are exactly what C3 asks you to")
        print("reproduce and screenshot there.")
    print("\nDone. Now answer the C4 questions — you just watched every answer.")


if __name__ == "__main__":
    main()
