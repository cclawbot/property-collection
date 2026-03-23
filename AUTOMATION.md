# Property Searcher — Automation Task

Run the full property pipeline: collect new listings → enrich, filter, score, report.

**Schedule:** Tuesday and Friday mornings

---

## Step 1: First-time setup (skip if repo already cloned)

If `property-search/` does not exist yet, clone the fork and configure the upstream remote:

```bash
# Clone the fork (origin)
git clone https://github.com/cclawbot/property-search.git

# Add upstream — source of truth for skills and code
cd property-search
git remote add upstream https://github.com/zhuohanl/property-search.git

# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install Python dependencies
uv pip install -r analysis/requirements.txt
```

---

## Step 2: Enter the repo

```bash
cd property-search
```

All subsequent commands must be run from this directory.

---

## Step 3: Pull validated data from remote

The property-validator agent runs Mon/Thu nights and pushes an updated CSV (with sold/removed listings flagged) to `origin`. Pull that first so this run works from a clean, validated dataset:

```bash
git pull origin main
```

---

## Step 4: Sync with upstream (code updates)

Pull the latest skills and config from the source repo before running:

```bash
git fetch upstream
git merge upstream/main
```

If there are merge conflicts (e.g. in `analysis/src/`), resolve them before proceeding.

---

## Step 5: Run the pipeline

Run the `/property-pipeline` skill.

Follow `skills/property-pipeline/SKILL.md` in full — but **skip the "sync with upstream" step** inside that skill, since it was already done in Step 2 above.

### ⚠️ Verification — MUST NOT SKIP

After running the pipeline, **verify collection actually happened**:

1. Check the latest CSV timestamp:
   ```bash
   ls -la data/property/*.csv | tail -1
   ```

2. The CSV should have today's date in the filename (e.g., `property_collection_list_20260324_...csv`).

3. **If the CSV is OLD (e.g., from March 21)**, collection DID NOT RUN. You MUST:
   - Run `/property-collection` skill manually to force collection
   - Verify "New this run: X" shows X > 0
   - Do NOT proceed to Step 6 until collection succeeds

4. **Silent failure detection**: If the pipeline says "New to enrich: 0" or "New this run: 0", this means collection was skipped or failed. Fix it before pushing results.

---

## Step 6: Push results to remote

Commit and push the new collection CSV and analysis outputs so results are available for review:

```bash
git add data/property/ output/
git commit -m "feat: property pipeline run [property-searcher]"
git push origin main
```
