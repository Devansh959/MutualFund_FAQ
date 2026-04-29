import subprocess
import os
import sys
import logging
from datetime import datetime

# Setup logging
os.makedirs("logs", exist_ok=True)
log_filename = f"logs/ingest_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename),
        logging.StreamHandler(sys.stdout)
    ]
)

def run_script(script_path):
    logging.info(f"Starting execution: {script_path}")
    try:
        # Use sys.executable to ensure we use the same environment
        result = subprocess.run(
            [sys.executable, script_path],
            check=True,
            capture_output=True,
            text=True
        )
        logging.info(f"Successfully completed: {script_path}")
        logging.debug(f"Output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"Error executing {script_path}: {e.stderr}")
        return False
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return False

def cleanup_old_data():
    """
    Retains only the most recent file in data/raw and data/processed 
    to prevent local storage bloat.
    """
    logging.info("--- Phase: Cleanup ---")
    data_dirs = ["data/raw", "data/processed"]
    
    for directory in data_dirs:
        if not os.path.exists(directory):
            continue
            
        files = [os.path.join(directory, f) for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
        # Keep latest_facts.json as it's a fixed name and always 'new'
        files = [f for f in files if "latest_facts.json" not in f]
        
        if len(files) <= 1:
            continue
            
        # Sort by creation time
        files.sort(key=os.path.getctime, reverse=True)
        
        # Delete all but the most recent
        for old_file in files[1:]:
            try:
                os.remove(old_file)
                logging.info(f"Removed old data file: {old_file}")
            except Exception as e:
                logging.warning(f"Failed to remove {old_file}: {e}")

def main():
    logging.info("=== Starting Mutual Fund Ingestion Pipeline (Local) ===")
    
    phases = [
        ("Scraping", "src/ingestion/scraper.py"),
        ("Processing", "src/ingestion/processor.py"),
        ("Embedding", "src/ingestion/embedder.py")
    ]
    
    success_count = 0
    for phase_name, script_path in phases:
        logging.info(f"--- Phase: {phase_name} ---")
        if run_script(script_path):
            success_count += 1
        else:
            logging.error(f"Pipeline halted due to error in phase: {phase_name}")
            break
            
    if success_count == len(phases):
        logging.info("=== Ingestion Pipeline Completed Successfully ===")
        cleanup_old_data()
    else:
        logging.warning(f"=== Ingestion Pipeline Failed ({success_count}/{len(phases)} phases successful) ===")

if __name__ == "__main__":
    main()
