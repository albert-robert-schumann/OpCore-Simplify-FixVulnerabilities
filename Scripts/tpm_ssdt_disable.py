#!/usr/bin/env python3
"""
One-click ACPI -> DSL -> TPM detect -> SSDT (_STA=Zero) -> AML -> OpenCore config update.

Steps:
1. Dump ACPI tables (acpidump/acpidump.exe)
2. Disassemble with iasl (-da -dl)
3. Detect TPM devices by HID (PNP0C31, MSFT0101) and names (TPM, TPM2, PTT, FTPM)
4. Emit SSDT-DisableTPM.dsl with guarded overrides (CondRefOf + _STA=Zero)
5. Compile SSDT to AML with iasl
6. Add SSDT-DisableTPM.aml to ACPI->Add in EFI/OC/config.plist

Usage:
  python disable_tpm_full.py [--efi /mnt/EFI] [--config EFI/OC/config.plist]
"""

import os, sys, platform, subprocess, shutil, re, textwrap, plistlib, argparse
from pathlib import Path

# Work directories
WORKDIR = Path.cwd() / "acpi_work"
DUMP_DIR = WORKDIR / "dump"
DSL_DIR = WORKDIR / "dsl"
OUT_SSDT_DSL = WORKDIR / "SSDT-DisableTPM.dsl"
OUT_SSDT_AML = WORKDIR / "SSDT-DisableTPM.aml"

# Detection rules
TPM_HIDS = {"PNP0C31", "MSFT0101"}
TPM_NAMES = {"TPM", "TPM2", "PTT", "FTPM"}

def info(msg): print(f"[+] {msg}")
def warn(msg): print(f"[!] {msg}")
def err(msg): print(f"[-] {msg}", file=sys.stderr)

def ensure_dirs():
    DUMP_DIR.mkdir(parents=True, exist_ok=True)
    DSL_DIR.mkdir(parents=True, exist_ok=True)

def which_tool(names):
    for n in names:
        p = shutil.which(n)
        if p:
            return Path(p)
    return None

def detect_acpidump():
    if platform.system() == "Windows":
        local = Path.cwd() / "acpidump.exe"
        if local.exists():
            return local
        return which_tool(["acpidump.exe"])
    else:
        return which_tool(["acpidump"])

def detect_iasl():
    return which_tool(["iasl"])

def run(cmd, cwd=None, check=True):
    info("Running: " + " ".join(cmd))
    return subprocess.run(cmd, cwd=cwd, check=check)

def dump_acpi(acpidump):
    info("Dumping ACPI tables...")
    # Dump all tables in binary format
    run([str(acpidump), "-b"], cwd=DUMP_DIR, check=False)

def list_aml_like(dirpath: Path):
    files = list(dirpath.glob("*.aml")) + list(dirpath.glob("*.dat"))
    return files

