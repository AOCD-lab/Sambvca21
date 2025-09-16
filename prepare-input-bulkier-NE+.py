#!/usr/bin/env python3
# Python 3.6+
import sys
import os
import re
from typing import List, Tuple, Dict, Optional

# ---------------------- helpers ----------------------

def last_float_in_line(line: str) -> Optional[float]:
    toks = re.findall(r'[-+]?\d*\.\d+|[-+]?\d+', line)
    return float(toks[-1]) if toks else None

def ints_in_line(line: str) -> List[int]:
    return [int(x) for x in re.findall(r'\d+', line)]

def find_line_idx(lines: List[str], pattern: str, start: int = 0,
                  max_ahead: Optional[int] = None) -> int:
    """Find first index >= start whose text matches regex pattern (case-insensitive)."""
    pat = re.compile(pattern, re.IGNORECASE)
    end = len(lines) if max_ahead is None else min(len(lines), start + max_ahead)
    for i in range(start, end):
        if pat.search(lines[i]):
            return i
    return -1

def next_nonempty_idx(lines: List[str], idx: int, max_ahead: int = 10) -> int:
    for k in range(idx + 1, min(len(lines), idx + 1 + max_ahead)):
        if lines[k].strip():
            return k
    return -1

def next_line_with_digits(lines: List[str], idx: int, max_ahead: int = 10) -> Optional[str]:
    """Return the first subsequent line (within max_ahead) that contains at least one digit."""
    for k in range(idx + 1, min(len(lines), idx + 1 + max_ahead)):
        if re.search(r'\d', lines[k]):
            return lines[k]
    return None

def parse_int_list_after_header(lines: List[str], header_regex: str,
                                start: int = 0, max_seek: int = 50, max_ahead: int = 10) -> List[int]:
    """Find a header, then grab integers from the first following line that has digits."""
    hdr_idx = find_line_idx(lines, header_regex, start=start, max_ahead=max_seek)
    if hdr_idx == -1:
        return []
    candidate = next_line_with_digits(lines, hdr_idx, max_ahead=max_ahead)
    return ints_in_line(candidate) if candidate else []

# --------------- parse .out file ---------------

