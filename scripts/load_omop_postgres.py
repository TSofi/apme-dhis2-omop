"""
OMOP CDM v5.4 Bulk Ingestion Script (Sprint 3).
Loads transformed CSVs from omop_output/ into PostgreSQL using COPY
with explicit column mappings matching CSV headers.
"""
import os
import sys
import psycopg2

DB_HOST = os.getenv("OMOP_DB_HOST", "localhost")
DB_PORT = os.getenv("OMOP_DB_PORT", "5433")
DB_NAME = os.getenv("OMOP_DB_NAME", "omop")
DB_USER = os.getenv("OMOP_DB_USER", "postgres")
DB_PASSWORD = os.getenv("OMOP_DB_PASSWORD", "postgres")

INPUT_DIR = "omop_output"
TABLE_ORDER = ["location", "care_site", "person", "drug_exposure", "observation"]


def load_table(cursor, table_name, csv_path):
    print(f"Loading {table_name} from {csv_path}...")
    with open(csv_path, "r", encoding="utf-8") as f:
        # Read header to pass explicit column names to COPY
        header_line = f.readline().strip()
        columns = [col.strip() for col in header_line.split(",") if col.strip()]
        columns_str = ", ".join(columns)

        # Rewind file back to start
        f.seek(0)
        copy_sql = f"""
            COPY cdm.{table_name} ({columns_str})
            FROM STDIN
            WITH (FORMAT csv, HEADER true, NULL '');
        """
        cursor.copy_expert(sql=copy_sql, file=f)
    print(f"  -> Successfully loaded {table_name}.")


def main():
    print("=" * 60)
    print("Starting OMOP CDM v5.4 Database Ingestion")
    print(f"Target: {DB_USER}@{DB_HOST}:{DB_PORT}/{DB_NAME} (schema: cdm)")
    print("=" * 60)

    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        conn.autocommit = False
    except Exception as e:
        print(f"[FAIL] Database connection failed: {e}")
        sys.exit(1)

    try:
        with conn.cursor() as cur:
            print("\nCleaning existing records (idempotent run)...")
            for table_name in reversed(TABLE_ORDER):
                cur.execute(f"TRUNCATE TABLE cdm.{table_name} CASCADE;")
            print("  -> Tables truncated.")

            print("\nBulk-loading CSV data with explicit column headers...")
            for table_name in TABLE_ORDER:
                csv_path = os.path.join(INPUT_DIR, f"{table_name}.csv")
                if not os.path.exists(csv_path):
                    raise FileNotFoundError(f"Missing CSV: {csv_path}")
                load_table(cur, table_name, csv_path)

            conn.commit()
            print("\n[OK] Transaction committed successfully.")

            print("\n--- Ingestion Row Counts ---")
            for table_name in TABLE_ORDER:
                cur.execute(f"SELECT COUNT(*) FROM cdm.{table_name};")
                count = cur.fetchone()[0]
                print(f"  * cdm.{table_name:<16} : {count:>4} rows")

    except Exception as e:
        conn.rollback()
        print(f"\n[FAIL] Ingestion error: {e}")
        sys.exit(1)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
