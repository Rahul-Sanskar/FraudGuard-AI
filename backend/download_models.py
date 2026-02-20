"""
Download ML models at runtime from cloud storage or HuggingFace.
This keeps models out of the Docker image, reducing size significantly.
"""
import os
import sys
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MODEL_DIR = Path("ml_models")
MODEL_DIR.mkdir(exist_ok=True)

# Model URLs (replace with your actual URLs)
MODELS = {
    "deepfake_model_enhanced.pt": {
        "url": os.getenv("DEEPFAKE_MODEL_URL", ""),
        "size_mb": 18,
    },
    "document_model.pt": {
        "url": os.getenv("DOCUMENT_MODEL_URL", ""),
        "size_mb": 41,
    },
    "voice_spoof_model.pt": {
        "url": os.getenv("VOICE_MODEL_URL", ""),
        "size_mb": 361,
    },
}


def download_from_url(url: str, destination: Path) -> bool:
    """Download file from URL with progress."""
    if not url:
        logger.warning(f"No URL provided for {destination.name}")
        return False
    
    try:
        import requests
        from tqdm import tqdm
        
        logger.info(f"Downloading {destination.name} from {url}")
        
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        
        with open(destination, 'wb') as f, tqdm(
            total=total_size,
            unit='B',
            unit_scale=True,
            desc=destination.name
        ) as pbar:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                pbar.update(len(chunk))
        
        logger.info(f"✅ Downloaded {destination.name}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to download {destination.name}: {e}")
        return False


def download_from_huggingface(repo_id: str, filename: str, destination: Path) -> bool:
    """Download model from HuggingFace Hub."""
    try:
        from huggingface_hub import hf_hub_download
        
        logger.info(f"Downloading {filename} from HuggingFace: {repo_id}")
        
        downloaded_path = hf_hub_download(
            repo_id=repo_id,
            filename=filename,
            cache_dir=str(MODEL_DIR),
        )
        
        # Move to expected location
        import shutil
        shutil.move(downloaded_path, destination)
        
        logger.info(f"✅ Downloaded {filename} from HuggingFace")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to download from HuggingFace: {e}")
        return False


def check_models_exist() -> bool:
    """Check if all required models exist."""
    all_exist = True
    for model_name in MODELS.keys():
        model_path = MODEL_DIR / model_name
        if model_path.exists():
            size_mb = model_path.stat().st_size / (1024 * 1024)
            logger.info(f"✅ {model_name} exists ({size_mb:.1f} MB)")
        else:
            logger.warning(f"❌ {model_name} missing")
            all_exist = False
    return all_exist


def download_all_models() -> bool:
    """Download all required models."""
    logger.info("Starting model download...")
    
    success_count = 0
    for model_name, config in MODELS.items():
        model_path = MODEL_DIR / model_name
        
        # Skip if already exists
        if model_path.exists():
            logger.info(f"⏭️  {model_name} already exists, skipping")
            success_count += 1
            continue
        
        # Try downloading
        url = config.get("url")
        if url:
            if download_from_url(url, model_path):
                success_count += 1
        else:
            logger.warning(f"⚠️  No URL configured for {model_name}")
    
    logger.info(f"Downloaded {success_count}/{len(MODELS)} models")
    return success_count == len(MODELS)


def main():
    """Main entry point."""
    logger.info("=" * 60)
    logger.info("ML Model Download Script")
    logger.info("=" * 60)
    
    # Check if models already exist
    if check_models_exist():
        logger.info("✅ All models already present")
        return 0
    
    # Download missing models
    logger.info("Downloading missing models...")
    if download_all_models():
        logger.info("✅ All models downloaded successfully")
        return 0
    else:
        logger.error("❌ Some models failed to download")
        logger.error("Application may not work correctly")
        return 1


if __name__ == "__main__":
    sys.exit(main())
