# comprehensive_data_collector.py
# Fixed version with proper data validation

import time
import pandas as pd
import os
import requests
import json
import random
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ZillowDataCollector:
    """Fixed Zillow data collector with better error handling"""
    
    def __init__(self):
        self.api_key = os.getenv('RAPIDAPI_KEY')
        self.base_url = "https://zillow-com1.p.rapidapi.com"
        
        if not self.api_key:
            print("❌ RAPIDAPI_KEY not found in .env file!")
            return
        
        self.headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": "zillow-com1.p.rapidapi.com"
        }
        
        print(f"✅ API key loaded: {self.api_key[:8]}...")
    
    def search_minneapolis_houses(self, max_price=400000, min_beds=3):
        """Search for houses with better error handling"""
        
        print(f"🏠 Searching houses (${max_price:,} max, {min_beds}+ beds)...")
        
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
        """Parse response with better validation"""
        
        houses = []
        
        try:
            props = data.get('props', [])
            
            if not props:
                for key in ['results', 'properties', 'listings', 'homes']:
                    if key in data and data[key]:
                        props = data[key]
                        break
            
            if not props:
                print("⚠️ No properties found in response")
                return []
            
            print(f"🏠 Processing {len(props)} properties...")
            
            for i, prop in enumerate(props):
                try:
                    house = self.extract_property_details(prop)
                    if house:
                        houses.append(house)
                except Exception as e:
                    print(f"⚠️ Error parsing property {i+1}: {e}")
                    continue
            
            print(f"✅ Successfully parsed {len(houses)} houses")
            return houses
            
        except Exception as e:
            print(f"❌ Response parsing error: {e}")
            return []
    
    def extract_property_details(self, prop):
        """Extract house details with proper validation"""
        
        try:
            # Get coordinates with fallback
            latitude = self.safe_get_number(prop, ['latitude', 'lat'])
            longitude = self.safe_get_number(prop, ['longitude', 'lon', 'lng'])
            
            # If no coordinates, estimate from address
            if not latitude or not longitude:
                address = prop.get('address', '')
                latitude, longitude = self.estimate_coordinates(address)
            
            house = {
                'data_source': 'zillow_rapidapi',
                'zpid': prop.get('zpid'),
                'address': prop.get('address', 'Unknown Address'),
                'price': self.safe_get_number(prop, ['price'], 0),
                'bedrooms': self.safe_get_number(prop, ['bedrooms'], 3),
                'bathrooms': self.safe_get_number(prop, ['bathrooms'], 2),
                'sqft': self.safe_get_number(prop, ['livingArea'], 1200),
                'lot_size': self.safe_get_number(prop, ['lotAreaValue'], 7000),
                'year_built': self.safe_get_number(prop, ['yearBuilt'], 2000),
                'latitude': latitude or 44.9778,
                'longitude': longitude or -93.2650,
                'property_type': prop.get('homeType', 'Single Family'),
                'listing_url': f"https://www.zillow.com{prop.get('detailUrl', '')}",
                'zestimate': self.safe_get_number(prop, ['zestimate'], 0),
                'days_on_market': self.safe_get_number(prop, ['daysOnZillow'], 30),
                'price_change': self.safe_get_number(prop, ['priceChange'], 0),
                'listing_status': prop.get('homeStatus', 'For Sale'),
                'photos': prop.get('imgSrc', []),
                'last_updated': datetime.now().isoformat()
            }
            
            # Add calculated fields
            if house['price'] and house['sqft'] and house['sqft'] > 0:
                house['price_per_sqft'] = round(house['price'] / house['sqft'], 0)
            else:
                house['price_per_sqft'] = 0
            
            house['has_garage'] = 'garage' in str(prop).lower()
            house['neighborhood'] = self.estimate_neighborhood_from_address(house['address'])
            
            # Validate essential fields before returning
            if self.validate_house_data(house):
                return house
            else:
                return None
                
        except Exception as e:
            print(f"⚠️ Property extraction error: {e}")
            return None
    
    def safe_get_number(self, data, field_names, default=None):
        """Safely get numeric value from various field names"""
        
        for field in field_names:
            value = data.get(field)
            if value is not None:
                try:
                    # Handle string numbers
                    if isinstance(value, str):
                        # Remove commas and dollar signs
                        cleaned = value.replace(',', '').replace('$', '').strip()
                        if cleaned:
                            return float(cleaned)
                    elif isinstance(value, (int, float)):
                        return float(value)
                except (ValueError, TypeError):
                    continue
        
        return default
    
    def validate_house_data(self, house):
        """Validate house data before scoring"""
        
        # Check essential fields
        required_fields = {
            'price': (50000, 2000000),      # Reasonable price range
            'bedrooms': (1, 10),            # Reasonable bedroom count
            'bathrooms': (1, 10),           # Reasonable bathroom count  
            'sqft': (500, 10000),           # Reasonable square footage
            'year_built': (1900, 2025),     # Reasonable year range
            'latitude': (44, 46),           # Minneapolis area latitude
            'longitude': (-95, -92)         # Minneapolis area longitude
        }
        
        for field, (min_val, max_val) in required_fields.items():
            value = house.get(field)
            
            # Check if value exists and is reasonable
            if value is None:
                return False
            
            try:
                num_value = float(value)
                if not (min_val <= num_value <= max_val):
                    return False
            except (ValueError, TypeError):
                return False
        
        return True
    
    def estimate_coordinates(self, address):
        """Estimate coordinates from address"""
        
        neighborhoods = {
            'plymouth': (45.01, -93.45),
            'woodbury': (44.92, -92.96),
            'maple grove': (45.07, -93.46),
            'blaine': (45.16, -93.23),
            'eagan': (44.80, -93.17),
            'roseville': (45.01, -93.16),
            'minnetonka': (44.92, -93.47),
            'minneapolis': (44.98, -93.27)
        }
        
        if address:
            address_lower = address.lower()
            for name, coords in neighborhoods.items():
                if name in address_lower:
                    return coords[0] + random.uniform(-0.01, 0.01), coords[1] + random.uniform(-0.01, 0.01)
        
        # Default to Minneapolis
        return 44.9778 + random.uniform(-0.1, 0.1), -93.2650 + random.uniform(-0.1, 0.1)
    
    def estimate_neighborhood_from_address(self, address):
        """Estimate neighborhood from address"""
        
        if not address:
            return 'Minneapolis'
        
        neighborhoods = ['Plymouth', 'Woodbury', 'Maple Grove', 'Blaine', 'Eagan', 'Roseville', 'Minnetonka']
        address_lower = address.lower()
        
        for neighborhood in neighborhoods:
            if neighborhood.lower() in address_lower:
                return neighborhood
        
        return 'Minneapolis'

