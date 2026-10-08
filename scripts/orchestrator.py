"""
Master End-to-End Orchestrator (Sprint 4).
Runs all pipeline stages sequentially:
  1. Generate synthetic cohort
  2. Ingest into DHIS2 Tracker
  3. Extract and transform to OMOP CSVs
  4. Seed CDM Concept vocabulary
  5. Bulk load CSVs into PostgreSQL
  6. Run referential integrity and quality validation
"""
import subprocess
import sys
import time

PIPELINE_STAGES = [
    ("Step 1: Generate Synthetic Cohort", "scripts/generate_cohort.py"),
    ("Step 2: Ingest Cohort to DHIS2", "scripts/ingest_cohort.py"),
    ("Step 3: Extract and Transform to OMOP CSVs", "scripts/etl_dhis2_to_omop.py"),
    ("Step 4: Load OMOP Vocabulary Concepts", "scripts/load_vocabularies_subset.py"),
    ("Step 5: Bulk Load to OMOP PostgreSQL", "scripts/load_omop_postgres.py"),
    ("Step 6: Run Quality and Clinical Validation", "scripts/validate_omop_quality.py")
]

def run_stage(title, script_path):
    print("\n" + "=" * 65)
    print(f"RUNNING: {title}")
    print(f"Target : {script_path}")
    print("=" * 65)
    start_time = time.time()
    result = subprocess.run([sys.executable, script_path])
    elapsed = time.time() - start_time
    if result.returncode != 0:
        print(f"\n[ERROR] Stage '{title}' failed with exit code {result.returncode}!")
        sys.exit(result.returncode)
    print(f"[OK] Completed in {elapsed:.2f} seconds.")

def main():
    total_start = time.time()
    print("*" * 65)
    print("   DHIS2 TRACKER -> OMOP CDM v5.4 AUTOMATED PIPELINE RUNNER      ")
    print("*" * 65)
    for title, script in PIPELINE_STAGES:
        run_stage(title, script)
    total_elapsed = time.time() - total_start
    print("\n" + "*" * 65)
    print(f" PIPELINE COMPLETE: All stages finished in {total_elapsed:.2f}s ")
    print("*" * 65)

if __name__ == "__main__":
    main()
