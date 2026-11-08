#!/usr/bin/env python3
"""Static preflight for a DOOM Android APK and its AdrenoTools hook libraries.

This only inventories ZIP members, ELF headers and hashes. It does not install
or execute the APK and cannot prove that a custom driver was loaded at runtime.
"""

from __future__ import annotations

import argparse
import hashlib
import sys
import zipfile
from collections import defaultdict
from pathlib import Path
from typing import BinaryIO


DEFAULT_HOOK_LIBRARIES = (
    "libmain_hook.so",
    "libfile_redirect_hook.so",
    "libgsl_alloc_hook.so",
    "libhook_impl.so",
)

ABI_ELF = {
    "arm64-v8a": (2, 183, "ELF64 little-endian AArch64"),
    "armeabi-v7a": (1, 40, "ELF32 little-endian ARM"),
    "armeabi": (1, 40, "ELF32 little-endian ARM"),
    "x86": (1, 3, "ELF32 little-endian Intel 80386"),
    "x86_64": (2, 62, "ELF64 little-endian AMD x86-64"),
    "riscv64": (2, 243, "ELF64 little-endian RISC-V"),
}


def elf_description(stream: BinaryIO) -> tuple[str, tuple[int, int] | None]:
    header = stream.read(64)
    if len(header) < 20 or header[:4] != b"\x7fELF":
        return "invalid or truncated ELF header", None

    elf_class = header[4]
    data_encoding = header[5]
    class_name = {1: "ELF32", 2: "ELF64"}.get(elf_class, f"ELF class {elf_class}")
    endian_name = {1: "little-endian", 2: "big-endian"}.get(
        data_encoding, f"data encoding {data_encoding}"
    )
    if data_encoding not in (1, 2):
        return f"{class_name}, {endian_name}", None

    byteorder = "little" if data_encoding == 1 else "big"
    machine = int.from_bytes(header[18:20], byteorder)
    machine_name = {
        3: "Intel 80386",
        40: "ARM",
        62: "AMD x86-64",
        183: "AArch64",
        243: "RISC-V",
    }.get(machine, f"e_machine={machine}")
    return f"{class_name} {endian_name} {machine_name}", (elf_class, machine)


def sha256_member(archive: zipfile.ZipFile, info: zipfile.ZipInfo) -> str:
    digest = hashlib.sha256()
    with archive.open(info, "r") as member:
        for chunk in iter(lambda: member.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Inspect the renderer and AdrenoTools hook libraries in a DOOM APK. "
            "Presence is not proof of runtime loading."
        )
    )
    parser.add_argument("apk", type=Path, help="APK to inspect; it is never extracted")
    parser.add_argument(
        "--renderer-lib",
        default="libdm.so",
        help="renderer library basename (default: libdm.so)",
    )
    parser.add_argument(
        "--hook-lib",
        action="append",
        dest="hook_libraries",
        help=(
            "required hook library basename; repeat as needed. By default, checks "
            "the four AdrenoTools hooks expected by the documented DOOM case."
        ),
    )
    parser.add_argument(
        "--skip-hooks",
        action="store_true",
        help="skip hook-library presence checks for ports without AdrenoTools",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    apk_path: Path = args.apk
    hook_libraries = tuple(args.hook_libraries or DEFAULT_HOOK_LIBRARIES)

    if not apk_path.is_file():
        print(f"ERROR: APK not found: {apk_path}", file=sys.stderr)
        return 2

    try:
        archive = zipfile.ZipFile(apk_path, "r")
    except (OSError, zipfile.BadZipFile) as exc:
        print(f"ERROR: cannot read APK ZIP: {exc}", file=sys.stderr)
        return 2

    libraries: dict[str, dict[str, list[zipfile.ZipInfo]]] = defaultdict(
        lambda: defaultdict(list)
    )
    with archive:
        for info in archive.infolist():
            parts = info.filename.split("/")
            if len(parts) == 3 and parts[0] == "lib" and parts[2].endswith(".so"):
                libraries[parts[1]][parts[2]].append(info)

        print(f"APK: {apk_path.name}")
        print(f"ZIP readable: yes ({len(archive.infolist())} entries)")
        print(f"Renderer requested: {args.renderer_lib}")

        renderer_abis = sorted(
            abi for abi, names in libraries.items() if args.renderer_lib in names
        )
        if not renderer_abis:
            print("ERROR: renderer library was not found under lib/<abi>/.")
            return 1

        passed = True
        for abi in renderer_abis:
            print(f"\nABI directory: {abi}")
            expected = ABI_ELF.get(abi)
            renderer_infos = libraries[abi][args.renderer_lib]
            if len(renderer_infos) > 1:
                print(f"  ERROR: duplicate ZIP entries for {args.renderer_lib}")
                passed = False

            renderer = renderer_infos[0]
            with archive.open(renderer, "r") as member:
                description, identity = elf_description(member)
            print(f"  {'OK' if identity else 'ERROR'} {args.renderer_lib}: {description}")
            print(f"    size={renderer.file_size} bytes sha256={sha256_member(archive, renderer)}")
            if identity is None:
                passed = False
            elif expected is None:
                print("    NOTE: ABI is not in this script's ELF identity table.")
            elif identity != expected[:2]:
                print(
                    f"    ERROR: ELF identity does not match expected {abi}: {expected[2]}"
                )
                passed = False
            else:
                print(f"    ABI match: {expected[2]}")

            if args.skip_hooks:
                continue

            for hook_name in hook_libraries:
                hook_infos = libraries[abi].get(hook_name, [])
                if not hook_infos:
                    print(f"  MISSING {hook_name}")
                    passed = False
                    continue
                if len(hook_infos) > 1:
                    print(f"  ERROR: duplicate ZIP entries for {hook_name}")
                    passed = False
                hook = hook_infos[0]
                with archive.open(hook, "r") as member:
                    description, identity = elf_description(member)
                print(f"  {'OK' if identity else 'ERROR'} {hook_name}: {description}")
                print(f"    size={hook.file_size} bytes sha256={sha256_member(archive, hook)}")
                if identity is None:
                    passed = False
                elif expected is not None and identity != expected[:2]:
                    print(f"    ERROR: ELF identity does not match expected ABI {abi}")
                    passed = False

        if args.skip_hooks:
            print("\nHook checks: skipped by request")
        else:
            print(f"\nHook libraries checked: {', '.join(hook_libraries)}")

    print("\nLIMIT: APK contents and ELF ABI do not prove a custom driver was selected or loaded.")
    print("Confirm the renderer/driver from logs or status emitted by the same running process.")
    print("RESULT: static package preflight " + ("passed" if passed else "needs review"))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