def disassemble(iasl):
    aml_files = list_aml_like(DUMP_DIR)
    if not aml_files:
        warn("No AML/DAT found after dump; attempting named dumps (DSDT/SSDT) on Windows...")
        acp = detect_acpidump()
        if acp and platform.system() == "Windows":
            for name in ("DSDT", "SSDT"):
                run([str(acp), "-b", "-n", name, "-o", f"{name}.aml"], cwd=DUMP_DIR, check=False)
            aml_files = list_aml_like(DUMP_DIR)
    if not aml_files:
        err("No ACPI AML/DAT files found. Run as Administrator/root and ensure acpidump is available.")
        sys.exit(2)

    info(f"Disassembling {len(aml_files)} file(s) with iasl")
    run([str(iasl), "-da", "-dl"] + [str(f) for f in aml_files], cwd=DUMP_DIR, check=True)

    for dsl in DUMP_DIR.glob("*.dsl"):
        shutil.move(str(dsl), DSL_DIR)
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
    Build qualified ACPI paths with type info.
    """
    lines = dsl_text.splitlines()
    type_re = re.compile(r'^\s*(Device|Name|Method)\s*`\(([^,\)`]+)')
    paths = []
    stack = []  # (name, depth)
    depth = 0

    for i, raw in enumerate(lines):
        depth += raw.count("{") - raw.count("}")
        while stack and stack[-1][1] >= depth:
            stack.pop()

        m = type_re.match(raw)
        if not m:
            continue

        obj_type, name = m.group(1), m.group(2).strip()
        stack.append((name, depth))

        elems = [nm for nm, _ in stack]
        norm = []
        for e in elems:
            if "^" in e:
                ups = e.count("^")
                for _ in range(ups):
                    if norm:
                        norm.pop()
                e = e.replace("^", "")
            norm.append(e.rstrip("_"))

        path = "\\\\" + ".".join(norm)
        paths.append((path, i, obj_type))

    return paths

def find_devices(paths, lines):
    hid_devices, name_devices = set(), set()
    for p, idx, typ in paths:
        if p.endswith("._HID"):
            txt = lines[idx].upper()
            if any(h in txt for h in TPM_HIDS):
                hid_devices.add(p[:-len("._HID")])
        if typ == "Device":
            leaf = p.split(".")[-1].upper()
            if leaf in TPM_NAMES:
                name_devices.add(p)
    return sorted(hid_devices | name_devices)

def emit_ssdt(devices):
    externals, bodies = [], []

    for full in devices:
        normalized = full.replace("\\\\.", "\\\\").lstrip("\\\\")
        parts = normalized.split(".")
        if len(parts) < 2:
            continue
        parent, leaf = ".".join(parts[:-1]), parts[-1]
        externals.append(f'    External (_{parent if parent.startswith("_") else parent}, DeviceObj)')
        bodies.append(textwrap.dedent(f"""
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
        """))

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

def compile_ssdt(iasl):
    run([str(iasl), str(OUT_SSDT_DSL)], cwd=WORKDIR, check=True)
    if OUT_SSDT_AML.exists():
        info(f"Compiled SSDT → {OUT_SSDT_AML}")
    else:
        warn("iasl did not produce SSDT-DisableTPM.aml; check compile output.")

def add_ssdt_to_config(config_path: Path, ssdt_name="SSDT-DisableTPM.aml"):
    if not config_path.exists():
        err(f"config.plist not found at {config_path}")
        return False

    # Backup
    backup = config_path.with_suffix(".backup.plist")
    shutil.copy2(config_path, backup)
    info(f"Backed up config to {backup}")

    with config_path.open("rb") as f:
        config = plistlib.load(f)

    if "ACPI" not in config:
        config["ACPI"] = {}
    if "Add" not in config["ACPI"]:
        config["ACPI"]["Add"] = []

    # Normalize existing entries to avoid duplicates
    add_list = config["ACPI"]["Add"]
    for entry in add_list:
        if entry.get("Path") == ssdt_name:
            info("SSDT already present in ACPI->Add; no changes made.")
            return True

    new_entry = {
        "Path": ssdt_name,
        "Comment": "Disable TPM via SSDT (_STA=Zero)",
        "Enabled": True
    }
    add_list.append(new_entry)

    with config_path.open("wb") as f:
        plistlib.dump(config, f)

    info(f"Added {ssdt_name} to ACPI->Add in {config_path}")
    return True

def find_default_config_path(efi_root: Path):
    # Default: EFI/OC/config.plist under the provided/mounted EFI root
    candidate = efi_root / "OC" / "config.plist"
    if candidate.exists():
        return candidate
    # Common alternative: EFI/OC/config.plist when efi_root is the mounted EFI partition root
    candidate = efi_root / "EFI" / "OC" / "config.plist"
    if candidate.exists():
        return candidate
    return None

def copy_ssdt_to_efi(efi_root: Path, ssdt_path: Path):
    targets = [
        efi_root / "OC" / "ACPI",
        efi_root / "EFI" / "OC" / "ACPI"
    ]
    for t in targets:
        if t.exists():
            t.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ssdt_path, t / ssdt_path.name)
            info(f"Copied {ssdt_path.name} to {t}")
            return t / ssdt_path.name
    warn("Could not locate EFI/OC/ACPI under provided EFI root; skipped copy.")
    return None

def parse_args():
    ap = argparse.ArgumentParser(description="Disable TPM via SSDT and update OpenCore config.plist")
    ap.add_argument("--efi", type=Path, default=None,
                    help="Mounted EFI root path (e.g., /Volumes/EFI or X:\\EFI). If provided, script will copy AML and update config.plist.")
    ap.add_argument("--config", type=Path, default=None,
                    help="Explicit path to OpenCore config.plist. Overrides --efi detection.")
    return ap.parse_args()

def main():
    args = parse_args()

    ensure_dirs()
    acpidump, iasl = detect_acpidump(), detect_iasl()
    if not acpidump:
        err("acpidump/acpidump.exe not found in PATH or next to the script.")
        sys.exit(1)
    if not iasl:
        err("iasl not found in PATH. Install ACPICA iasl.")
        sys.exit(1)

    dump_acpi(acpidump)
    disassemble(iasl)

    files = read_dsl_files()
    if not files:
        err("No DSL files found after disassembly.")
        sys.exit(2)

    all_paths, all_lines = [], []
    for _, text in files:
        all_paths.extend(build_paths(text))
        all_lines.extend(text.splitlines())

    devices = find_devices(all_paths, all_lines)
    if not devices:
        warn("No TPM devices found by HID or name hints. Exiting without generating SSDT.")
        sys.exit(3)

    info("Detected TPM device paths:")
    for d in devices:
        print("  -", d)

    emit_ssdt(devices)
    compile_ssdt(iasl)

    # Optional EFI integration
    if args.config or args.efi:
        ssdt_target = None
        if args.efi:
            ssdt_target = copy_ssdt_to_efi(args.efi, OUT_SSDT_AML)
            cfg = args.config or find_default_config_path(args.efi)
        else:
            cfg = args.config

        if not cfg:
            warn("Could not resolve config.plist path; skipping plist update.")
        else:
            added = add_ssdt_to_config(cfg, OUT_SSDT_AML.name)
            if added:
                info("OpenCore config updated successfully.")

    info("Done. If you didn't use --efi/--config, place SSDT-DisableTPM.aml in EFI/OC/ACPI and add it to ACPI->Add.")
    info(f"Work directory: {WORKDIR}")

if __name__ == "__main__":
    main()
