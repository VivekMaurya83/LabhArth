"""
LabhArth AI — Dataset Downloader
==================================
Downloads the government schemes dataset (shrijayan/gov_myscheme) from Hugging Face Hub.
"""

import os
from pathlib import Path
from typing import List
from huggingface_hub import snapshot_download

from backend.utils.logger import logger


def download_dataset(dest_dir: str = "data") -> List[Path]:
    """
    Downloads the gov_myscheme dataset PDF files from Hugging Face Hub.
    Caches the files locally under dest_dir/text_data.

    Args:
        dest_dir: Base directory to download dataset files into.

    Returns:
        List of Path objects representing the unique scheme PDF files.
    """
    dest_path = Path(dest_dir)
    pdf_dir = dest_path / "text_data"

    # Check if we already have local PDFs to avoid slow remote LFS/snapshot check
    if pdf_dir.exists():
        local_files = list(pdf_dir.glob("*.pdf"))
        unique_local = [f for f in local_files if not f.name.lower().endswith(" copy.pdf")]
        if len(unique_local) > 100:
            logger.info(f"Detected {len(unique_local)} unique local PDFs in {pdf_dir}. Skipping Hugging Face download.")
            unique_local.sort(key=lambda p: p.name.lower())
            return unique_local

    logger.info("Initializing Hugging Face dataset download...")
    
    # Run snapshot download (only fetching PDFs in the text_data/ subfolder)
    try:
        snapshot_download(
            repo_id="shrijayan/gov_myscheme",
            repo_type="dataset",
            allow_patterns="text_data/*.pdf",
            local_dir=str(dest_path),
            local_dir_use_symlinks=False,
        )
        logger.info("Hugging Face download complete.")
    except Exception as e:
        logger.error(f"Failed to download dataset from Hugging Face: {e}")
        # If files exist locally, we can proceed as fallback
        if not pdf_dir.exists():
            raise RuntimeError(f"Hugging Face download failed and local backup {pdf_dir} does not exist.") from e
        logger.warning("Proceeding with existing files in local backup.")

    if not pdf_dir.exists():
        raise FileNotFoundError(f"PDF directory not found at {pdf_dir} after download attempt.")

    # List all files and filter duplicates
    all_files = list(pdf_dir.glob("*.pdf"))
    unique_files: List[Path] = []

    for file_path in all_files:
        name = file_path.name
        # Skip duplicates (e.g., 'xxx copy.pdf')
        if name.lower().endswith(" copy.pdf"):
            logger.debug(f"Skipping duplicate copy file: {name}")
            continue
        unique_files.append(file_path)

    # Sort files by name to ensure consistent ordering in iteration
    unique_files.sort(key=lambda p: p.name.lower())
    
    logger.info(f"Dataset acquisition complete. Found {len(unique_files)} unique scheme PDFs (skipped duplicate copies).")
    return unique_files


if __name__ == "__main__":
    # Test script execution
    logging_level = os.environ.get("LOG_LEVEL", "INFO")
    import logging
    logging.basicConfig(level=logging_level)
    
    try:
        files = download_dataset()
        print(f"Success! Found {len(files)} files.")
        if files:
            print(f"First file: {files[0]}")
    except Exception as exc:
        print(f"Error during execution: {exc}")
