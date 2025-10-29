#!/usr/bin/env python3
"""
NY State Gaming Reports Downloader
Downloads all weekly Excel reports from gaming.ny.gov efficiently using parallel processing.
"""

import asyncio
import aiohttp
import aiofiles
from datetime import datetime
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Report configurations
REPORTS = [
    {
        "name": "Bally Bet",
        "url": "https://gaming.ny.gov/ballybet-weekly-report-excel",
        "filename": "Bally_Bet_Weekly_Report.xlsx"
    },
    {
        "name": "BetMGM",
        "url": "https://gaming.ny.gov/betmgm-weekly-report-excel",
        "filename": "BetMGM_Weekly_Report.xlsx"
    },
    {
        "name": "Caesars Sport Book",
        "url": "https://gaming.ny.gov/caesars-sport-book-weekly-report-excel",
        "filename": "Caesars_Sport_Book_Weekly_Report.xlsx"
    },
    {
        "name": "DraftKings Sport Book",
        "url": "https://gaming.ny.gov/draftkings-sport-book-weekly-report-excel",
        "filename": "DraftKings_Sport_Book_Weekly_Report.xlsx"
    },
    {
        "name": "ESPN Bet (Wynn Interactive)",
        "url": "https://gaming.ny.gov/wynn-interactive-weekly-report-excel",
        "filename": "ESPN_Bet_Wynn_Interactive_Weekly_Report.xlsx"
    },
    {
        "name": "Fanatics",
        "url": "https://gaming.ny.gov/fanatics-weekly-report-excel",
        "filename": "Fanatics_Weekly_Report.xlsx"
    },
    {
        "name": "FanDuel",
        "url": "https://gaming.ny.gov/fanduel-weekly-report-excel",
        "filename": "FanDuel_Weekly_Report.xlsx"
    },
    {
        "name": "Resorts World Bet",
        "url": "https://gaming.ny.gov/resorts-world-bet-weekly-report-excel",
        "filename": "Resorts_World_Bet_Weekly_Report.xlsx"
    },
    {
        "name": "Rush Street Interactive",
        "url": "https://gaming.ny.gov/rush-street-interactive-weekly-report-excel",
        "filename": "Rush_Street_Interactive_Weekly_Report.xlsx"
    }
]

class NYGamingReportsDownloader:
    """Efficient downloader for NY State Gaming reports using async/await."""
    
    def __init__(self, output_dir: str = None):
        """Initialize the downloader with output directory."""
        if output_dir is None:
            today = datetime.now().strftime("%Y-%m-%d")
            output_dir = f"NY_State_Reports_{today}"
        
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.session = None
        
    async def __aenter__(self):
        """Async context manager entry."""
        connector = aiohttp.TCPConnector(limit=100, limit_per_host=10)
        timeout = aiohttp.ClientTimeout(total=300, connect=30)
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def download_single_report(self, report):
        """
        Download a single report asynchronously.
        
        Args:
            report: Dictionary containing name, url, and filename
            
        Returns:
            Tuple of (report_name, success, message)
        """
        try:
            logger.info(f"Starting download: {report['name']}")
            
            async with self.session.get(report['url']) as response:
                if response.status == 200:
                    file_path = self.output_dir / report['filename']
                    
                    async with aiofiles.open(file_path, 'wb') as f:
                        async for chunk in response.content.iter_chunked(8192):
                            await f.write(chunk)
                    
                    file_size = file_path.stat().st_size
                    logger.info(f"✅ Downloaded {report['name']}: {file_size:,} bytes")
                    return report['name'], True, f"Downloaded {file_size:,} bytes"
                else:
                    error_msg = f"HTTP {response.status}: {response.reason}"
                    logger.error(f"❌ Failed to download {report['name']}: {error_msg}")
                    return report['name'], False, error_msg
                    
        except asyncio.TimeoutError:
            error_msg = "Request timeout"
            logger.error(f"❌ Timeout downloading {report['name']}")
            return report['name'], False, error_msg
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            logger.error(f"❌ Failed to download {report['name']}: {error_msg}")
            return report['name'], False, error_msg
    
    async def download_all_reports(self):
        """
        Download all reports concurrently.
        
        Returns:
            Dictionary mapping report names to success status
        """
        logger.info(f"🚀 Starting download of {len(REPORTS)} reports to {self.output_dir}")
        start_time = datetime.now()
        
        # Create all download tasks
        tasks = [self.download_single_report(report) for report in REPORTS]
        
        # Execute all downloads concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        success_count = 0
        failed_reports = []
        
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"❌ Unexpected error: {result}")
                failed_reports.append(f"Unknown error: {result}")
            else:
                name, success, message = result
                if success:
                    success_count += 1
                else:
                    failed_reports.append(f"{name}: {message}")
        
        # Calculate timing
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Summary
        logger.info(f"\n📊 Download Summary:")
        logger.info(f"   ✅ Successful: {success_count}/{len(REPORTS)}")
        logger.info(f"   ❌ Failed: {len(failed_reports)}")
        logger.info(f"   ⏱️  Duration: {duration:.2f} seconds")
        logger.info(f"   📁 Output: {self.output_dir.absolute()}")
        
        if failed_reports:
            logger.error(f"\n❌ Failed downloads:")
            for failure in failed_reports:
                logger.error(f"   • {failure}")
        
        return success_count == len(REPORTS)

async def main():
    """Main function to run the downloader."""
    try:
        async with NYGamingReportsDownloader() as downloader:
            success = await downloader.download_all_reports()
            
            if success:
                logger.info("🎉 All downloads completed successfully!")
                return 0
            else:
                logger.error("💥 Some downloads failed!")
                return 1
                
    except KeyboardInterrupt:
        logger.info("\n🛑 Download interrupted by user")
        return 130
    except Exception as e:
        logger.error(f"💥 Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    import sys
    try:
        import aiohttp
        import aiofiles
    except ImportError as e:
        print("❌ Missing required packages. Please install them:")
        print("   pip install aiohttp aiofiles")
        print(f"   Error: {e}")
        sys.exit(1)
    
    sys.exit(asyncio.run(main()))
