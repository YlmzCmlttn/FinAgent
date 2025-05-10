import os
from datetime import datetime
import cloudscraper
import logging
import time
from typing import List, Optional
from pathlib import Path
import random

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class FinancialStatementDownloader:
    def __init__(self, output_dir: str = "output", max_retries: int = 3, base_delay: float = 2.0):
        self.output_dir = Path(output_dir)
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.scraper = None
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def _create_scraper(self) -> None:
        """Create a new cloudscraper session with random browser settings"""
        if self.scraper is None:
            browsers = ['chrome', 'firefox', 'safari']
            platforms = ['windows', 'darwin', 'linux']
            
            self.scraper = cloudscraper.create_scraper(
                browser={
                    'browser': random.choice(browsers),
                    'platform': random.choice(platforms),
                    'desktop': True
                }
            )
            logger.info("Created new cloudscraper session")
    
    def _get_exponential_backoff(self, attempt: int) -> float:
        """Calculate exponential backoff with jitter"""
        jitter = random.uniform(0, 0.1 * self.base_delay)
        return min(300, self.base_delay * (2 ** attempt) + jitter)
    
    def _download_with_retry(self, stock_code: str) -> bool:
        """Download financial statements with retry logic"""
        for attempt in range(self.max_retries):
            try:
                if attempt > 0:
                    delay = self._get_exponential_backoff(attempt)
                    logger.info(f"Retry attempt {attempt + 1}/{self.max_retries} after {delay:.2f}s delay")
                    time.sleep(delay)
                    self._create_scraper()  # Create new session for retry
                
                # Construct URLs
                main_url = f"https://fintables.com/sirketler/{stock_code}/finansal-tablolar"
                excel_url = f"{main_url}/excel?currency="
                
                # Visit main page first
                logger.info(f"Visiting main page for {stock_code}")
                self.scraper.get(main_url)
                time.sleep(random.uniform(2, 4))  # Random delay between requests
                
                # Download Excel file
                logger.info(f"Downloading Excel file for {stock_code}")
                response = self.scraper.get(excel_url)
                
                if response.status_code == 200 and response.headers.get('content-type', '').startswith('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'):
                    filename = self.output_dir / f"{stock_code}.xlsx"
                    with open(filename, 'wb') as f:
                        f.write(response.content)
                    logger.info(f"Successfully downloaded {stock_code} to {filename}")
                    return True
                else:
                    logger.warning(f"Invalid response for {stock_code}: Status {response.status_code}, Content-Type: {response.headers.get('content-type')}")
                    
            except Exception as e:
                logger.error(f"Error downloading {stock_code} (attempt {attempt + 1}): {str(e)}")
                
        return False
    
    def download_all(self, stock_codes: List[str]) -> dict:
        """Download financial statements for multiple stock codes"""
        results = {
            'successful': [],
            'failed': [],
            'total': len(stock_codes)
        }
        
        self._create_scraper()
        
        for index, stock_code in enumerate(stock_codes, 1):
            stock_code = stock_code.strip()
            if not stock_code:
                continue
                
            logger.info(f"Processing {stock_code} ({index}/{len(stock_codes)})")
            
            if self._download_with_retry(stock_code):
                results['successful'].append(stock_code)
            else:
                results['failed'].append(stock_code)
            
            # Add random delay between companies
            if index < len(stock_codes):
                delay = random.uniform(3, 5)
                time.sleep(delay)
            
            # Show progress
            progress = (index / len(stock_codes)) * 100
            logger.info(f"Progress: {progress:.2f}%")
        
        return results

def main():
    # Read stock codes
    try:
        with open("stock_codes.txt", "r") as f:
            stock_codes = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        logger.error("stock_codes.txt file not found")
        return
    except Exception as e:
        logger.error(f"Error reading stock_codes.txt: {str(e)}")
        return
    
    if not stock_codes:
        logger.error("No stock codes found in stock_codes.txt")
        return
    
    # Initialize downloader and start downloading
    downloader = FinancialStatementDownloader()
    results = downloader.download_all(stock_codes)
    
    # Print summary
    logger.info("\nDownload Summary:")
    logger.info(f"Total companies: {results['total']}")
    logger.info(f"Successfully downloaded: {len(results['successful'])}")
    logger.info(f"Failed downloads: {len(results['failed'])}")
    
    if results['failed']:
        logger.info("\nFailed downloads:")
        for code in results['failed']:
            logger.info(f"- {code}")

if __name__ == "__main__":
    main()