class AdvancedHouseScorer:
    """Fixed house scorer with proper validation"""
    
    def __init__(self):
        self.preferences = {
            'max_budget': 400000,
            'max_commute_minutes': 30,
            'min_bedrooms': 3,
            'min_sqft': 1200,
            'min_year_built': 2000,
            'needs_garage': True
        }
        
        self.weights = {
            'price': 0.25,
            'commute': 0.20,
            'size': 0.15,
            'age': 0.15,
            'location': 0.15,
            'market': 0.10
        }
        
        self.downtown_minneapolis = (44.9778, -93.2650)
    
    def score_house(self, house):
        """Score house with proper validation"""
        
        try:
            # Validate and clean house data first
            cleaned_house = self.ensure_scoring_compatibility(house)
            
            # Calculate individual scores
            price_score = self.calculate_price_score(cleaned_house['price'])
            commute_score = self.calculate_commute_score(cleaned_house['latitude'], cleaned_house['longitude'])
            size_score = self.calculate_size_score(cleaned_house['sqft'])
            age_score = self.calculate_age_score(cleaned_house['year_built'])
            location_score = self.calculate_location_score(cleaned_house['neighborhood'])
            market_score = self.calculate_market_score(cleaned_house['days_on_market'], cleaned_house['price_change'])
            
            # Calculate weighted overall score
            overall_score = (
                price_score * self.weights['price'] +
                commute_score * self.weights['commute'] +
                size_score * self.weights['size'] +
                age_score * self.weights['age'] +
                location_score * self.weights['location'] +
                market_score * self.weights['market']
            )
            
            # Check requirements
            meets_requirements = (
                cleaned_house['price'] <= self.preferences['max_budget'] and
                cleaned_house['bedrooms'] >= self.preferences['min_bedrooms'] and
                cleaned_house['sqft'] >= self.preferences['min_sqft'] and
                cleaned_house['year_built'] >= self.preferences['min_year_built'] and
                (not self.preferences['needs_garage'] or cleaned_house['has_garage'])
            )
            
            return {
                'overall_score': round(overall_score, 3),
                'price_score': round(price_score, 3),
                'commute_score': round(commute_score, 3),
                'size_score': round(size_score, 3),
                'age_score': round(age_score, 3),
                'location_score': round(location_score, 3),
                'market_score': round(market_score, 3),
                'meets_requirements': meets_requirements,
                'recommendation': self.get_recommendation(overall_score, meets_requirements)
            }
            
        except Exception as e:
            print(f"Scoring error: {e}")
            return {
                'overall_score': 0,
                'price_score': 0,
                'commute_score': 0,
                'size_score': 0,
                'age_score': 0,
                'location_score': 0,
                'market_score': 0,
                'meets_requirements': False,
                'recommendation': "❌ Scoring failed"
            }
    
    def ensure_scoring_compatibility(self, house):
        """Ensure house has all required fields with valid values"""
        
        # Default values for missing or invalid data
        defaults = {
            'price': 350000,
            'bedrooms': 3,
            'bathrooms': 2,
            'sqft': 1500,
            'year_built': 2010,
            'latitude': 44.9778,
            'longitude': -93.2650,
            'has_garage': True,
            'lot_size': 7000,
            'days_on_market': 30,
            'price_change': 0,
            'neighborhood': 'Minneapolis',
            'school_rating': 8.0,
            'walk_score': 60,
            'property_type': 'Single Family',
            'address': 'Unknown Address'
        }
        
        cleaned_house = {}
        
        for field, default_value in defaults.items():
            value = house.get(field)
            
            # Handle None or invalid values
            if value is None or value == '' or str(value).lower() == 'none':
                cleaned_house[field] = default_value
            else:
                # Try to convert numeric fields
                if field in ['price', 'bedrooms', 'bathrooms', 'sqft', 'year_built', 
                           'latitude', 'longitude', 'lot_size', 'days_on_market', 
                           'price_change', 'school_rating', 'walk_score']:
                    try:
                        if field in ['bedrooms', 'bathrooms']:
                            cleaned_house[field] = int(float(value))
                        else:
                            cleaned_house[field] = float(value)
                    except (ValueError, TypeError):
                        cleaned_house[field] = default_value
                elif field == 'has_garage':
                    cleaned_house[field] = bool(value) if isinstance(value, bool) else default_value
                else:
                    cleaned_house[field] = str(value) if value else default_value
        
        # Validate ranges
        if cleaned_house['price'] < 50000 or cleaned_house['price'] > 2000000:
            cleaned_house['price'] = defaults['price']
        
        if cleaned_house['sqft'] < 500 or cleaned_house['sqft'] > 10000:
            cleaned_house['sqft'] = defaults['sqft']
        
        if cleaned_house['year_built'] < 1900 or cleaned_house['year_built'] > 2025:
            cleaned_house['year_built'] = defaults['year_built']
        
        return cleaned_house
    
    def calculate_price_score(self, price):
        """Calculate price score"""
        if price <= self.preferences['max_budget']:
            return 1.0 - (price / self.preferences['max_budget']) * 0.4
        else:
            return max(0, 1.0 - (price - self.preferences['max_budget']) / self.preferences['max_budget'])
    
    def calculate_commute_score(self, lat, lon):
        """Calculate commute score"""
        try:
            from geopy.distance import geodesic
            distance = geodesic((lat, lon), self.downtown_minneapolis).miles
        except:
            # Fallback distance calculation
            lat_diff = lat - self.downtown_minneapolis[0]
            lon_diff = lon - self.downtown_minneapolis[1]
            distance = (lat_diff**2 + lon_diff**2)**0.5 * 69  # Rough miles
        
        commute_minutes = distance * 2
        
        if commute_minutes <= self.preferences['max_commute_minutes']:
            return 1.0 - (commute_minutes / self.preferences['max_commute_minutes']) * 0.6
        else:
            return 0.2
    
    def calculate_size_score(self, sqft):
        """Calculate size score"""
        if sqft >= self.preferences['min_sqft']:
            bonus = (sqft - self.preferences['min_sqft']) / self.preferences['min_sqft']
            return min(1.0, 0.7 + bonus * 0.3)
        else:
            return sqft / self.preferences['min_sqft']
    
    def calculate_age_score(self, year_built):
        """Calculate age score"""
        if year_built >= self.preferences['min_year_built']:
            years_newer = year_built - self.preferences['min_year_built']
            return min(1.0, 0.8 + years_newer * 0.01)
        else:
            age_penalty = (self.preferences['min_year_built'] - year_built) / 25
            return max(0.2, 1.0 - age_penalty)
    
    def calculate_location_score(self, neighborhood):
        """Calculate location score"""
        premium_areas = ['Plymouth', 'Maple Grove', 'Woodbury', 'Eden Prairie', 'Minnetonka']
        return 0.9 if neighborhood in premium_areas else 0.7
    
    def calculate_market_score(self, days_on_market, price_change):
        """Calculate market score"""
        if days_on_market < 7:
            dom_score = 1.0
        elif days_on_market < 21:
            dom_score = 0.8
        else:
            dom_score = 0.6
        
        if price_change < 0:
            change_score = 1.0  # Price reduction is good
        else:
            change_score = 0.8
        
        return (dom_score + change_score) / 2
    
    def get_recommendation(self, score, meets_requirements):
        """Get recommendation based on score"""
        if not meets_requirements:
            return "❌ SKIP - Doesn't meet requirements"
        elif score >= 0.85:
            return "🔥 MUST SEE - Exceptional match!"
        elif score >= 0.75:
            return "⭐ HIGHLY RECOMMENDED"
        elif score >= 0.65:
            return "✅ GOOD OPTION"
        else:
            return "⚠️ BELOW THRESHOLD"

