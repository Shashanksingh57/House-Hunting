# test_real_data.py
# Test script for real Zillow data using RapidAPI

import os
import requests
import pandas as pd
import json
import random
from dotenv import load_dotenv
import time
from datetime import datetime

# Load environment variables
load_dotenv()

class ZillowRapidAPI:
    """Direct Zillow API integration using RapidAPI"""
    
    def __init__(self):
        self.api_key = os.getenv('RAPIDAPI_KEY')
        self.base_url = "https://zillow-com1.p.rapidapi.com"
        
        if not self.api_key:
            raise ValueError("❌ RAPIDAPI_KEY not found in .env file!")
        
        self.headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": "zillow-com1.p.rapidapi.com"
        }
        
        print(f"✅ API key loaded: {self.api_key[:8]}...")
    
    def test_api_connection(self):
        """Test if API key works"""
        
        print("🧪 Testing API connection...")
        
        url = f"{self.base_url}/propertyExtendedSearch"
        
        params = {
            "location": "Minneapolis, MN",
            "status_type": "ForSale",
            "home_type": "Houses",
            "maxPrice": "350000",
            "minBeds": "3",
            "sortSelection": "priorityscore"
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=15)
            
            print(f"📡 Response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ API connection successful!")
                print(f"📊 Response keys: {list(data.keys())}")
                return data
            
            elif response.status_code == 403:
                print("❌ API key invalid or subscription needed")
                print("💡 Check your RapidAPI subscription status")
                return None
            
            elif response.status_code == 429:
                print("⚠️ Rate limit exceeded - wait and try again")
                return None
            
            else:
                print(f"❌ API error {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Connection error: {e}")
            return None
    
    def search_minneapolis_houses(self, max_price=400000, min_beds=3):
        """Search for houses in Minneapolis area"""
        
        print(f"🏠 Searching Minneapolis houses (${max_price:,} max, {min_beds}+ beds)...")
        
        url = f"{self.base_url}/propertyExtendedSearch"
        
        params = {
            "location": "Minneapolis, MN",
            "status_type": "ForSale", 
            "home_type": "Houses",
            "maxPrice": str(max_price),
            "minBeds": str(min_beds),
            "sortSelection": "priorityscore"
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=20)
            
            if response.status_code == 200:
                data = response.json()
                return self.parse_zillow_response(data)
            else:
                print(f"❌ Search failed: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Search error: {e}")
            return []
    
    def parse_zillow_response(self, data):
        """Parse Zillow API response into house data"""
        
        houses = []
        
        try:
            # Debug: show response structure
            print(f"🔍 API Response keys: {list(data.keys())}")
            
            # Navigate the response structure
            props = data.get('props', [])
            
            if not props:
                # Try alternative response structures
                alternative_keys = ['results', 'properties', 'listings', 'homes']
                for key in alternative_keys:
                    if key in data and data[key]:
                        props = data[key]
                        print(f"🔍 Found properties in '{key}' field")
                        break
            
            if not props:
                print("⚠️ No properties found in response")
                print(f"🔍 Full response structure:")
                print(json.dumps(data, indent=2)[:500] + "..." if len(str(data)) > 500 else json.dumps(data, indent=2))
                return []
            
            print(f"🏠 Processing {len(props)} properties...")
            
            # Debug: show structure of first property
            if props:
                print(f"🔍 First property keys: {list(props[0].keys())}")
                
                # Show coordinate fields specifically
                first_prop = props[0]
                coord_info = {}
                for key, value in first_prop.items():
                    if any(coord_word in key.lower() for coord_word in ['lat', 'lon', 'coord']):
                        coord_info[key] = value
                
                if coord_info:
                    print(f"🗺️ Coordinate fields found: {coord_info}")
                else:
                    print("⚠️ No obvious coordinate fields found")
            
            for i, prop in enumerate(props):
                try:
                    house = self.extract_property_details(prop)
                    if house:
                        houses.append(house)
                        if i < 3:  # Debug first few houses
                            print(f"✅ House {i+1}: {house.get('address', 'No address')[:50]} - Coords: ({house.get('latitude')}, {house.get('longitude')})")
                except Exception as e:
                    print(f"⚠️ Error parsing property {i+1}: {e}")
                    continue
            
            print(f"✅ Successfully parsed {len(houses)} houses")
            return houses
            
        except Exception as e:
            print(f"❌ Response parsing error: {e}")
            return []
    
    def extract_property_details(self, prop):
        """Extract house details from property object"""
        
        try:
            # First, let's see what coordinate fields are available
            lat_fields = ['latitude', 'lat', 'latLong.latitude']
            lon_fields = ['longitude', 'lon', 'lng', 'latLong.longitude']
            
            latitude = None
            longitude = None
            
            # Try different ways to get latitude
            for field in lat_fields:
                if '.' in field:
                    # Handle nested fields like latLong.latitude
                    parts = field.split('.')
                    value = prop
                    for part in parts:
                        value = value.get(part, {}) if isinstance(value, dict) else {}
                    if value and isinstance(value, (int, float)):
                        latitude = float(value)
                        break
                else:
                    value = prop.get(field)
                    if value and isinstance(value, (int, float)):
                        latitude = float(value)
                        break
            
            # Try different ways to get longitude
            for field in lon_fields:
                if '.' in field:
                    parts = field.split('.')
                    value = prop
                    for part in parts:
                        value = value.get(part, {}) if isinstance(value, dict) else {}
                    if value and isinstance(value, (int, float)):
                        longitude = float(value)
                        break
                else:
                    value = prop.get(field)
                    if value and isinstance(value, (int, float)):
                        longitude = float(value)
                        break
            
            # If no coordinates found, try to estimate from address
            if not latitude or not longitude:
                address = prop.get('address', '')
                if address:
                    latitude, longitude = self.estimate_coordinates_from_address(address)
            
            house = {
                'data_source': 'zillow_rapidapi',
                'zpid': prop.get('zpid'),
                'address': prop.get('address'),
                'price': prop.get('price'),
                'bedrooms': prop.get('bedrooms'),
                'bathrooms': prop.get('bathrooms'), 
                'sqft': prop.get('livingArea'),
                'lot_size': prop.get('lotAreaValue'),
                'year_built': prop.get('yearBuilt'),
                'latitude': latitude,
                'longitude': longitude,
                'property_type': prop.get('homeType', 'Single Family'),
                'listing_url': f"https://www.zillow.com{prop.get('detailUrl', '')}",
                'zestimate': prop.get('zestimate'),
                'days_on_market': prop.get('daysOnZillow'),
                'price_change': prop.get('priceChange', 0),
                'listing_status': prop.get('homeStatus'),
                'photos': prop.get('imgSrc', []),
                'last_updated': datetime.now().isoformat()
            }
            
            # Clean and validate data
            house = self.clean_house_data(house)
            
            # More flexible validation - only require price and basic info
            essential_fields = ['price', 'sqft']
            
            if all(house.get(field) is not None and house.get(field) > 0 for field in essential_fields):
                # Add derived fields
                house['price_per_sqft'] = round(house['price'] / house['sqft'], 0) if house['sqft'] > 0 else 0
                house['has_garage'] = 'garage' in str(prop).lower()
                
                # Add neighborhood based on coordinates
                if house['latitude'] and house['longitude']:
                    house['neighborhood'] = self.estimate_neighborhood(house['latitude'], house['longitude'])
                else:
                    house['neighborhood'] = self.estimate_neighborhood_from_address(house.get('address', ''))
                
                return house
            else:
                missing = [f for f in essential_fields if not house.get(f) or house.get(f) <= 0]
                print(f"⚠️ Skipping property - invalid/missing: {missing}")
                return None
                
        except Exception as e:
            print(f"⚠️ Property extraction error: {e}")
            return None
    
    def estimate_coordinates_from_address(self, address):
        """Estimate coordinates based on address string"""
        
        # Minneapolis area neighborhoods with approximate coordinates
        neighborhood_coords = {
            'plymouth': (45.01, -93.45),
            'woodbury': (44.92, -92.96),
            'maple grove': (45.07, -93.46),
            'blaine': (45.16, -93.23),
            'eagan': (44.80, -93.17),
            'roseville': (45.01, -93.16),
            'minnetonka': (44.92, -93.47),
            'burnsville': (44.77, -93.28),
            'eden prairie': (44.85, -93.47),
            'minneapolis': (44.98, -93.27),
            'st paul': (44.95, -93.09),
            'brooklyn park': (45.09, -93.35),
            'coon rapids': (45.12, -93.30)
        }
        
        address_lower = address.lower()
        
        for neighborhood, coords in neighborhood_coords.items():
            if neighborhood in address_lower:
                # Add small random offset for variety
                lat_offset = random.uniform(-0.01, 0.01)
                lon_offset = random.uniform(-0.01, 0.01)
                return coords[0] + lat_offset, coords[1] + lon_offset
        
        # Default to Minneapolis downtown with random offset
        base_lat, base_lon = 44.9778, -93.2650
        lat_offset = random.uniform(-0.1, 0.1)
        lon_offset = random.uniform(-0.1, 0.1)
        return base_lat + lat_offset, base_lon + lon_offset
    
    def estimate_neighborhood_from_address(self, address):
        """Estimate neighborhood from address string"""
        
        neighborhoods = ['Plymouth', 'Woodbury', 'Maple Grove', 'Blaine', 'Eagan', 
                        'Roseville', 'Minnetonka', 'Burnsville', 'Eden Prairie', 'Minneapolis']
        
        address_lower = address.lower()
        
        for neighborhood in neighborhoods:
            if neighborhood.lower() in address_lower:
                return neighborhood
        
        return 'Minneapolis'  # Default
    
    def clean_house_data(self, house):
        """Clean and validate house data"""
        
        # Set defaults for None values
        defaults = {
            'price': 0,
            'bedrooms': 3,
            'bathrooms': 2,
            'sqft': 1200,
            'lot_size': 7000,
            'year_built': 2000,
            'latitude': 44.9778,  # Downtown Minneapolis
            'longitude': -93.2650,
            'days_on_market': 30,
            'price_change': 0,
            'zestimate': 0
        }
        
        # Clean numeric fields
        numeric_fields = ['price', 'bedrooms', 'bathrooms', 'sqft', 'lot_size', 
                         'year_built', 'latitude', 'longitude', 'days_on_market', 
                         'price_change', 'zestimate']
        
        for field in numeric_fields:
            value = house.get(field)
            
            # Handle None, empty string, or invalid values
            if value is None or value == '' or value == 'None':
                if field in defaults:
                    house[field] = defaults[field]
                    print(f"   🔧 Set {field} = {defaults[field]} (was None)")
                else:
                    house[field] = 0
            else:
                try:
                    # Convert to appropriate numeric type
                    if field in ['bedrooms', 'bathrooms']:
                        house[field] = int(float(value)) if value else defaults.get(field, 0)
                    else:
                        house[field] = float(value) if value else defaults.get(field, 0)
                        
                except (ValueError, TypeError):
                    house[field] = defaults.get(field, 0)
                    print(f"   🔧 Set {field} = {defaults[field]} (invalid: {value})")
        
        # Validate ranges
        if house['price'] < 50000 or house['price'] > 2000000:
            house['price'] = 0  # Will be filtered out
        
        if house['sqft'] < 500 or house['sqft'] > 10000:
            house['sqft'] = defaults['sqft']
        
        if house['year_built'] < 1900 or house['year_built'] > 2025:
            house['year_built'] = defaults['year_built']
        
        if house['bedrooms'] < 1 or house['bedrooms'] > 10:
            house['bedrooms'] = defaults['bedrooms']
        
        return house
    
    def estimate_neighborhood(self, lat, lon):
        """Estimate neighborhood based on coordinates"""
        
        # Rough Minneapolis neighborhood mapping
        neighborhoods = {
            'Plymouth': (45.01, -93.45),
            'Woodbury': (44.92, -92.96), 
            'Maple Grove': (45.07, -93.46),
            'Blaine': (45.16, -93.23),
            'Eagan': (44.80, -93.17),
            'Roseville': (45.01, -93.16),
            'Minnetonka': (44.92, -93.47)
        }
        
        min_distance = float('inf')
        closest_neighborhood = 'Minneapolis'
        
        for neighborhood, (n_lat, n_lon) in neighborhoods.items():
            distance = ((lat - n_lat) ** 2 + (lon - n_lon) ** 2) ** 0.5
            if distance < min_distance:
                min_distance = distance
                closest_neighborhood = neighborhood
        
        return closest_neighborhood

