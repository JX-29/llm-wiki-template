#!/usr/bin/env python3
"""Check mp4 files for truncation by parsing the atom structure.

MEGA and other downloaders leave block-aligned stubs that look like valid
files by size but lack the moov atom and cut mid-mdat. NotebookLM returns
SourceStatus.ERROR on those after a 900 s wait each — cheaper to catch here.

Usage: python3 scripts/check_mp4_integrity.py <folder> [<folder> ...]
Exit code 1 if any broken file is found.
"""
import struct
import sys
from pathlib import Path


def probe(p: Path) -> dict:
    size = p.stat().st_size
    off, atoms, truncated = 0, [], False
    with p.open("rb") as f:
        while off < size:
            f.seek(off)
            hdr = f.read(8)
            if len(hdr) < 8:
                truncated = True
                break
            asz = struct.unpack(">I", hdr[:4])[0]
            atype = hdr[4:8].decode("latin-1", "replace")
            hdrlen = 8
            if asz == 1:
                ext = f.read(8)
                if len(ext) < 8:
                    truncated = True
                    break
                asz = struct.unpack(">Q", ext)[0]
                hdrlen = 16
            elif asz == 0:
                asz = size - off
            if asz < hdrlen:
                truncated = True
                break
            atoms.append(atype)
            if off + asz > size:
                truncated = True
                break
            off += asz
    return {"size": size, "moov": "moov" in atoms, "trunc": truncated,
            "covered": off, "atoms": atoms}


def main(roots: list[str]) -> int:
    bad = good = 0
    for root_s in roots:
        root = Path(root_s).expanduser()
        vids = sorted(p for p in root.rglob("*.mp4")
                      if not any(part.startswith("_") for part in p.parts))
        print(f"== {root} ({len(vids)} mp4) ==")
        for v in vids:
            r = probe(v)
            if r["moov"] and not r["trunc"]:
                good += 1
            else:
                bad += 1
                miss = r["size"] - r["covered"]
                print(f"  BROKEN  {v.relative_to(root)}")
                print(f"          {r['size']:,} b | moov={r['moov']} | "
                      f"parse stops at {r['covered']:,} (+{miss:,} b orphan) | "
                      f"atoms={r['atoms'][:5]}")
    print(f"\nintact: {good} | broken: {bad}")
    return 1 if bad else 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    sys.exit(main(sys.argv[1:]))