def parse_out(path: str):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    # defaults (in case of imperfect inputs)
    num_remove, remove_atoms = 0, []
    num_center, center_atoms = 0, []
    num_z, z_atoms = 0, []
    num_xz, xz_atoms = 0, []
    radius, displacement, bin_width = 5.0, 0.0, 0.10
    flag_remove_H, flag_steric_map = 0, 0
    atom_types_count: Optional[int] = None
    radii_table: List[str] = []

    # (1) No. of atoms to be removed + list
    idx = find_line_idx(lines, r'Checking:\s*No\.\s*of\s*atoms\s*to\s*be\s*removed\s*:|No\.\s*of\s*atoms\s*to\s*be\s*removed\s*:')
    if idx != -1:
        v = last_float_in_line(lines[idx])
        if v is not None:
            num_remove = int(v)
    remove_atoms = parse_int_list_after_header(
        lines,
        r'Checking:\s*Atoms\s*to\s*be\s*removed\s*:|Atoms\s*to\s*be\s*removed\s*:',
        start=idx if idx != -1 else 0,
        max_seek=30,
        max_ahead=10
    )

    # (2) Sphere center count + list
    idx = find_line_idx(lines, r'Checking:\s*No\.\s*of\s*atoms\s*defining\s*the\s*sphere\s*center\s*:|No\.\s*of\s*atoms\s*defining\s*the\s*sphere\s*center\s*:')
    if idx != -1:
        v = last_float_in_line(lines[idx])
        if v is not None:
            num_center = int(v)
    center_atoms = parse_int_list_after_header(
        lines,
        r'Checking:\s*Atoms\s*defining\s*the\s*sphere\s*center\s*:|Atoms\s*defining\s*the\s*sphere\s*center\s*:',
        start=idx if idx != -1 else 0,
        max_seek=30,
        max_ahead=10
    )

    # (3) Z-axis count + list
    idx = find_line_idx(lines, r'Checking\s*:\s*No\.\s*of\s*atoms\s*defining\s*the\s*Z-axis\s*:|No\.\s*of\s*atoms\s*defining\s*the\s*Z-axis\s*:')
    if idx != -1:
        v = last_float_in_line(lines[idx])
        if v is not None:
            num_z = int(v)
        k = next_nonempty_idx(lines, idx, max_ahead=10)
        if k != -1:
            z_atoms = ints_in_line(lines[k])

    # (4) XZ-plane count + list
    idx = find_line_idx(lines, r'Checking\s*:\s*No\.\s*of\s*atoms\s*defining\s*the\s*XZ-plane\s*:|No\.\s*of\s*atoms\s*defining\s*the\s*XZ-plane\s*:')
    if idx != -1:
        v = last_float_in_line(lines[idx])
        if v is not None:
            num_xz = int(v)
        k = next_nonempty_idx(lines, idx, max_ahead=10)
        if k != -1:
            xz_atoms = ints_in_line(lines[k])

    # (5) Scalars (radius, displacement, bin width)
    idx = find_line_idx(lines, r'Checking:\s*Vbur\s*sphere\s*radius|Vbur\s*sphere\s*radius')
    if idx != -1:
        v = last_float_in_line(lines[idx])
        if v is not None:
            radius = v
    idx = find_line_idx(lines, r'Checking:\s*Displacement\s*from\s*origin|Displacement\s*from\s*origin')
    if idx != -1:
        v = last_float_in_line(lines[idx])
        if v is not None:
            displacement = v
    idx = find_line_idx(lines, r'Checking:\s*Bin\s*width|Bin\s*width')
    if idx != -1:
        v = last_float_in_line(lines[idx])
        if v is not None:
            bin_width = v

    # (6) Flags
    if find_line_idx(lines, r'Checking:\s*Removing\s*H\s*atoms|Removing\s*H\s*atoms') != -1:
        flag_remove_H = 1
    if find_line_idx(lines, r'Checking:\s*Outputting\s*steric\s*map|Outputting\s*steric\s*map') != -1:
        flag_steric_map = 1

    # (7) Atom types + radii table
    idx = find_line_idx(lines, r'Checking:\s*No\.\s*of\s*atom\s*types\s*in\s*your\s*database\s*:|No\.\s*of\s*atom\s*types\s*in\s*your\s*database\s*:')
    if idx != -1:
        v = last_float_in_line(lines[idx])
        if v is not None:
            atom_types_count = int(v)
        idx2 = find_line_idx(lines, r'Checking:\s*Atom\s*labels\s*and\s*radius\s*in\s*the\s*database\s*:|Atom\s*labels\s*and\s*radius\s*in\s*the\s*database\s*:', start=idx, max_ahead=30)
        if idx2 != -1:
            k = idx2 + 1
            while k < len(lines):
                s = lines[k].rstrip("\n")
                if not s or s.strip().startswith("Checking:") or "No. of atoms of input frame" in s:
                    break
                radii_table.append(s)
                k += 1
    if atom_types_count is None:
        atom_types_count = len([r for r in radii_table if r.strip()])

    # -------- B) Octants analysis (+z, %V b from last column) --------
    oct_vals: Dict[str, float] = {}
    in_oct = False
    for line in lines:
        if "Octants analysis" in line:
            in_oct = True
            continue
        if in_oct:
            if line.strip().startswith("Octant"):
                continue
            if not line.strip():
                break
            parts = line.split()
            if len(parts) >= 6 and parts[0] in ("SW+z", "NW+z", "NE+z", "SE+z"):
                try:
                    oct_vals[parts[0]] = float(parts[-1])
                except ValueError:
                    pass

    # -------- C) Rotated-frame coordinates --------
    atom_count_line: Optional[str] = None
    title_line: Optional[str] = None
    coords: List[Tuple[str, float, float, float]] = []
    in_rot = False
    got_count = False
    got_title = False
    for line in lines:
        if line.strip().startswith("Results: Coordinates of rotated frame"):
            in_rot = True
            continue
        if in_rot and not got_count:
            atom_count_line = line.strip()
            got_count = True
            continue
        if in_rot and got_count and not got_title:
            title_line = line.rstrip("\n")
            got_title = True
            continue
        if in_rot and got_title:
            s = line.strip()
            if s.startswith("Results :") or s.startswith("Results:") or s == "":
                break
            parts = line.split()
            if len(parts) >= 4:
                atom = parts[0]
                try:
                    x, y, z = map(float, parts[1:4])
                except ValueError:
                    continue
                coords.append((atom, x, y, z))

    return (
        num_remove, remove_atoms,
        num_center, center_atoms,
        num_z, z_atoms,
        num_xz, xz_atoms,
        radius, displacement, bin_width,
        flag_remove_H, flag_steric_map,
        atom_types_count, radii_table,
        oct_vals,
        atom_count_line, title_line, coords
    )

# ---------------- transforms & writer ----------------

def transform_coords(coords: List[Tuple[str, float, float, float]], mode: str) -> List[Tuple[str, float, float, float]]:
    out = []
    for atom, x, y, z in coords:
        if mode == 'flip_yz':          # NW+z
            out.append((atom, -x, y, z))
        elif mode == 'flip_xz':        # SE+z
            out.append((atom, x, -y, z))
        elif mode == 'rot_z_180':      # SW+z
            out.append((atom, -x, -y, z))
        else:                          # NE+z or default
            out.append((atom, x, y, z))
    return out

