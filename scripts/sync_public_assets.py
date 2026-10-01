from pathlib import Path
import shutil


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "static"
DESTINATION = ROOT / "public" / "static"


def main():
    if not SOURCE.is_dir():
        raise SystemExit("The static asset source directory is missing.")
    for source_file in SOURCE.rglob("*"):
        if source_file.is_file():
            relative_path = source_file.relative_to(SOURCE)
            target = DESTINATION / relative_path
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_file, target)
    print("Vercel public assets synchronized from static/.")


if __name__ == "__main__":
    main()