def ensure_scoring_compatibility(house):
    """Ensure house data has all fields needed for scoring"""
    
    # Fields the scorer expects
    required_scorer_fields = {
        'price': house.get('price', 0),
        'bedrooms': house.get('bedrooms', 3),
        'bathrooms': house.get('bathrooms', 2),
        'sqft': house.get('sqft', 1200),
        'year_built': house.get('year_built', 2000),
        'latitude': house.get('latitude', 44.9778),
        'longitude': house.get('longitude', -93.2650),
        'has_garage': house.get('has_garage', True),
        'lot_size': house.get('lot_size', 7000),
        'days_on_market': house.get('days_on_market', 30),
        'price_change': house.get('price_change', 0),
        'neighborhood': house.get('neighborhood', 'Minneapolis'),
        'school_rating': house.get('school_rating', 8.0),
        'walk_score': house.get('walk_score', 60),
        'property_type': house.get('property_type', 'Single Family'),
        'address': house.get('address', 'Unknown Address')
    }
    
    # Merge with original house data
    for field, default_value in required_scorer_fields.items():
        if field not in house or house[field] is None:
            house[field] = default_value
    
    # Ensure numeric fields are actually numbers
    numeric_fields = ['price', 'bedrooms', 'bathrooms', 'sqft', 'year_built', 
                     'latitude', 'longitude', 'lot_size', 'days_on_market', 
                     'price_change', 'school_rating', 'walk_score']
    
    for field in numeric_fields:
        try:
            if field in ['bedrooms', 'bathrooms']:
                house[field] = int(float(house[field]))
            else:
                house[field] = float(house[field])
        except (ValueError, TypeError):
            house[field] = required_scorer_fields[field]
    
    return house
    
    def get_property_details(self, zpid):
        """Get detailed info for a specific property"""
        
        url = f"{self.base_url}/propertyDetails"
        
        params = {"zpid": zpid}
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=15)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Details failed for {zpid}: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Details error: {e}")
            return None