def write_combined(path: str,
                   num_remove: int, remove_atoms: List[int],
                   num_center: int, center_atoms: List[int],
                   num_z: int, z_atoms: List[int],
                   num_xz: int, xz_atoms: List[int],
                   radius: float, displacement: float, bin_width: float,
                   flag_remove_H: int, flag_steric_map: int,
                   atom_types_count: int, radii_table: List[str],
                   atom_count_line: str, title_line: str,
                   coords: List[Tuple[str, float, float, float]]) -> None:
    """Write job parameters (compact) + XYZ header/coords into one .inp file."""
    with open(path, "w", encoding="utf-8") as f:
        # Job parameters
        f.write(f"{num_remove}\n")
        f.write((" " + "  ".join(str(a) for a in remove_atoms) + "   \n") if remove_atoms else " \n")
        f.write(f"-1\n")
        f.write((" " + "  ".join(str(a) for a in center_atoms) + "              \n") if center_atoms else " \n")
        f.write(f"{num_z}\n")
        f.write((" " + "  ".join(str(a) for a in z_atoms) + "               \n") if z_atoms else " \n")
        f.write(f"{num_xz}\n")
        f.write((" " + "  ".join(str(a) for a in xz_atoms) + "     \n") if xz_atoms else " \n")
        f.write(f"{radius:.1f}\n")
        f.write(f"{displacement:.1f}\n")
        f.write(f"{bin_width:.2f}\n")
        f.write(f"{1 if flag_remove_H else 0}\n")
        f.write(f"{1 if flag_steric_map else 0}\n")
        f.write("1\n")  # third flag as in your sample
        f.write(f"{atom_types_count}\n")
        for row in radii_table:
            f.write(row + "\n")

        # Coordinates (XYZ)
        f.write(f"{atom_count_line}\n")
        f.write(f"{title_line}\n")
        for atom, x, y, z in coords:
            f.write(f"{atom:2s} {x:11.5f} {y:11.5f} {z:11.5f}\n")

# ---------------- tie-break & main ----------------

def choose_winner(oct_vals: Dict[str, float]) -> str:
    """Tie rules: if tie includes NE+z -> NE+z (no action).
       Else pick among tied by priority: SW+z > NW+z > SE+z.
       If single winner, return it."""
    keys = ["SW+z", "NW+z", "NE+z", "SE+z"]
    if not all(k in oct_vals for k in keys):
        raise ValueError("Missing required +z octants in data.")
    max_val = max(oct_vals[k] for k in keys)
    winners = [k for k in keys if abs(oct_vals[k] - max_val) < 1e-9]
    if "NE+z" in winners:
        return "NE+z"
    if len(winners) == 1:
        return winners[0]
    for p in ["SW+z", "NW+z", "SE+z"]:
        if p in winners:
            return p
    return winners[0]  # fallback

def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python3 gg.py <file.out>")
        sys.exit(1)

    outpath = sys.argv[1]
    base, _ = os.path.splitext(outpath)

    (
        num_remove, remove_atoms,
        num_center, center_atoms,
        num_z, z_atoms,
        num_xz, xz_atoms,
        radius, displacement, bin_width,
        flag_remove_H, flag_steric_map,
        atom_types_count, radii_table,
        oct_vals,
        atom_count_line, title_line, coords
    ) = parse_out(outpath)

    if not oct_vals or atom_count_line is None or title_line is None or not coords:
        print("Error: could not parse octants and/or rotated coordinates.")
        sys.exit(2)

    print("Octants (+z) %V b:", oct_vals)
    chosen = choose_winner(oct_vals)

    mode = 'none'
    if chosen == "NE+z":
        print("NE+z is the most buried (or tied). No action needed.")
    elif chosen == "NW+z":
        print("Chosen most buried: NW+z. Flipping on the yz-plane (x -> -x).")
        mode = 'flip_yz'
    elif chosen == "SE+z":
        print("Chosen most buried: SE+z. Flipping on the xz-plane (y -> -y).")
        mode = 'flip_xz'
    elif chosen == "SW+z":
        print("Chosen most buried: SW+z. Rotating 180° around z (x,y -> -x,-y).")
        mode = 'rot_z_180'

    coords_t = transform_coords(coords, mode)
    inp_out = f"{base}-SP.inp"
    write_combined(
        inp_out,
        num_remove, remove_atoms,
        num_center, center_atoms,
        num_z, z_atoms,
        num_xz, xz_atoms,
        radius if radius is not None else 5.0,
        displacement if displacement is not None else 0.0,
        bin_width if bin_width is not None else 0.10,
        flag_remove_H, flag_steric_map,
        atom_types_count if atom_types_count is not None else len([r for r in radii_table if r.strip()]),
        radii_table,
        atom_count_line, title_line, coords_t
    )
    print("Final combined file written to:", inp_out)

if __name__ == "__main__":
    main()

