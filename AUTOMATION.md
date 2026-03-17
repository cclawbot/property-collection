# AUTOMATION.md - Property Pipeline Automation

## Overview
This document defines the standardized workflow for running the property search pipeline via cron job.

## Schedule
- **Run time:** Tuesday & Friday at 2:00 AM
- **Frequency:** Twice per week

## Workflow

### 1. Setup
```bash
# First-time setup: add upstream remote (only needed once)
git remote add upstream https://github.com/zhuohanl/property-search.git

# Before each run: sync fork with upstream
git fetch upstream
git merge upstream/main
git checkout main
```

### 2. Run Collection Pipeline
Capture listings from the past 7 days:

```bash
# Activate virtual environment
source .venv/bin/activate

# Run collection (adjust dates as needed)
python -m cli collect \
  --suburb <suburb> \
  --state vic \
  --days 7 \
  --output data/property/listing_{date}.csv
```

### 3. Run Enrichment Pipeline
Enrich the collected listings:

```bash
python -m cli enrich \
  --input data/property/listing_{date}.csv \
  --output data/property/enriched_{date}.csv
```

### 4. Run Scoring Pipeline
Score and rank properties:

```bash
python -m cli score \
  --input data/property/enriched_{date}.csv \
  --output data/property/scored_{date}.csv
```

### 5. Run Filtering Pipeline
Apply user preferences to filter:

```bash
python -m cli filter \
  --input data/property/scored_{date}.csv \
  --output data/property/filtered_{date}.csv
```

### 6. Commit and Push Results
After successful pipeline run, commit and push all changes so users can see the results:

```bash
# Add all new files
git add output/ data/property/

# Commit with timestamp
git commit -m "Pipeline run: {n} shortlisted properties ($(date +%Y-%m-%d))"

# Push to main branch
git push origin main
```

### 7. Report Results
Post summary to #property-watch:
- Total listings collected
- Enrichment success rate
- Final filtered count
- Top 5 recommended properties

## Cron Command
```bash
openclaw cron add \
  --name "property pipeline runner" \
  --cron "0 2 * * 2,5" \
  --session isolated \
  --agent property-searcher \
  --message "Read AUTOMATION.md and execute the automation task" \
  --announce \
  --channel discord \
  --to 1481420691382210570
```

## Notes
- Always use `main` branch
- Check git status before running
- Review output files before posting results
- Handle errors gracefully and report failures
- **Always commit and push after each run** so users can see results in GitHub
