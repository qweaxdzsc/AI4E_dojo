"""Install the pinned Quarto CLI into backend/.tools after SHA-256 verification."""

from __future__ import annotations

import argparse
import hashlib
import os
import platform
import shutil
import subprocess
import tarfile
import tempfile
import time
import urllib.request
import urllib.error
from pathlib import Path


VERSION = "1.10.18"
ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / ".tools" / "quarto" / VERSION
PACKAGES = {
    ("Darwin", "arm64"): ("macos", "ddd6a71a9e0448ab15fb655bc589e11cb6589a248ec35ccd7f7f44137531688e"),
    ("Darwin", "x86_64"): ("macos", "ddd6a71a9e0448ab15fb655bc589e11cb6589a248ec35ccd7f7f44137531688e"),
    ("Linux", "x86_64"): ("linux-amd64", "afad071b5bd22c02f2d300695743189d3650e0537a53073e654b630cff2b0c73"),
    ("Linux", "aarch64"): ("linux-arm64", "f6a07df68e25330b5df34f65d3df66bca605acce3b830c593a58e91884d4cf6c"),
}


def _inside_directory(root: Path, candidate: Path) -> bool:
    try:
        candidate.relative_to(root)
        return True
    except ValueError:
        return False


def safe_extract_archive(bundle: tarfile.TarFile, destination: Path) -> None:
    """Extract safely on Python 3.11 and use stdlib's data filter when available."""

    try:
        bundle.extractall(destination, filter="data")
        return
    except TypeError:
        # ``filter=`` was added after Python 3.11.  Validate paths, links and
        # special files ourselves before using the older extraction API.
        pass

    root = destination.resolve()
    members = bundle.getmembers()
    for member in members:
        member_path = (root / member.name).resolve()
        if not _inside_directory(root, member_path):
            raise SystemExit(f"Unsafe archive path: {member.name}")
        if member.isdev() or member.isfifo():
            raise SystemExit(f"Unsupported special file in archive: {member.name}")
        if member.issym():
            link_target = (member_path.parent / member.linkname).resolve()
            if not _inside_directory(root, link_target):
                raise SystemExit(f"Unsafe archive symlink: {member.name} -> {member.linkname}")
        elif member.islnk():
            link_target = (root / member.linkname).resolve()
            if not _inside_directory(root, link_target):
                raise SystemExit(f"Unsafe archive hard link: {member.name} -> {member.linkname}")
    bundle.extractall(destination, members=members)


