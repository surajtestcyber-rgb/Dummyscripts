from pathlib import Path
import subprocess
import shutil
import sys

def run_ps(cmd: str) -> None:
    """Run a PowerShell command and print output."""
    p = subprocess.run(
        ["powershell", "-NoProfile", "-Command", cmd],
        capture_output=True,
        text=True
    )
    if p.stdout.strip():
        print(p.stdout.strip())
    if p.stderr.strip():
        print(p.stderr.strip(), file=sys.stderr)

def main():
    # Update these paths as needed
    src = Path(r"D:\Users\suraj.pallagatti\Desktop\report.xlsx")
    dst_dir = Path(r"D:\Users\suraj.pallagatti\Cyberhaven\[SP]Test Site - Documents")
    dst = dst_dir / src.name

    stream_name = "report.xlsx"   # same as your PowerShell example
    ads_path = f"{src}:{stream_name}"

    print("✅ Step 1 — Create Main File")
    src.parent.mkdir(parents=True, exist_ok=True)
    src.write_bytes(b"")  # creates/overwrites empty file
    print(f"Created: {src}")

    print("\n✅ Step 2 — Create Alternate Data Stream (ADS)")
    secret_text = "Hidden inside Excel file my SSN is <REDACTED>"
    # Writing ADS is as simple as opening "filename:streamname" on NTFS
    with open(ads_path, "w", encoding="utf-8") as f:
        f.write(secret_text)
    print(f"Wrote ADS: {ads_path}")

    print("\n✅ Step 3 — Verify ADS Exists (PowerShell Get-Item -Stream *)")
    # Python itself doesn't list streams easily without extra Win32 APIs,
    # so we call PowerShell to match your verification step.
    run_ps(f'Get-Item "{src}" -Stream * | Format-Table -AutoSize')

    print("\n✅ Step 4 — Copy File to Another Location")
    dst_dir.mkdir(parents=True, exist_ok=True)
    # shutil.copy2 typically preserves ADS when copying within NTFS volumes
    shutil.copy2(src, dst)
    print(f"Copied to: {dst}")

    print("\n✅ Step 5 — Read Hidden ADS Content")
    with open(f"{src}:{stream_name}", "r", encoding="utf-8") as f:
        print(f.read())

    print("\n✅ Optional — Read ADS from COPIED file (if preserved)")
    try:
        with open(f"{dst}:{stream_name}", "r", encoding="utf-8") as f:
            print(f.read())
    except FileNotFoundError:
        print("(ADS not present on copied file — can happen if destination/copy method doesn't preserve streams.)")

if __name__ == "__main__":
    main()