def get_comprehensive_data():
    """Get comprehensive data from multiple searches with error handling"""
    
    print("🔍 Starting comprehensive data collection...")
    
    if not os.getenv('RAPIDAPI_KEY'):
        print("❌ No RAPIDAPI_KEY found in .env file")
        return None
    
    zillow = ZillowDataCollector()
    all_houses = []
    
    # Search multiple areas and price ranges
    search_configs = [
        {"max_price": 350000, "min_beds": 3},
        {"max_price": 400000, "min_beds": 3},
        {"max_price": 450000, "min_beds": 3},
        {"max_price": 400000, "min_beds": 4},
    ]
    
    for i, config in enumerate(search_configs):
        print(f"\n📡 Search {i+1}/{len(search_configs)}: ${config['max_price']:,}, {config['min_beds']}+ beds")
        
        try:
            houses = zillow.search_minneapolis_houses(
                max_price=config['max_price'],
                min_beds=config['min_beds']
            )
            
            if houses:
                print(f"   ✅ Found {len(houses)} houses")
                all_houses.extend(houses)
            else:
                print(f"   ⚠️ No houses found")
            
            # Rate limiting
            time.sleep(3)
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            continue
    
    if not all_houses:
        print("❌ No houses collected")
        return None
    
    # Remove duplicates based on zpid
    df = pd.DataFrame(all_houses)
    df = df.drop_duplicates(subset=['zpid'], keep='first')
    
    print(f"\n🎯 Total unique houses collected: {len(df)}")
    
    # Score all houses with error handling
    scorer = AdvancedHouseScorer()
    scored_houses = []
    
    print("🎯 Scoring all houses...")
    
    for i, house in enumerate(df.to_dict('records')):
        try:
            scores = scorer.score_house(house)
            house_with_scores = {**house, **scores}
            scored_houses.append(house_with_scores)
            
            if i % 10 == 0:  # Progress update every 10 houses
                print(f"   Scored {i+1}/{len(df)} houses...")
                
        except Exception as e:
            print(f"⚠️ Scoring error for house {i+1}: {e}")
            # Add house without scores
            house['overall_score'] = 0
            house['meets_requirements'] = False
            house['recommendation'] = "❌ Scoring failed"
            scored_houses.append(house)
            continue
    
    # Save comprehensive data
    if scored_houses:
        comprehensive_df = pd.DataFrame(scored_houses)
        comprehensive_df = comprehensive_df.sort_values('overall_score', ascending=False)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        filename = f'comprehensive_houses_{timestamp}.csv'
        comprehensive_df.to_csv(filename, index=False)
        
        print(f"\n💾 Saved {len(comprehensive_df)} scored houses to {filename}")
        
        # Show top opportunities
        viable_houses = comprehensive_df[comprehensive_df['meets_requirements'] == True]
        
        if len(viable_houses) > 0:
            print(f"\n🏆 TOP 5 OPPORTUNITIES:")
            for idx, house in viable_houses.head(5).iterrows():
                print(f"   {idx+1}. {house['address']}")
                print(f"      💰 ${house['price']:,} | 🎯 {house['overall_score']:.1%}")
        else:
            print(f"\n⚠️ No houses meet all requirements")
            print(f"📊 Total houses: {len(comprehensive_df)}")
            print(f"📊 Average score: {comprehensive_df['overall_score'].mean():.1%}")
        
        return comprehensive_df
    
    return None

if __name__ == "__main__":
    result = get_comprehensive_data()
    if result is not None:
        print(f"\n🎉 Success! Check your dashboard for {len(result)} houses")
        print(f"🚀 Run: streamlit run zillow_data_analytics_dashboard.py")
    else:
        print("\n❌ No data collected - check API key and connection")