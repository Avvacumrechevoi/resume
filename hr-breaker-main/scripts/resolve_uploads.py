"""Resolve resume and job inputs from uploads folder."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Iterable

RESUME_EXTS = {".pdf", ".txt", ".md", ".tex"}
JOB_EXTS = {".txt", ".md"}


def _read_lines(path: Path) -> list[str]:
    if not path.exists():
        return []
    return [line.strip() for line in path.read_text().splitlines() if line.strip()]


def _select_resume(uploads_dir: Path, candidates: Iterable[Path]) -> Path | None:
    candidates = [p for p in candidates if p.parent == uploads_dir]
    exact = [
        p
        for p in candidates
        if p.stem == "resume" and p.suffix.lower() in RESUME_EXTS and p.exists()
    ]
    if exact:
        return exact[0]

    fallback = [
        p
        for p in uploads_dir.iterdir()
        if p.is_file() and p.stem == "resume" and p.suffix.lower() in RESUME_EXTS
    ]
    return fallback[0] if fallback else None


def _select_job(uploads_dir: Path, candidates: Iterable[Path]) -> Path | None:
    candidates = [p for p in candidates if p.parent == uploads_dir]
    exact = [
        p
        for p in candidates
        if p.stem in {"job", "job_url"} and p.suffix.lower() in JOB_EXTS and p.exists()
    ]
    if exact:
        return exact[0]

    fallback = [
        p
        for p in uploads_dir.iterdir()
        if p.is_file() and p.stem in {"job", "job_url"} and p.suffix.lower() in JOB_EXTS
    ]
    return fallback[0] if fallback else None


def _write_output(key: str, value: str) -> None:
    output_path = os.environ.get("GITHUB_OUTPUT")
    if output_path:
        with open(output_path, "a", encoding="utf-8") as handle:
            handle.write(f"{key}={value}\n")
    print(f"{key}={value}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--changed-files", type=Path, default=None)
    parser.add_argument("--uploads-dir", type=Path, default=Path("uploads"))
    args = parser.parse_args()

    uploads_dir = args.uploads_dir
    if not uploads_dir.exists():
        print("uploads directory not found")
        return 1

    changed_files: list[Path] = []
    if args.changed_files:
        changed_files = [Path(p) for p in _read_lines(args.changed_files)]

    resume_path = _select_resume(uploads_dir, changed_files)
    job_path = _select_job(uploads_dir, changed_files)

    if not resume_path:
        print("resume file not found (expected uploads/resume.*)")
        return 1
    if not job_path:
        print("job file not found (expected uploads/job.txt or uploads/job.md)")
        return 1

    job_input = job_path.as_posix()
    if job_path.stem == "job_url":
        url = job_path.read_text().strip()
        if not url:
            print("job_url.txt is empty")
            return 1
        job_input = url

    _write_output("resume_path", resume_path.as_posix())
    _write_output("job_input", job_input)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
