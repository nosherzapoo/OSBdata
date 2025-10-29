#!/usr/bin/env python3
"""
NY State Gaming Reports Data Extractor V2
Simplified and robust extraction from Excel files to CSV.
"""

import pandas as pd
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class NYGamingDataExtractorV2:
    """Simplified extractor for NY State Gaming Excel reports."""
    
    def __init__(self, reports_dir=None):
        """Initialize the extractor.

        If reports_dir is not provided, automatically pick the most recent
        directory matching the pattern NY_State_Reports_*/ in the current
        working directory.
        """
        if reports_dir is None:
            root = Path('.')
            candidates = sorted(
                [p for p in root.glob('NY_State_Reports_*') if p.is_dir()],
                key=lambda p: p.stat().st_mtime,
                reverse=True,
            )
            if not candidates:
                logger.warning("No NY_State_Reports_* directory found; defaulting to current directory")
                self.reports_dir = Path('.')
            else:
                self.reports_dir = candidates[0]
                logger.info(f"Using reports directory: {self.reports_dir}")
        else:
            self.reports_dir = Path(reports_dir)
        self.all_data = []
        
        # Brand mapping from filename to display name
        self.brand_mapping = {
            'Bally_Bet_Weekly_Report.xlsx': 'Bally Bet',
            'BetMGM_Weekly_Report.xlsx': 'BetMGM',
            'Caesars_Sport_Book_Weekly_Report.xlsx': 'Caesars Sport Book',
            'DraftKings_Sport_Book_Weekly_Report.xlsx': 'DraftKings Sport Book',
            'ESPN_Bet_Wynn_Interactive_Weekly_Report.xlsx': 'ESPN Bet',
            'Fanatics_Weekly_Report.xlsx': 'Fanatics',
            'FanDuel_Weekly_Report.xlsx': 'FanDuel',
            'Resorts_World_Bet_Weekly_Report.xlsx': 'Resorts World Bet',
            'Rush_Street_Interactive_Weekly_Report.xlsx': 'Rush Street Interactive'
        }
    
    def extract_data_from_file(self, file_path):
        """Extract data from a single Excel file."""
        brand = self.brand_mapping.get(file_path.name, file_path.stem)
        logger.info(f"Processing {brand}...")
        
        try:
            excel_file = pd.ExcelFile(file_path)
            file_data = []
            
            for sheet_name in excel_file.sheet_names:
                logger.info(f"  Processing sheet: {sheet_name}")
                
                # Read the sheet without headers
                df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
                
                # Find the header row (contains "Week-Ending")
                header_row = None
                for idx, row in df.iterrows():
                    if pd.notna(row.iloc[0]) and 'Week-Ending' in str(row.iloc[0]):
                        header_row = idx
                        break
                
                if header_row is None:
                    logger.warning(f"    No header row found in {sheet_name}")
                    continue
                
                # Extract data starting from the row after header
                data_df = df.iloc[header_row + 1:].copy()
                
                # Clean up empty rows
                data_df = data_df.dropna(how='all')
                
                # Extract data from known columns:
                # Column 0: Date
                # Column 2: Handle  
                # Column 5: GGR
                for idx, row in data_df.iterrows():
                    date_val = row.iloc[0] if len(row) > 0 else None
                    handle_val = row.iloc[2] if len(row) > 2 else None
                    ggr_val = row.iloc[5] if len(row) > 5 else None
                    
                    # Validate data
                    if pd.notna(date_val) and pd.notna(ggr_val):
                        try:
                            # Convert date
                            if isinstance(date_val, str):
                                date_val = pd.to_datetime(date_val)
                            
                            # Convert GGR to float
                            ggr_val = float(ggr_val)
                            
                            # Convert Handle to float if available
                            handle_str = ''
                            if pd.notna(handle_val):
                                try:
                                    handle_float = float(handle_val)
                                    handle_str = str(int(handle_float))
                                except:
                                    handle_str = str(handle_val)
                            
                            # Only include positive GGR values
                            if ggr_val > 0:
                                file_data.append({
                                    'Date': date_val.strftime('%Y-%m-%d'),
                                    'Handle': handle_str,
                                    'GGR': ggr_val,
                                    'Brand': brand
                                })
                        except Exception as e:
                            logger.debug(f"    Skipping row due to error: {e}")
                            continue
                
                logger.info(f"    Extracted {len(file_data)} records from {sheet_name}")
            
            return file_data
            
        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")
            return []
    
    def extract_all_data(self):
        """Extract data from all Excel files."""
        logger.info("🚀 Starting data extraction...")
        
        excel_files = list(self.reports_dir.glob("*.xlsx"))
        # Filter out temporary Excel files
        excel_files = [f for f in excel_files if not f.name.startswith('~$')]
        logger.info(f"Found {len(excel_files)} Excel files")
        
        for file_path in excel_files:
            file_data = self.extract_data_from_file(file_path)
            self.all_data.extend(file_data)
            logger.info(f"  Total records so far: {len(self.all_data)}")
        
        logger.info(f"✅ Extraction complete! Total records: {len(self.all_data)}")
        return self.all_data
    
    def save_to_csv(self, output_file="ny_gaming_data.csv"):
        """Save all extracted data to CSV."""
        if not self.all_data:
            logger.warning("No data to save!")
            return None
        
        df = pd.DataFrame(self.all_data)
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.sort_values(['Date', 'Brand'])
        
        output_path = Path(output_file)
        df.to_csv(output_path, index=False)
        
        logger.info(f"💾 Data saved: {len(df)} records, {df['Brand'].nunique()} brands")
        return output_path

def main():
    """Main function to run the extraction."""
    try:
        extractor = NYGamingDataExtractorV2()
        
        # Extract all data
        extractor.extract_all_data()
        
        # Save to CSV
        output_file = extractor.save_to_csv()
        
        if output_file:
            print(f"\n🎉 Data extraction complete!")
            print(f"📁 Output file: {output_file.absolute()}")
        else:
            print("❌ No data extracted!")
            return 1
        
    except Exception as e:
        logger.error(f"💥 Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