def main():
    """Main function to test real data integration"""
    
    print("🏠 REAL ZILLOW DATA TEST")
    print("=" * 30)
    
    # Check .env file
    if not os.path.exists('.env'):
        print("❌ .env file not found!")
        print("💡 Create a .env file with:")
        print("   RAPIDAPI_KEY=your_api_key_here")
        return
    
    try:
        # Initialize API
        zillow = ZillowRapidAPI()
        
        # Test connection
        test_result = zillow.test_api_connection()
        
        if not test_result:
            print("❌ API test failed - check your key and subscription")
            return
        
        # Search for houses
        houses = zillow.search_minneapolis_houses(max_price=400000, min_beds=3)
        
        if houses:
            print(f"\n🎉 SUCCESS! Found {len(houses)} real houses")
            
            # Convert to DataFrame
            df = pd.DataFrame(houses)
            
            # Show sample data
            print(f"\n📋 Sample of real data:")
            sample_cols = ['address', 'price', 'bedrooms', 'sqft', 'neighborhood']
            print(df[sample_cols].head())
            
            # Show statistics
            print(f"\n📊 REAL MARKET STATS:")
            print(f"   Price range: ${df['price'].min():,} - ${df['price'].max():,}")
            print(f"   Avg price: ${df['price'].mean():,.0f}")
            print(f"   Avg sqft: {df['sqft'].mean():.0f}")
            print(f"   Avg price/sqft: ${df['price_per_sqft'].mean():.0f}")
            
            # Save real data
            df.to_csv('real_zillow_data.csv', index=False)
            print(f"\n💾 Real data saved to 'real_zillow_data.csv'")
            
            # Test scoring with real data
            try:
                from all_in_one_house_hunter import AdvancedHouseScorer
                
                print(f"\n🎯 Running AI analysis on REAL data...")
                
                scorer = AdvancedHouseScorer()
                scored_houses = []
                
                for i, house in enumerate(houses):
                    try:
                        # Add any missing fields the scorer expects
                        house = ensure_scoring_compatibility(house)
                        
                        scores = scorer.score_house(house)
                        house_with_scores = {**house, **scores}
                        scored_houses.append(house_with_scores)
                        
                    except Exception as e:
                        print(f"⚠️ Scoring error for house {i+1}: {e}")
                        print(f"   House data: {house.get('address', 'Unknown')}")
                        continue
                
                if scored_houses:
                    scored_df = pd.DataFrame(scored_houses)
                    scored_df = scored_df.sort_values('overall_score', ascending=False)
                    
                    print(f"\n🏆 TOP 3 REAL OPPORTUNITIES:")
                    for idx, house in scored_df.head(3).iterrows():
                        print(f"   🏠 {house['address']}")
                        print(f"      💰 ${house['price']:,} | 🎯 {house['overall_score']:.1%}")
                        print(f"      📊 {house['recommendation']}")
                        print(f"      🔗 {house['listing_url']}")
                        print()
                    
                    # Save scored real data  
                    scored_df.to_csv('real_scored_houses.csv', index=False)
                    print(f"💾 Scored real data saved to 'real_scored_houses.csv'")
                    
                    print(f"\n🚀 NEXT STEPS:")
                    print(f"   1. Update your dashboard: streamlit run live_dashboard.py")
                    print(f"   2. Set up automation: python daily_automation.py")
                    print(f"   3. Check 'real_scored_houses.csv' for full results")
                
            except ImportError:
                print("⚠️ Scoring system not available - install dependencies")
        
        else:
            print("❌ No houses found")
            print("💡 Try adjusting search parameters or check API limits")
    
    except Exception as e:
        print(f"❌ Main error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()