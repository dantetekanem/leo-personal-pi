#!/usr/bin/env python3
"""Measure a screen recording: motion energy, progress-to-final curve, loop period, contact sheet.

usage: motion.py VIDEO NAME [--crop W:H:X:Y] [--fps 30] [--from S] [--to S] [--sheet N] [--tile 5x4] [--width 360]
                 [--threshold 0.6] [--flashes]

--flashes approximates WCAG 2.3.1 on whole-frame mean luma: it counts pairs of opposing jumps of 10% or more and
reports the worst one-second window. Use it as a screen, not as a compliance proof.
"""
import argparse
import os
import shutil
import subprocess
import sys
import tempfile

SW, SH = 160, 112


def run(cmd, capture=True):
    return subprocess.run(cmd, check=True, stdout=subprocess.PIPE if capture else None, stderr=subprocess.DEVNULL).stdout


def vf_chain(args, extra):
    parts = [f"fps={args.fps}"]
    if args.crop:
        parts.append(f"crop={args.crop}")
    parts.extend(extra)
    return ",".join(parts)


def trim(args):
    out = []
    if args.start:
        out += ["-ss", str(args.start)]
    if args.end:
        out += ["-to", str(args.end)]
    return out


def gray_frames(args):
    raw = run(["ffmpeg", "-v", "error", "-i", args.video, *trim(args), "-vf",
               vf_chain(args, [f"scale={SW}:{SH}", "format=gray"]), "-f", "rawvideo", "-"])
    n = len(raw) // (SW * SH)
    return [raw[i * SW * SH:(i + 1) * SW * SH] for i in range(n)]


def mad(a, b):
    return sum(abs(x - y) for x, y in zip(a, b)) / len(a)


def bar(v, vmax, width=40):
    k = 0 if vmax <= 0 else int(round(width * v / vmax))
    return "#" * k


def main():
    p = argparse.ArgumentParser()
    p.add_argument("video")
    p.add_argument("name")
    p.add_argument("--crop")
    p.add_argument("--fps", type=float, default=30)
    p.add_argument("--from", dest="start", type=float)
    p.add_argument("--to", dest="end", type=float)
    p.add_argument("--sheet", type=int, default=20)
    p.add_argument("--tile", default="5x4")
    p.add_argument("--width", type=int, default=360)
    p.add_argument("--threshold", type=float, default=0.6)
    p.add_argument("--flashes", action="store_true")
    args = p.parse_args()

    frames = gray_frames(args)
    if len(frames) < 3:
        sys.exit("too few frames")
    dt = 1000.0 / args.fps
    offset = (args.start or 0) * 1000
    energy = [0.0] + [mad(frames[i], frames[i - 1]) for i in range(1, len(frames))]
    final = frames[-1]
    d0 = mad(frames[0], final) or 1e-9
    progress = [1 - mad(f, final) / d0 for f in frames]
    to_first = [mad(f, frames[0]) for f in frames]

    active = [i for i, e in enumerate(energy) if e > args.threshold]
    print(f"# {args.name}: {len(frames)} frames @ {args.fps}fps = {len(frames) * dt:.0f} ms (offset {offset:.0f} ms)")
    if active:
        print(f"motion window: {offset + active[0] * dt:.0f} -> {offset + active[-1] * dt:.0f} ms"
              f" ({(active[-1] - active[0]) * dt:.0f} ms), peak energy {max(energy):.2f}")
        segs, start, prev = [], active[0], active[0]
        for i in active[1:]:
            if i - prev > max(2, int(150 / dt)):
                segs.append((start, prev))
                start = i
            prev = i
        segs.append((start, prev))
        print("segments (ms): " + ", ".join(f"{offset + a * dt:.0f}-{offset + b * dt:.0f}" for a, b in segs))
    else:
        print("no motion above threshold")

    if active and d0 > 1.0:
        a, b = active[0], active[-1]
        span = max(1, b - a)
        marks = []
        for q in (0.1, 0.25, 0.5, 0.75, 0.9):
            hit = next((i for i in range(a, len(progress)) if progress[i] >= q), None)
            marks.append("n/a" if hit is None else f"{(hit - a) / span:.2f}")
        over = max(progress[a:]) - 1
        print("progress-to-final reached at fraction of window  10%/25%/50%/75%/90% = " + " / ".join(marks)
              + (f"  overshoot {over * 100:.0f}%" if over > 0.05 else ""))

    if args.flashes:
        luma = [sum(f) / (len(f) * 255.0) for f in frames]
        jumps = [(i, 1 if luma[i] > luma[i - 1] else -1) for i in range(1, len(luma)) if abs(luma[i] - luma[i - 1]) >= 0.10]
        flashes, last = [], None
        for i, sign in jumps:
            if last is not None and sign != last[1]:
                flashes.append(i)
                last = None
            else:
                last = (i, sign)
        window = int(round(args.fps))
        worst = max((sum(1 for j in flashes if s <= j < s + window) for s in range(len(frames))), default=0)
        print(f"flashes: {len(flashes)} total at ms {[round(offset + j * dt) for j in flashes]}; worst 1 s window: {worst}"
              + ("  OVER WCAG 2.3.1 LIMIT" if worst > 3 else ""))

    if len(frames) > args.fps:
        lo = int(0.25 * args.fps)
        best = min(range(lo, len(frames)), key=lambda i: to_first[i])
        print(f"closest return to first frame: {offset + best * dt:.0f} ms (mad {to_first[best]:.2f}; loop period if small)")

    vmax = max(energy) or 1
    step = max(1, int(round(len(frames) / 60)))
    print("t_ms   energy  progress")
    for i in range(0, len(frames), step):
        print(f"{offset + i * dt:6.0f} {energy[i]:6.2f} {progress[i]:6.2f} |{bar(energy[i], vmax)}")

    outdir = os.path.join(os.path.dirname(os.path.abspath(args.video)), "sheets")
    os.makedirs(outdir, exist_ok=True)
    tmp = tempfile.mkdtemp(prefix="motion-")
    try:
        run(["ffmpeg", "-v", "error", "-i", args.video, *trim(args), "-vf",
             vf_chain(args, [f"scale={args.width}:-2"]), "-q:v", "3", os.path.join(tmp, "f%05d.jpg")])
        files = sorted(os.listdir(tmp))
        if active:
            a, b = max(0, active[0] - 2), min(len(files) - 1, active[-1] + 2)
        else:
            a, b = 0, len(files) - 1
        n = min(args.sheet, b - a + 1)
        picks = sorted({a + round(k * (b - a) / max(1, n - 1)) for k in range(n)})
        labeled = []
        for i in picks:
            src = os.path.join(tmp, files[i])
            dst = os.path.join(tmp, f"{offset + i * dt:06.0f}ms.jpg")
            shutil.copy(src, dst)
            labeled.append(dst)
        sheet = os.path.join(outdir, f"{args.name}.jpg")
        run(["magick", "montage", "-label", "%t", "-pointsize", "11", "-background", "#111", "-fill", "#ddd",
             *labeled, "-tile", args.tile, "-geometry", "+2+2", "-quality", "82", sheet])
        print(f"sheet: {sheet}  frames {', '.join(os.path.basename(x)[:-4] for x in labeled)}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
