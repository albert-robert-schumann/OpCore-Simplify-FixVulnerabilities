#!/usr/bin/env python3
"""
One-click ACPI -> DSL -> TPM detect -> SSDT (_STA=Zero) -> AML pipeline.

- Dumps ACPI tables using acpidump/acpidump.exe
- Disassembles with iasl (-da -dl)
- Parses DSL for TPM by HID (PNP0C31, MSFT0101) and names (TPM, TPM2, PTT, FTPM)
- Emits SSDT-DisableTPM.dsl with guarded overrides
- Compiles SSDT to AML with iasl

Usage:
  python disable_tpm_pipeline.py
"""

import os
import sys
import platform
import subprocess
from pathlib import Path
import shutil
import re
import textwrap

WORKDIR = Path.cwd() / "acpi_work"
DUMP_DIR = WORKDIR / "dump"
DSL_DIR = WORKDIR / "dsl"
OUT_SSDT_DSL = WORKDIR / "SSDT-DisableTPM.dsl"
OUT_SSDT_AML = WORKDIR / "SSDT-DisableTPM.aml"

TPM_HIDS = {"PNP0C31", "MSFT0101"}
TPM_NAME_HINTS = {"TPM", "TPM2", "PTT", "FTPM"}

def info(msg):
    print(f"[+] {msg}")

def warn(msg):
    print(f"[!] {msg}")

def err(msg):
    print(f"[-] {msg}", file=sys.stderr)

def ensure_dirs():
    DUMP_DIR.mkdir(parents=True, exist_ok=True)
    DSL_DIR.mkdir(parents=True, exist_ok=True)

def which_tool(candidates):
    for c in candidates:
        p = shutil.which(c)
        if p:
            return Path(p)
    return None

def detect_acpidump():
    if platform.system() == "Windows":
        # Prefer acpidump.exe next to script or in PATH
        local = Path.cwd() / "acpidump.exe"
        if local.exists():
            return local
        found = which_tool(["acpidump.exe"])
        return found
    else:
        return which_tool(["acpidump"])

def detect_iasl():
    return which_tool(["iasl"])

def run(cmd, cwd=None, check=True):
    info(f"Running: {' '.join(cmd)}")
    return subprocess.run(cmd, cwd=cwd, check=check)

def dump_acpi(acpidump_path: Path):
    info(f"Dumping ACPI with: {acpidump_path}")
    # Dump all tables in binary AML format
    if platform.system() == "Windows":
        # Dortania acpidump.exe flags: -b dumps binary tables, no need to specify names
        run([str(acpidump_path), "-b"], cwd=DUMP_DIR)
    else:
        # ACPICA acpidump supports similar flags
        run([str(acpidump_path), "-b"], cwd=DUMP_DIR)

    # Some acpidump builds output .dat; convert .dat to .aml via iasl if needed later
    # We keep whatever is produced—.aml or .dat—then disassemble with iasl.

def list_aml_like(dirpath: Path):
    files = list(dirpath.glob("*.aml"))
    # Some Windows dumps produce .dat files; iasl can disassemble via -da -dl on .dat too
    files += list(dirpath.glob("*.dat"))
    return files

def disassemble_aml(iasl_path: Path):
    aml_files = list_aml_like(DUMP_DIR)
    if not aml_files:
        warn("No AML/DAT files found. Trying an alternative dump command...")
        # Try named dumps for DSDT/SSDT on Windows if generic dump failed
        acpidump = detect_acpidump()
        if acpidump and platform.system() == "Windows":
            # Attempt explicit DSDT and SSDT dump
            for name in ("DSDT", "SSDT"):
                try:
                    run([str(acpidump), "-b", "-n", name, "-o", f"{name}.aml"], cwd=DUMP_DIR, check=False)
                except Exception:
                    pass
            aml_files = list_aml_like(DUMP_DIR)

    if not aml_files:
        err("Still no ACPI AML/DAT files to disassemble. Run as Admin/root and ensure acpidump works.")
        sys.exit(2)

    info(f"Disassembling {len(aml_files)} file(s) with iasl")
    cmd = [str(iasl_path), "-da", "-dl"] + [str(f) for f in aml_files]
    run(cmd, cwd=DUMP_DIR)

    # Move resulting .dsl into DSL_DIR
    for dsl in DUMP_DIR.glob("*.dsl"):
        target = DSL_DIR / dsl.name
        dsl.replace(target)
    info(f"Moved DSL files to {DSL_DIR}")

def read_dsl_files():
    files = []
    for p in DSL_DIR.glob("*.dsl"):
        try:
            files.append((p, p.read_text(errors="ignore")))
        except Exception as e:
            warn(f"Failed to read {p}: {e}")
    return files

