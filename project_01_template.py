from pathlib import Path
from zipfile import ZipFile

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
ARCHIVE_PATH = BASE_DIR / "Datasets.zip"
DATA_DIR = BASE_DIR / "Datasets"
CSV_FILES = [DATA_DIR / f"events_part{i}.csv" for i in range(1, 9)]
OUTPUT_PATH = BASE_DIR / "problematic_event_ids.txt"

# %% 1. Read the Dataset. Extract once. Reuse the CSV files when all eight are already present.
if not all(csv_path.is_file() for csv_path in CSV_FILES):
    if not ARCHIVE_PATH.is_file():
        raise FileNotFoundError(
            f"Place Datasets.zip or all eight extracted CSV files in: {BASE_DIR}"
        )
    print("Extracting Datasets.zip...")
    with ZipFile(ARCHIVE_PATH) as archive:
        for csv_path in CSV_FILES:
            archive.extract(f"Datasets/{csv_path.name}", path=BASE_DIR)

missing_files = [str(p) for p in CSV_FILES if not p.is_file()]
if missing_files:
    raise FileNotFoundError(f"Missing CSV files: {missing_files}")

print("All 8 CSV files are ready.")


def iter_event_batches(csv_files, chunksize=50_000):
    for csv_path in csv_files:
        # Preserve IDs, telephone numbers, empty cells, and dirty values as text.
        options = dict(dtype="string", na_filter=False, encoding="utf-8-sig")
        if chunksize is None:
            yield pd.read_csv(csv_path, **options)
        else:
            with pd.read_csv(csv_path, chunksize=chunksize, **options) as reader:
                yield from reader


# %% 2. ANALYSIS — fill in the blank area for your chosen mode
USE_CHUNKS = True   # Set to False to load all eight files into memory.
CHUNK_SIZE = 50_000

# Add problematic original event IDs to this set in either mode.
# Keep it outside the loop so results are retained across batches.
problematic_event_ids = set()

if USE_CHUNKS:
    total_rows = 0
    for batch in iter_event_batches(CSV_FILES, chunksize=CHUNK_SIZE):
        original_event_ids = batch["event_id"].copy()
        total_rows += len(batch)

        # Add your analysis here.
        # Retain any state or intermediate results needed across batches.






    print(f"Total rows read: {total_rows:,}")
else:
    events = pd.concat(iter_event_batches(CSV_FILES, chunksize=None), ignore_index=True)
    original_event_ids = events["event_id"].copy()
    print(f"Total rows loaded into memory: {len(events):,}")

    # Add your analysis of events here.






# The complete assignment dataset is expected to contain 9,604,621 rows.
# If needed, finalize checks across all files/batches here before exporting.




# %% 3. OUTPUT — no changes needed
# One original event_id per line, with no header, duplicates, or explanation.
output_ids = sorted(set(problematic_event_ids))
with OUTPUT_PATH.open("w", encoding="utf-8", newline="\n") as output_file:
    for event_id in output_ids:
        output_file.write(f"{event_id}\n")

print(output_ids)
print(f"Saved {len(output_ids):,} problematic event IDs to: {OUTPUT_PATH}")


