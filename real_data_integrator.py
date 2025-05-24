# real_data_integrator.py
# Integration with real estate APIs and web scraping

import requests
import pandas as pd
import time
import json
from datetime import datetime, timedelta
import os
from typing import List, Dict, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class RealEstateDataIntegrator:
    """Integrate with multiple real estate data sources"""
    
    def __init__(self):
        self.apis = {
            'rapidapi_key': os.getenv('RAPIDAPI_KEY'),
            'rentspree_key': os.getenv('RENTSPREE_KEY'),
            'realty_mole_key': os.getenv('REALTY_MOLE_KEY')
        }
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; HouseHunter/1.0)'
        })
    
    def get_zillow_rentals_api(self, location: str = "Minneapolis, MN") -> List[Dict]:
        """
        Get data using RentSpree API (has free tier)
        Sign up at: https://www.rentspree.com/api
        """
        
        if not self.apis['rentspree_key']:
            print("ℹ️ RentSpree API key not configured")
            return []
        
        url = "https://api.rentspree.com/v1/listings"
        params = {
            'city': 'Minneapolis',
            'state': 'MN',
            'property_type': 'house',
            'status': 'for_sale',
            'limit': 50
        }
        
        headers = {
            'Authorization': f'Bearer {self.apis["rentspree_key"]}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = self.session.get(url, params=params, headers=headers, timeout=15)
            if response.status_code == 200:
                data = response.json()
                return self.parse_rentspree_data(data)
            else:
                print(f"❌ RentSpree API error: {response.status_code}")
        except Exception as e:
            print(f"❌ RentSpree API exception: {e}")
        
        return []
    
    def get_rapidapi_zillow(self, location: str = "Minneapolis, MN") -> List[Dict]:
        """
        Use RapidAPI Zillow endpoints
        Sign up at: https://rapidapi.com/apimaker/api/zillow-com1/
        """
        
        if not self.apis['rapidapi_key']:
            print("ℹ️ RapidAPI key not configured")
            return []
        
        url = "https://zillow-com1.p.rapidapi.com/propertyExtendedSearch"
        
        querystring = {
            "location": location,
            "status_type": "ForSale",
            "home_type": "Houses",
            "maxPrice": "500000",
            "minBeds": "3",
            "sortSelection": "priorityscore"
        }
        
        headers = {
            "X-RapidAPI-Key": self.apis['rapidapi_key'],
            "X-RapidAPI-Host": "zillow-com1.p.rapidapi.com"
        }
        
        try:
            response = requests.get(url, headers=headers, params=querystring, timeout=15)
            if response.status_code == 200:
                data = response.json()
                return self.parse_rapidapi_data(data)
            else:
                print(f"❌ RapidAPI error: {response.status_code}")
        except Exception as e:
            print(f"❌ RapidAPI exception: {e}")
        
        return []
    
    def get_realty_mole_data(self, address_list: List[str]) -> List[Dict]:
        """
        Get property details using Realty Mole API
        Good for enriching existing data with details
        """
        
        if not self.apis['realty_mole_key']:
            print("ℹ️ Realty Mole API key not configured")
            return []
        
        enriched_houses = []
        
        for address in address_list[:10]:  # Limit to avoid rate limits
            url = "https://realty-mole-property-api.p.rapidapi.com/properties"
            
            querystring = {"address": address}
            
            headers = {
                "X-RapidAPI-Key": self.apis['realty_mole_key'],
                "X-RapidAPI-Host": "realty-mole-property-api.p.rapidapi.com"
            }
            
            try:
                response = requests.get(url, headers=headers, params=querystring, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    enriched_houses.append(self.parse_realty_mole_data(data))
                
                time.sleep(1)  # Rate limiting
                
            except Exception as e:
                print(f"⚠️ Error enriching {address}: {e}")
                continue
        
        return enriched_houses
    
    def parse_rentspree_data(self, data: Dict) -> List[Dict]:
        """Parse RentSpree API response"""
        houses = []
        
        try:
            listings = data.get('listings', [])
            
            for listing in listings:
                house = {
                    'api_source': 'rentspree',
                    'external_id': listing.get('id'),
                    'address': listing.get('address', {}).get('full_address'),
                    'price': listing.get('price'),
                    'bedrooms': listing.get('bedrooms'),
                    'bathrooms': listing.get('bathrooms'),
                    'sqft': listing.get('square_feet'),
                    'year_built': listing.get('year_built'),
                    'latitude': listing.get('address', {}).get('latitude'),
                    'longitude': listing.get('address', {}).get('longitude'),
                    'property_type': listing.get('property_type'),
                    'listing_url': listing.get('listing_url'),
                    'photos': listing.get('photos', []),
                    'description': listing.get('description'),
                    'days_on_market': listing.get('days_on_market'),
                    'listing_agent': listing.get('agent', {}).get('name'),
                    'last_updated': datetime.now().isoformat()
                }
                
                if self.is_valid_house(house):
                    houses.append(house)
                    
        except Exception as e:
            print(f"⚠️ Error parsing RentSpree data: {e}")
        
        return houses
    
    def parse_rapidapi_data(self, data: Dict) -> List[Dict]:
        """Parse RapidAPI Zillow response"""
        houses = []
        
        try:
            results = data.get('props', [])
            
            for prop in results:
                house = {
                    'api_source': 'rapidapi_zillow',
                    'external_id': prop.get('zpid'),
                    'address': prop.get('address'),
                    'price': prop.get('price'),
                    'bedrooms': prop.get('bedrooms'),
                    'bathrooms': prop.get('bathrooms'),
                    'sqft': prop.get('livingArea'),
                    'year_built': prop.get('yearBuilt'),
                    'latitude': prop.get('latitude'),
                    'longitude': prop.get('longitude'),
                    'property_type': prop.get('homeType'),
                    'listing_url': f"https://www.zillow.com{prop.get('detailUrl', '')}",
                    'photos': prop.get('imgSrc', []),
                    'days_on_market': prop.get('daysOnZillow'),
                    'price_change': prop.get('priceChange'),
                    'zestimate': prop.get('zestimate'),
                    'last_updated': datetime.now().isoformat()
                }
                
                if self.is_valid_house(house):
                    houses.append(house)
                    
        except Exception as e:
            print(f"⚠️ Error parsing RapidAPI data: {e}")
        
        return houses
    
    def is_valid_house(self, house: Dict) -> bool:
        """Validate house data completeness"""
        required_fields = ['price', 'bedrooms', 'sqft', 'latitude', 'longitude']
        return all(house.get(field) is not None for field in required_fields)
    
    def get_enhanced_market_data(self) -> List[Dict]:
        """Combine multiple data sources for comprehensive market data"""
        
        print("🔍 Fetching real market data from multiple sources...")
        all_houses = []
        
        # Try each API
        sources = [
            ('RentSpree', self.get_zillow_rentals_api),
            ('RapidAPI', self.get_rapidapi_zillow),
        ]
        
        for source_name, source_func in sources:
            try:
                print(f"📡 Trying {source_name}...")
                houses = source_func()
                if houses:
                    print(f"✅ Got {len(houses)} houses from {source_name}")
                    all_houses.extend(houses)
                else:
                    print(f"⚠️ No data from {source_name}")
            except Exception as e:
                print(f"❌ {source_name} failed: {e}")
        
        # Remove duplicates based on address
        if all_houses:
            df = pd.DataFrame(all_houses)
            df = df.drop_duplicates(subset=['address'], keep='first')
            all_houses = df.to_dict('records')
            print(f"🎯 Final dataset: {len(all_houses)} unique houses")
        
        return all_houses

class SmartDataManager:
    """Manage data freshness and caching"""
    
    def __init__(self, cache_duration_hours: int = 6):
        self.cache_duration = timedelta(hours=cache_duration_hours)
        self.cache_file = 'real_estate_cache.json'
    
    def get_cached_data(self) -> Optional[List[Dict]]:
        """Get cached data if it's still fresh"""
        
        if not os.path.exists(self.cache_file):
            return None
        
        try:
            with open(self.cache_file, 'r') as f:
                cached = json.load(f)
            
            cache_time = datetime.fromisoformat(cached['timestamp'])
            
            if datetime.now() - cache_time < self.cache_duration:
                print(f"📋 Using cached data from {cache_time.strftime('%H:%M')}")
                return cached['houses']
            else:
                print("🔄 Cache expired, fetching fresh data...")
                return None
                
        except Exception as e:
            print(f"⚠️ Cache read error: {e}")
            return None
    
    def save_to_cache(self, houses: List[Dict]):
        """Save fresh data to cache"""
        
        try:
            cache_data = {
                'timestamp': datetime.now().isoformat(),
                'houses': houses,
                'count': len(houses)
            }
            
            with open(self.cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
            
            print(f"💾 Cached {len(houses)} houses")
            
        except Exception as e:
            print(f"⚠️ Cache save error: {e}")
    
    def get_fresh_data(self) -> List[Dict]:
        """Get the freshest data available"""
        
        # Try cache first
        cached_data = self.get_cached_data()
        if cached_data:
            return cached_data
        
        # Fetch fresh data
        integrator = RealEstateDataIntegrator()
        fresh_data = integrator.get_enhanced_market_data()
        
        if fresh_data:
            self.save_to_cache(fresh_data)
            return fresh_data
        else:
            print("⚠️ No fresh data available, using fallback...")
            # Import fallback data from your existing system
            try:
                from all_in_one_house_hunter import HouseDataCollector
                collector = HouseDataCollector()
                return collector.get_minneapolis_houses()
            except:
                return []

def setup_api_keys():
    """Helper function to set up API keys"""
    
    print("🔑 API Key Setup Guide")
    print("=" * 40)
    
    apis = {
        'RapidAPI (Zillow)': {
            'url': 'https://rapidapi.com/apimaker/api/zillow-com1/',
            'cost': '$10/month for 1000 requests',
            'env_var': 'RAPIDAPI_KEY',
            'description': 'Most reliable Zillow data'
        },
        'RentSpree': {
            'url': 'https://www.rentspree.com/api',
            'cost': 'Free tier available',
            'env_var': 'RENTSPREE_KEY', 
            'description': 'Good for rental and sale data'
        },
        'Realty Mole': {
            'url': 'https://rapidapi.com/realty-mole/api/realty-mole-property-api/',
            'cost': '$20/month',
            'env_var': 'REALTY_MOLE_KEY',
            'description': 'Property details and comparables'
        }
    }
    
    for name, info in apis.items():
        print(f"\n📡 {name}")
        print(f"   🌐 Sign up: {info['url']}")
        print(f"   💰 Cost: {info['cost']}")
        print(f"   🔧 Set env var: export {info['env_var']}=your_key_here")
        print(f"   📝 {info['description']}")
    
    print(f"\n💡 Quick Setup:")
    print(f"   1. Start with RapidAPI Zillow (most data)")
    print(f"   2. Add RentSpree for free tier")
    print(f"   3. Use Realty Mole for detailed analysis")
    
    print(f"\n🔧 To set environment variables:")
    print(f"   # Linux/Mac:")
    print(f"   export RAPIDAPI_KEY='your_key_here'")
    print(f"   # Windows:")
    print(f"   set RAPIDAPI_KEY=your_key_here")

def main():
    """Main function to test real data integration"""
    
    print("🏠 Real Estate Data Integration Test")
    print("=" * 45)
    
    # Check for API keys
    data_manager = SmartDataManager()
    
    # Get fresh data
    houses = data_manager.get_fresh_data()
    
    if houses:
        print(f"✅ Successfully loaded {len(houses)} houses")
        
        # Convert to DataFrame for analysis
        df = pd.DataFrame(houses)
        
        # Show data sources
        if 'api_source' in df.columns:
            sources = df['api_source'].value_counts()
            print(f"\n📊 Data Sources:")
            for source, count in sources.items():
                print(f"   {source}: {count} houses")
        
        # Show sample data
        print(f"\n📋 Sample Data:")
        sample_cols = ['address', 'price', 'bedrooms', 'sqft', 'api_source']
        available_cols = [col for col in sample_cols if col in df.columns]
        print(df[available_cols].head())
        
        # Save for use with scoring system
        df.to_csv('real_market_data.csv', index=False)
        print(f"\n💾 Saved to 'real_market_data.csv'")
        
        # Integration with existing scorer
        try:
            from all_in_one_house_hunter import AdvancedHouseScorer
            
            print(f"\n🎯 Running AI Analysis...")
            scorer = AdvancedHouseScorer()
            
            scored_houses = []
            for house in houses[:10]:  # Score first 10 for demo
                try:
                    scores = scorer.score_house(house)
                    house_with_scores = {**house, **scores}
                    scored_houses.append(house_with_scores)
                except Exception as e:
                    print(f"⚠️ Scoring error for house: {e}")
            
            if scored_houses:
                scored_df = pd.DataFrame(scored_houses)
                scored_df = scored_df.sort_values('overall_score', ascending=False)
                
                print(f"\n🏆 TOP 3 REAL MARKET OPPORTUNITIES:")
                for idx, house in scored_df.head(3).iterrows():
                    print(f"   {house.get('address', 'Address N/A')[:50]}")
                    print(f"   💰 ${house.get('price', 0):,} | 🎯 Score: {house.get('overall_score', 0):.1%}")
                    print(f"   📊 {house.get('recommendation', 'No recommendation')}")
                    print()
                
                # Save scored real data
                scored_df.to_csv('real_scored_houses.csv', index=False)
                print(f"💾 Scored real data saved to 'real_scored_houses.csv'")
            
        except ImportError:
            print("⚠️ Could not import scoring system")
        
    else:
        print("❌ No real data available")
        print("💡 Try setting up API keys or check your internet connection")
        setup_api_keys()

if __name__ == "__main__":
    main()