def build_paths(dsl_text: str):
    """
    Construct qualified ACPI paths (\\._SB.PCI0.LPCB.TPM etc.) with type info.
    """
    lines = dsl_text.splitlines()
    type_re = re.compile(r'^\s*(Processor|Scope|Device|Method|Name)\s*\(([^,\)]+)')
    paths = []
    stack = []  # (name, depth)
    depth = 0

    for i, raw in enumerate(lines):
        # Update depth
        opens = raw.count("{")
        closes = raw.count("}")
        depth += opens - closes

        # pop stack to current depth
        while stack and stack[-1][1] >= depth:
            stack.pop()

        m = type_re.match(raw)
        if not m:
            continue

        obj_type, name = m.group(1), m.group(2).strip()
        stack.append((name, depth))

        # We only record devices and names/methods for path qualification
        if obj_type not in {"Device", "Name", "Method"}:
            continue

        # Build path from stack, stop when encountering root symbols
        elems = [nm for nm, _ in stack]
        # Normalize carets (^), remove trailing underscores aesthetics
        norm = []
        for e in elems:
            if "^" in e:
                ups = e.count("^")
                for _ in range(ups):
                    if norm:
                        norm.pop()
                e = e.replace("^", "")
            norm.append(e.rstrip("_"))

        # Prepend root \\ if not already absolute
        path = "\\\\" + ".".join(norm)
        paths.append((path, i, obj_type))

    return paths

def find_devices_with_hid(paths, lines, hid):
    hid_bases = set()
    for p, idx, typ in paths:
        if p.endswith("._HID"):
            line = lines[idx]
            if hid.upper() in line.upper():
                hid_bases.add(p[:-len("._HID")])
    devices = []
    for p, idx, typ in paths:
        if typ == "Device" and p in hid_bases:
            devices.append(p)
    return devices

def find_tpm_candidates(paths, lines):
    # HID-based
    hid_devices = set()
    for hid in TPM_HIDS:
        for dev in find_devices_with_hid(paths, lines, hid):
            hid_devices.add(dev)

    # Name-based (leaf equals hint)
    name_devices = set()
    for p, idx, typ in paths:
        if typ == "Device":
            leaf = p.split(".")[-1].upper()
            if leaf in TPM_NAME_HINTS:
                name_devices.add(p)

    candidates = sorted(hid_devices | name_devices)
    return candidates

def emit_ssdt(device_paths):
    externals = []
    bodies = []

    for full in device_paths:
        # Normalize to remove leading \\.
        normalized = full.replace("\\\\.", "\\\\").lstrip("\\\\")
        parts = normalized.split(".")
        if len(parts) < 2:
            # Skip improbable
            continue
        parent = ".".join(parts[:-1])
        leaf = parts[-1]

        externals.append(f'    External (_{parent if parent.startswith("_") else parent}, DeviceObj)')
        body = textwrap.dedent(f"""
            Scope (_{parent if parent.startswith("_") else parent})
            {{
                If (CondRefOf ({leaf}))
                {{
                    Device ({leaf})
                    {{
                        Name (_STA, Zero)
                    }}
                }}
            }}
        """)
        bodies.append(body)

    ssdt = textwrap.dedent(f"""\
        // Auto-generated: Disable TPM by masking _STA=Zero for discovered devices
        DefinitionBlock ("", "SSDT", 2, "OC", "DisableTPM", 0)
        {{
        {os.linesep.join(externals)}

        {os.linesep.join(bodies)}
        }}
    """)
    OUT_SSDT_DSL.write_text(ssdt)
    info(f"Wrote {OUT_SSDT_DSL}")

def compile_ssdt(iasl_path: Path):
    run([str(iasl_path), str(OUT_SSDT_DSL)])
    if OUT_SSDT_AML.exists():
        info(f"Compiled SSDT → {OUT_SSDT_AML}")
    else:
        warn("iasl did not produce SSDT-DisableTPM.aml; check iasl output above.")

def summarize(candidates):
    if not candidates:
        warn("No TPM devices found by HID or name hints.")
        return
    info("Detected TPM device paths:")
    for p in candidates:
        print(f"  - {p}")

def main():
    info("Starting TPM disable pipeline")
    ensure_dirs()

    acpidump = detect_acpidump()
    if not acpidump:
        err("acpidump/acpidump.exe not found. On Windows, place Dortania's acpidump.exe in PATH or next to this script. On Linux/macOS, install acpidump (ACPICA).")
        sys.exit(1)

    iasl = detect_iasl()
    if not iasl:
        err("iasl not found. Install ACPICA iasl (apt/brew) and ensure it's in PATH.")
        sys.exit(1)

    dump_acpi(acpidump)
    disassemble_aml(iasl)

    files = read_dsl_files()
    if not files:
        err(f"No DSL files found in {DSL_DIR}. Disassembly may have failed.")
        sys.exit(2)

    # Aggregate paths and line buffers
    all_paths = []
    all_lines = []
    for p, text in files:
        all_paths.extend(build_paths(text))
        all_lines.extend(text.splitlines())

    candidates = find_tpm_candidates(all_paths, all_lines)
    summarize(candidates)
    if not candidates:
        warn("Proceeding without generating SSDT. Run with elevated privileges or verify ACPI dump.")
        sys.exit(3)

    emit_ssdt(candidates)
    compile_ssdt(iasl)

    info("Done. Place SSDT-DisableTPM.aml in EFI/OC/ACPI and add it under ACPI → Add in your OpenCore config.")
    info(f"Work directory: {WORKDIR}")

if __name__ == "__main__":
    main()
