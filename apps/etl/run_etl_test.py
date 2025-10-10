"""Test ETL pipeline with safe date range."""

import logging
from datetime import datetime
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Import after logging setup
from apps.etl.pipeline import run_pipeline
from apps.etl.config import Settings

# Use a safe date range in the past (January 2024)
test_date = datetime(2024, 1, 15)  # Middle of January 2024

print("=" * 80)
print(f"Running ETL pipeline with test date: {test_date}")
print("=" * 80)

# Create settings with 30-day window
settings = Settings(nsf_awards_window_days=30)
print(f"\nSettings loaded:")
print(f"  - NSF Awards API: {settings.nsf_awards_api}")
print(f"  - Window days: {settings.nsf_awards_window_days}")
print(f"  - Grants XML URL: {settings.grants_xml_url}")
print(f"  - Local data dir: {settings.local_data_dir}")
print(f"  - Database URL: {'✓ Configured' if settings.database_url else '✗ Not configured'}")
print(f"  - Supabase key: {'✓ Configured' if settings.supabase_service_key else '✗ Not configured'}")
print()

try:
    run_pipeline(run_date=test_date, settings=settings)
    print("\n" + "=" * 80)
    print("✓ ETL pipeline completed successfully!")
    print("=" * 80)
except Exception as e:
    print("\n" + "=" * 80)
    print(f"✗ ETL pipeline failed: {e}")
    print("=" * 80)
    raise
