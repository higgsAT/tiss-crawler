# tiss-crawler v2
TISS (TU Wien Informations-Systeme & Services) Crawler

## Description
Python crawler for extracting course data from [TISS](https://tiss.tuwien.ac.at) for a given university semester. It collects all courses across all study programs, deduplicates them, and stores raw HTML page sources alongside structured extracted data for later processing.

This is a rewrite of [v1](https://github.com/higgsAT/tiss-crawler/commit/9da4719d75af75d24d8b611bc07a2e7bdc53e27a). Compared to v1, this version:
- has no direct database connectivity (data is exported separately after crawling)
- drops Selenium in favour of `requests` + `BeautifulSoup` (TISS uses server-side rendering via JSF, so no JS execution is required)
- is smaller in scope and easier to maintain

---

## Crawl workflow
The crawler operates in three distinct, resumable phases:

**Phase 1 — Fetch all Studienpläne**
A single TISS page lists all study programs. The crawler fetches this page and extracts ~50 Studienplan URLs.

**Phase 2 — Extract courses per Studienplan**
Each Studienplan page is fetched and all corresponding courses (Lehrveranstaltungen) are extracted, including the mapping of which course belongs to which Studienplan. This mapping is retained for later use.

**Phase 3 — Crawl each unique course**
Duplicates are removed from the full course list. Each unique course is fetched twice — once in German, once in English. Raw HTML is stored and structured data is extracted.

---

## Extracted course data
For each course, the following is extracted in both German and English:
- Course number
- Course title
- Type (VO, UE, VU, SE, ...)
- ECTS
- SWS
- Lecturers
- Further fields as available on the course page

---

## Project structure
```
tiss-crawler/
  crawler.py                          # entry point
  config.yaml                         # user-facing configuration (see below)
  requirements.txt
  src/
    phases/
      studienplaene.py                # Phase 1: fetch all Studienpläne
      courses_discovery.py            # Phase 2: extract courses per Studienplan
      courses_crawl.py                # Phase 3: crawl each unique course
    parser.py                         # BeautifulSoup extraction logic
    state.py                          # load/save crawl state
    storage.py                        # file I/O (HTML, JSON)
    http_client.py                    # requests session + rate limiting
    export.py                         # post-crawl: JSON → SQL INSERT statements
    logger.py                         # logging setup
  output/                             # generated at runtime (see below)
```

---

## Configuration (`config.yaml`)
```yaml
semester: WS2025

output:
  base_dir: output/

crawl:
  sleep_between_requests: 2          # seconds between requests
  resume: true                       # pick up from existing state.json if present

logging:
  level: INFO
  file: output/logs/crawler.log
```

---

## Output structure
```
output/
  state.json                          # crawl state: progress tracking + visited sets
  study_programs/
    <program>/
      <program_name>__<semester>.html
  courses/
    <semester>/
      <course_number>__DE__<date>.html
      <course_number>__EN__<date>.html
  data/
    courses_<semester>.json           # structured extracted data for all courses
  logs/
    crawler.log
```

Raw HTML files are stored so that extraction can be re-run without re-crawling. The structured data file (`courses_<semester>.json`) is the basis for any downstream database import.

---

## Stop & resume
Crawl state is persisted in `output/state.json` after each fetch. On restart, the crawler loads existing state and skips already-completed items. Each of the three phases tracks progress independently.

---

## Rate limiting
Requests are throttled with a configurable sleep between fetches to avoid hitting TISS rate limits. No authentication is required — all course and Studienplan data is publicly accessible.

---

## Database export
This crawler does not write to a database directly. After crawling, a separate export step reads `courses_<semester>.json` and generates SQL `INSERT` statements (or performs the insert via a script). This keeps the crawl and the import decoupled.

---

## Tech stack
- Python 3.x
- `requests` — HTTP
- `BeautifulSoup` — HTML parsing
- `json` — state and data storage
- `logging` — structured logs

---

## Usage
```bash
python crawler.py --semester WS2025
```

Resuming an interrupted crawl:
```bash
python crawler.py --semester WS2025 --resume
```
