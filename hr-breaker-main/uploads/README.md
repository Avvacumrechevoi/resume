# Uploads

Place files in this folder via the GitHub web UI to trigger the workflow.

Required filenames:
- `uploads/resume.pdf` (or `.txt`, `.md`, `.tex`)
- `uploads/job.txt` (or `uploads/job.md`)

Optional:
- `uploads/job_url.txt` (contains a job posting URL)

Each push to this folder triggers the GitHub Actions workflow to generate a
new optimized PDF and upload it as a workflow artifact.
