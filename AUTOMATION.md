# Property Searcher — Automation Task

Run the full property pipeline: collect new listings → enrich, filter, score, report.

**Schedule:** Tuesday and Friday mornings

## Scheduler Policy (authoritative)

Use **OpenClaw cron only** for this automation. Do **not** rely on system `crontab`, ad-hoc shell scripts in `/tmp`, or any parallel scheduler.

Run this automation in a **dedicated property pipeline session/thread** so the pipeline context stays isolated from normal chat.

### Model policy

- **Do not hard-code a specific model in this file.**
- The **parent scheduled run** chooses the model.
- Any spawned child/sub-agent tasks should **inherit the parent model by default**.
- Only use an explicit model override at spawn time when a specific run needs it (for example, if collection/browser extraction becomes unusually complex).

This keeps the workflow model-agnostic while still allowing a given scheduled run to use GPT-5.4 or switch back to MiniMax without editing this document.

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

Run the `/property-pipeline` skill in the dedicated property pipeline session/thread.

Follow `skills/property-pipeline/SKILL.md` in full — but **skip the "sync with upstream" step** inside that skill, since it was already done in Step 2 above.

### Execution contract

The run must follow this exact order:

1. Sync repo (`git pull origin main`)
2. Sync upstream (`git fetch upstream && git merge upstream/main`)
3. **Run collection**
4. **Verify collection really happened**
5. Run analysis from the repo root with the virtualenv active
6. Verify a new output directory was created for this run
7. Commit and push results

If collection did not happen, **fail the run instead of continuing to analysis**.

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

## Operational notes

- Use `source .venv/bin/activate` before running the analysis command.
- If the latest CSV is still an old file, or if no new run directory appears under `output/`, treat the automation as failed.
- Prefer one parent scheduled run that owns the whole workflow. Child tasks may be spawned for collection or diagnostics, but they should inherit the parent model unless there is an explicit one-off override.
- The scheduler configuration should be the place where model choice is controlled; this file defines workflow, not model selection.
