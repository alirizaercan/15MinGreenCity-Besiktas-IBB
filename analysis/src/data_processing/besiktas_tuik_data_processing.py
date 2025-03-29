import pandas as pd
import os
from pathlib import Path

def setup_directories():
    """Create necessary directories if they don't exist"""
    os.makedirs("data/processed", exist_ok=True)

def process_besiktas_district_data():
    """Process Beşiktaş district population data"""
    try:
        print("Processing Beşiktaş district population data...")
        
        # Read the district data with correct column handling
        district_df = pd.read_excel(
            "data/processed/besiktas_population_by_district.xlsx",
            sheet_name="Sheet1",
            header=0
        )
        
        # Handle columns - the file has 5 columns but we need to name them properly
        if len(district_df.columns) == 5:
            district_df.columns = [
                'district',
                'total_population',
                'urban_population',
                'rural_population',
                'annual_growth_rate'
            ]
        else:
            # If column count doesn't match, take only the columns we need
            district_df = district_df.iloc[:, :5]
            district_df.columns = [
                'district',
                'total_population',
                'urban_population',
                'rural_population',
                'annual_growth_rate'
            ]
        
        # Filter for Beşiktaş
        besiktas_data = district_df[district_df['district'].str.contains('Beşiktaş', na=False, case=False)]
        
        # Create metadata
        metadata = {
            "description": "Beşiktaş district population data (2024)",
            "source": "TÜİK (Turkish Statistical Institute)",
            "columns": {
                "district": "District name",
                "total_population": "Total population count",
                "urban_population": "Urban population count",
                "rural_population": "Rural population count",
                "annual_growth_rate": "Annual population growth rate (‰)"
            },
            "note": "Negative growth rate indicates population decrease"
        }
        
        # Save processed data
        with pd.ExcelWriter("data/processed/besiktas_district_population_processed.xlsx") as writer:
            besiktas_data.to_excel(writer, sheet_name="Population Data", index=False)
            pd.DataFrame.from_dict(metadata, orient='index').to_excel(
                writer, sheet_name="README", header=False)
            
        print("Successfully processed Beşiktaş district population data")
        
    except Exception as e:
        print(f"Error processing district population data: {e}")

def process_nationwide_age_gender_data():
    """Process nationwide population data by age and gender"""
    try:
        print("Processing nationwide age/gender population data...")
        
        # Read the Excel file with proper handling
        df = pd.read_excel(
            "data/processed/besiktas_population_age_gender.xlsx",
            sheet_name="Population Data",
            header=5  # Skip the metadata rows
        )
        
        # Take only the columns we need (first 11 columns)
        df = df.iloc[:, :11]
        
        # Clean up column names
        df.columns = [
            'Year',
            'Age Group',
            'Total Population',
            'Male',
            'Female',
            'Urban Total',
            'Urban Male',
            'Urban Female',
            'Rural Total',
            'Rural Male',
            'Rural Female'
        ]
        
        # Convert Year column - handle potential non-date values
        df['Year'] = pd.to_datetime(df['Year'], errors='coerce').dt.year
        df = df.dropna(subset=['Year'])  # Remove rows where Year couldn't be parsed
        
        # Filter out summary rows
        df = df[df['Age Group'] != 'Toplam-Total']
        
        # Create age group bins
        age_bins = [0, 4, 9, 14, 19, 24, 29, 34, 39, 44, 49, 54, 59, 64, 69, 74, 79, 84, 89, 120]
        age_labels = ['0-4', '5-9', '10-14', '15-19', '20-24', '25-29', '30-34', 
                     '35-39', '40-44', '45-49', '50-54', '55-59', '60-64', 
                     '65-69', '70-74', '75-79', '80-84', '85-89', '90+']
        
        # Extract numeric age
        df['Age'] = df['Age Group'].str.extract('(\d+)').astype(float)
        df['Age Group'] = pd.cut(df['Age'], bins=age_bins, labels=age_labels, right=False)
        df = df.drop(columns=['Age'])
        
        # Create metadata
        metadata = {
            "description": "Nationwide population data by age and gender (2007-2024)",
            "source": "TÜİK (Turkish Statistical Institute)",
            "note": "This is nationwide data, not specific to Beşiktaş",
            "processing_steps": [
                "Skipped metadata rows",
                "Standardized column names",
                "Converted Year to proper format",
                "Created consistent age groups",
                "Removed summary rows"
            ]
        }
        
        # Save processed data
        with pd.ExcelWriter("data/processed/nationwide_population_age_gender_processed.xlsx") as writer:
            df.to_excel(writer, sheet_name="Population Data", index=False)
            pd.DataFrame.from_dict(metadata, orient='index').to_excel(
                writer, sheet_name="README", header=False)
            
        print("Successfully processed nationwide population data")
        
    except Exception as e:
        print(f"Error processing population data: {e}")

def main():
    print("Starting data processing pipeline...")
    setup_directories()
    
    # Process both datasets
    process_besiktas_district_data()
    process_nationwide_age_gender_data()
    
    print("All processing completed!")

if __name__ == "__main__":
    main()