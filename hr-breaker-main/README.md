# HR-Breaker

Resume optimization tool that transforms any resume into a job-specific, ATS-friendly PDF.

![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)

## Features

- **Any format in** - LaTeX, plain text, markdown, HTML, PDF
- **Optimized PDF out** - Single-page, professionally formatted
- **LLM-powered optimization** - Tailors content to job requirements
- **Minimal changes** - Preserves your content, only restructures for fit
- **No fabrication** - Hallucination detection prevents made-up claims
- **Opinionated formatting** - Follows proven resume guidelines (one page, no fluff, etc.)
- **Multi-filter validation** - ATS simulation, keyword matching, structure checks
- **Web UI + CLI** - Streamlit dashboard or command-line
- **Debug mode** - Inspect optimization iterations

## How It Works

1. Upload resume in any text format (content source only)
2. Provide job posting URL or text description
3. LLM extracts content and generates optimized HTML resume
4. System runs internal filters (ATS simulation, keyword matching, hallucination detection)
5. If filters reject, regenerates using feedback
6. When all checks pass, renders HTML→PDF via WeasyPrint

## Quick Start

```bash
# Install
uv sync

# Configure
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY

# Run web UI
uv run streamlit run src/hr_breaker/main.py
```

## Usage

### Web UI

Launch with `uv run hr-breaker ui` (or `uv run streamlit run src/hr_breaker/main.py`)

1. Paste or upload resume
2. Enter job URL or description
3. Click optimize
4. Download PDF

### CLI

```bash
# From URL
uv run hr-breaker optimize resume.txt https://example.com/job

# From job description file
uv run hr-breaker optimize resume.txt job.txt

# Debug mode (saves iterations)
uv run hr-breaker optimize resume.txt job.txt -d

# Lenient mode - relaxes content constraints but still prevents fabricating experience. Use with caution!
uv run hr-breaker optimize resume.txt job.txt --no-shame

# List generated PDFs
uv run hr-breaker list
```

### GitHub Actions (upload from GitHub web UI)

1. Add `GOOGLE_API_KEY` in **Settings → Secrets and variables → Actions**.
2. Upload files to `uploads/` via **Add file → Upload files**:
   - `uploads/resume.pdf` (or `.txt`, `.md`, `.tex`)
   - `uploads/job.txt` (or `uploads/job.md`)
   - Optional: `uploads/job_url.txt` (contains a job posting URL)
3. The **Process uploads** workflow runs automatically.
4. Download the optimized PDF from the workflow **Artifacts**.

## Output

- Final PDFs: `output/<name>_<company>_<role>.pdf`
- Debug iterations: `output/debug_<company>_<role>/`
- Records: `output/index.json`

## Configuration

Set `GOOGLE_API_KEY` (required). For API gateways/proxies, set `GOOGLE_API_BASE_URL`
to the custom base URL (for Gemini-compatible endpoints, use the root URL without `/v1`).

---

## Architecture

```
src/hr_breaker/
├── agents/          # Pydantic-AI agents (optimizer, reviewer, etc.)
├── filters/         # Validation plugins (ATS, keywords, hallucination)
├── services/        # Rendering, scraping, caching
│   └── scrapers/    # Job scraper implementations
├── models/          # Pydantic data models
├── orchestration.py # Core optimization loop
├── main.py          # Streamlit UI
└── cli.py           # Click CLI
```

**Filters** (run by priority):

- 0: ContentLengthChecker - Size check
- 1: DataValidator - HTML structure validation
- 3: HallucinationChecker - Detect fabricated claims not supported by original resume
- 4: KeywordMatcher - TF-IDF matching
- 5: LLMChecker - Visual formatting check and LLM-based ATS simulation
- 6: VectorSimilarityMatcher - Semantic similarity
- 7: AIGeneratedChecker - Detect AI-sounding text

## Development

```bash
# Run tests
uv run pytest tests/

# Install dev dependencies
uv sync --group dev
```