def current_version(binary: Path) -> str | None:
    if not binary.is_file():
        return None
    try:
        result = subprocess.run(
            [binary, "--version"], capture_output=True, text=True, timeout=30, check=True
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return result.stdout.strip()


def download_with_progress(url: str, destination: Path, *, timeout: float, retries: int) -> None:
    """Download a large release asset with bounded retries and visible progress."""

    request = urllib.request.Request(url, headers={"User-Agent": "Qoder-design2-quarto-installer/1.0"})
    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        destination.unlink(missing_ok=True)
        try:
            print(f"Download attempt {attempt}/{retries}: {url}", flush=True)
            with urllib.request.urlopen(request, timeout=timeout) as response, destination.open("wb") as output:
                total = int(response.headers.get("Content-Length") or 0)
                received = 0
                last_report = 0.0
                started = time.monotonic()
                while True:
                    chunk = response.read(1024 * 1024)
                    if not chunk:
                        break
                    output.write(chunk)
                    received += len(chunk)
                    now = time.monotonic()
                    if now - last_report >= 1.0 or (total and received == total):
                        elapsed = max(now - started, 0.001)
                        speed = received / elapsed / 1048576
                        if total:
                            percent = received * 100 / total
                            print(
                                f"  {received / 1048576:.1f}/{total / 1048576:.1f} MiB "
                                f"({percent:.1f}%) · {speed:.1f} MiB/s",
                                flush=True,
                            )
                        else:
                            print(f"  {received / 1048576:.1f} MiB · {speed:.1f} MiB/s", flush=True)
                        last_report = now
            if total and received != total:
                raise OSError(f"incomplete download: expected {total} bytes, got {received}")
            print(f"Download complete: {received / 1048576:.1f} MiB", flush=True)
            return
        except (TimeoutError, OSError, urllib.error.URLError) as error:
            last_error = error
            destination.unlink(missing_ok=True)
            if attempt < retries:
                delay = min(2 ** (attempt - 1), 8)
                print(f"Download failed: {error}. Retrying in {delay}s…", flush=True)
                time.sleep(delay)
    raise SystemExit(
        "Quarto download failed after "
        f"{retries} attempts: {last_error}\n"
        "If GitHub release assets are blocked, download the official tar.gz on another network "
        "and rerun with --archive /path/to/quarto-1.10.18-platform.tar.gz."
    )


def prune_unused_macos_architecture(target: Path, machine: str) -> list[Path]:
    """The official macOS archive is universal; retain only this host's tools."""
    if platform.system() != "Darwin":
        return []
    keep = "aarch64" if machine == "arm64" else "x86_64"
    tools = target / "bin" / "tools"
    removed: list[Path] = []
    for candidate in ("aarch64", "x86_64"):
        path = tools / candidate
        if candidate != keep and path.is_dir():
            shutil.rmtree(path)
            removed.append(path)
    return removed


def main() -> None:
    parser = argparse.ArgumentParser(description="Install pinned Quarto after checksum verification")
    parser.add_argument("--archive", type=Path, help="Use an already downloaded official tar.gz")
    parser.add_argument("--force", action="store_true", help="Reinstall even when Quarto 1.10.18 is already valid")
    parser.add_argument("--timeout", type=float, default=60.0, help="Socket timeout in seconds (default: 60)")
    parser.add_argument("--retries", type=int, default=3, help="Download attempts (default: 3)")
    parser.add_argument(
        "--download-url",
        help="Override the official URL with a trusted mirror; the official SHA-256 is still required",
    )
    args = parser.parse_args()
    key = (platform.system(), platform.machine())
    if key not in PACKAGES:
        raise SystemExit(f"Unsupported platform: {key}")
    suffix, expected = PACKAGES[key]
    name = f"quarto-{VERSION}-{suffix}.tar.gz"
    url = args.download_url or os.environ.get("QUARTO_DOWNLOAD_URL") or f"https://github.com/quarto-dev/quarto-cli/releases/download/v{VERSION}/{name}"
    binary = TARGET / "bin" / "quarto"
    installed = current_version(binary)
    if installed == VERSION and not args.force:
        print(f"Quarto {VERSION} is already installed: {binary}")
        return
    if installed and not args.force:
        print(f"Replacing unexpected Quarto version {installed} with {VERSION}", flush=True)
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="qoder-quarto-") as temporary:
        archive = Path(temporary) / name
        if args.archive:
            if not args.archive.is_file():
                raise SystemExit(f"Archive does not exist: {args.archive}")
            shutil.copy2(args.archive, archive)
        else:
            download_with_progress(
                url,
                archive,
                timeout=max(5.0, args.timeout),
                retries=max(1, args.retries),
            )
        actual = hashlib.sha256(archive.read_bytes()).hexdigest()
        if actual != expected:
            raise SystemExit(f"Checksum mismatch: expected {expected}, got {actual}")
        extracted = Path(temporary) / "extracted"
        extracted.mkdir()
        with tarfile.open(archive, "r:gz") as bundle:
            safe_extract_archive(bundle, extracted)
        candidate = next(extracted.glob("**/bin/quarto"), None)
        if candidate is None:
            raise SystemExit("Downloaded archive does not contain bin/quarto")
        source_root = candidate.parent.parent
        staging = TARGET.with_name(TARGET.name + ".staging")
        if staging.exists():
            shutil.rmtree(staging)
        shutil.copytree(source_root, staging)
        if TARGET.exists():
            shutil.rmtree(TARGET)
        os.replace(staging, TARGET)
    removed = prune_unused_macos_architecture(TARGET, platform.machine())
    result = subprocess.run([binary, "--version"], capture_output=True, text=True, timeout=30, check=True)
    if result.stdout.strip() != VERSION:
        raise SystemExit(f"Installed Quarto version mismatch: {result.stdout.strip()}")
    for path in removed:
        print(f"Removed unused architecture: {path}")
    print(binary)


if __name__ == "__main__":
    main()
