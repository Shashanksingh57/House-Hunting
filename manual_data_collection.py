# manual_data_collection.py
import pandas as pd
import requests
from geopy.distance import geodesic
import time

def create_sample_dataset():
    """
    Start by manually collecting 10-20 houses from Zillow to test the system
    This gives you immediate results while you build automation
    """
    
    # You'll manually copy this data from Zillow searches
    sample_houses = [
        {
            'address': '123 Example St, Plymouth, MN 55447',
            'price': 349000,
            'sqft': 1450,
            'bedrooms': 3,
            'bathrooms': 2,
            'year_built': 2012,
            'latitude': 45.0105,
            'longitude': -93.4555,
            'zpid': '12345',
            'listing_url': 'https://zillow.com/homedetails/12345',
            'days_on_market': 12,
            'lot_size': 8000,
            'has_garage': True,
            'garage_spaces': 2,
            'description': 'Updated kitchen, hardwood floors...'
        },
        # Add more houses here as you find them
    ]
    
    return pd.DataFrame(sample_houses)

def add_basic_calculations(df):
    """Add calculated fields we can compute immediately"""
    
    downtown_minneapolis = (44.9778, -93.2650)
    
    for idx, row in df.iterrows():
        house_location = (row['latitude'], row['longitude'])
        
        # Calculate distance to downtown
        distance_miles = geodesic(house_location, downtown_minneapolis).miles
        df.at[idx, 'distance_to_downtown'] = round(distance_miles, 1)
        
        # Estimate commute time (rough: 2 miles per minute in suburbs)
        df.at[idx, 'estimated_commute_minutes'] = round(distance_miles * 2, 0)
        
        # Price per sqft
        df.at[idx, 'price_per_sqft'] = round(row['price'] / row['sqft'], 0)
        
        # House age
        df.at[idx, 'house_age'] = 2025 - row['year_built']
    
    return df

if __name__ == "__main__":
    # Create sample dataset
    df = create_sample_dataset()
    df = add_basic_calculations(df)
    
    # Save to CSV
    df.to_csv('sample_houses.csv', index=False)
    print(f"Created sample dataset with {len(df)} houses")
    print(df[['address', 'price', 'estimated_commute_minutes', 'price_per_sqft']].head())