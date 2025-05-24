# all_in_one_house_hunter.py
# Complete house hunting system - data collection + scoring + analysis

import pandas as pd
import numpy as np
from geopy.distance import geodesic
from datetime import datetime
import json

class HouseDataCollector:
    """Collects realistic house data for Minneapolis area"""
    
    def get_minneapolis_houses(self):
        """Get realistic sample data based on current market research"""
        
        print("🏠 Collecting Minneapolis area house data...")
        
        # Realistic data based on actual Minneapolis market
        houses = [
            {
                'zpid': f'sample_{i}',
                'address': address,
                'price': price,
                'bedrooms': beds,
                'bathrooms': baths,
                'sqft': sqft,
                'lot_size': lot,
                'year_built': year,
                'latitude': lat,
                'longitude': lon,
                'property_type': 'Single Family',
                'days_on_market': days,
                'has_garage': garage,
                'garage_spaces': garage_spaces,
                'listing_url': f'https://www.zillow.com/homedetails/sample_{i}',
                'price_change': price_change,
                'listing_status': 'For Sale',
                'neighborhood': neighborhood,
                'school_rating': school,
                'walk_score': walk,
                'description': description
            }
            for i, (address, price, beds, baths, sqft, lot, year, lat, lon, days, garage, garage_spaces, 
                    price_change, neighborhood, school, walk, description) in enumerate([
                
                # Plymouth - Great schools, family-friendly
                ('4125 Fernbrook Ln, Plymouth, MN 55446', 349900, 3, 2.5, 1456, 7200, 2014, 
                 45.0123, -93.4501, 8, True, 2, 0, 'Plymouth', 8.2, 65,
                 'Updated kitchen, hardwood floors, finished basement'),
                
                ('3890 Juniper Ave, Plymouth, MN 55446', 372000, 4, 3, 1650, 8100, 2016, 
                 45.0156, -93.4423, 5, True, 3, -5000, 'Plymouth', 8.5, 68,
                 'New construction, granite counters, 3-car garage'),
                 
                # Woodbury - Newer developments, good value
                ('8945 Tamarack Dr, Woodbury, MN 55125', 329000, 4, 2.5, 1620, 8500, 2016, 
                 44.9234, -92.9591, 5, True, 3, -5000, 'Woodbury', 9.1, 52,
                 'Open floor plan, master suite, large lot'),
                 
                ('7234 Eagle Ridge Dr, Woodbury, MN 55125', 298500, 3, 2, 1380, 7800, 2012, 
                 44.9189, -92.9456, 12, True, 2, 0, 'Woodbury', 8.8, 48,
                 'Move-in ready, updated appliances, quiet cul-de-sac'),
                 
                # Maple Grove - Premium area, higher prices  
                ('12567 Elm Creek Blvd, Maple Grove, MN 55369', 389000, 3, 2, 1385, 6800, 2018, 
                 45.0697, -93.4568, 12, True, 2, 0, 'Maple Grove', 9.2, 71,
                 'Like new, premium finishes, near parks'),
                 
                ('11890 Main St, Maple Grove, MN 55369', 365000, 3, 2.5, 1445, 7200, 2015, 
                 45.0723, -93.4612, 18, True, 2, -8000, 'Maple Grove', 8.9, 74,
                 'Price reduced! Vaulted ceilings, fireplace'),
                 
                # Blaine - Best value, longer commute
                ('2834 Northern Pine Dr, Blaine, MN 55449', 298000, 3, 2, 1344, 7800, 2011, 
                 45.1608, -93.2349, 18, True, 2, -8000, 'Blaine', 7.8, 45,
                 'Great value, near lakes, spacious yard'),
                 
                ('3456 Sunrise Blvd, Blaine, MN 55449', 275000, 3, 2, 1298, 8200, 2009, 
                 45.1678, -93.2287, 25, True, 2, 0, 'Blaine', 7.5, 42,
                 'Starter home, good bones, needs updates'),
                 
                # Roseville - Close to city, walkable
                ('1567 Victoria St, Roseville, MN 55113', 365000, 3, 2, 1298, 6200, 2009, 
                 45.0061, -93.1567, 25, True, 2, 0, 'Roseville', 8.1, 78,
                 'Walkable neighborhood, close to transit'),
                 
                ('2890 Lexington Ave, Roseville, MN 55113', 342000, 3, 2.5, 1425, 6800, 2013, 
                 45.0089, -93.1623, 15, True, 2, -3000, 'Roseville', 8.3, 81,
                 'Updated throughout, corner lot, mature trees'),
                 
                # Eagan - Good schools, family areas
                ('4567 Cedar Grove Dr, Eagan, MN 55123', 335000, 4, 2.5, 1580, 8900, 2014, 
                 44.8041, -93.1668, 9, True, 3, 0, 'Eagan', 8.7, 58,
                 'Spacious layout, 4 bedrooms, 3-car garage'),
                 
                ('5678 Parkview Ln, Eagan, MN 55123', 318000, 3, 2, 1456, 7600, 2010, 
                 44.8123, -93.1589, 22, True, 2, -7000, 'Eagan', 8.4, 55,
                 'Price drop! Motivated seller, great schools'),
                 
                # White Bear Lake - Lakefront premium
                ('1234 Lake Dr, White Bear Lake, MN 55110', 395000, 3, 2.5, 1389, 9200, 2017, 
                 45.0847, -92.9968, 6, True, 2, 0, 'White Bear Lake', 8.6, 62,
                 'Near lake, new construction, premium lot'),
                 
                ('5432 Forest Ave, White Bear Lake, MN 55110', 358000, 3, 2, 1345, 8100, 2011, 
                 45.0798, -92.9945, 14, True, 2, -4000, 'White Bear Lake', 8.2, 59,
                 'Lake access, updated kitchen, mature landscaping'),
                 
                # Burnsville - Southern suburb value
                ('7890 River Hills Dr, Burnsville, MN 55337', 289000, 3, 2, 1267, 7200, 2008, 
                 44.7678, -93.2777, 28, True, 2, -12000, 'Burnsville', 7.9, 51,
                 'Motivated seller, some updates needed, good location')
            ])
        ]
        
        return houses

class AdvancedHouseScorer:
    """Advanced scoring system with detailed analysis"""
    
    def __init__(self, preferences=None):
        # Your customizable preferences
        self.preferences = preferences or {
            'max_budget': 400000,
            'max_commute_minutes': 30,
            'min_bedrooms': 3,
            'min_sqft': 1200,
            'min_year_built': 2000,
            'needs_garage': True,
            'needs_backyard': True,
            'water_proximity_important': True
        }
        
        # Scoring weights (must sum to 1.0)
        self.weights = {
            'price': 0.25,           # Value for money
            'commute': 0.20,         # Distance to downtown
            'size': 0.15,            # Square footage
            'age': 0.15,             # Year built/condition  
            'location': 0.10,        # Neighborhood quality
            'market_timing': 0.10,   # Days on market, price changes
            'features': 0.05         # Garage, lot size, etc.
        }
        
        self.downtown_minneapolis = (44.9778, -93.2650)
    
    def calculate_commute_score(self, lat, lon):
        """Score based on commute to downtown Minneapolis"""
        house_location = (lat, lon)
        distance_miles = geodesic(house_location, self.downtown_minneapolis).miles
        commute_minutes = distance_miles * 2  # Rough estimate: 2 min per mile
        
        if commute_minutes <= self.preferences['max_commute_minutes']:
            # Linear scoring: closer = better
            return 1.0 - (commute_minutes / self.preferences['max_commute_minutes']) * 0.6
        else:
            return 0.0  # Deal breaker if too far
    
    def calculate_price_score(self, price):
        """Score based on price vs budget"""
        if price <= self.preferences['max_budget']:
            # Reward lower prices within budget
            return 1.0 - (price / self.preferences['max_budget']) * 0.4
        else:
            # Penalty for over budget
            overage = (price - self.preferences['max_budget']) / self.preferences['max_budget']
            return max(0, 1.0 - overage * 2)
    
    def calculate_size_score(self, sqft):
        """Score based on square footage"""
        if sqft >= self.preferences['min_sqft']:
            # Bonus for larger houses, but diminishing returns
            bonus = (sqft - self.preferences['min_sqft']) / self.preferences['min_sqft']
            return min(1.0, 0.7 + bonus * 0.3)
        else:
            return sqft / self.preferences['min_sqft']
    
    def calculate_age_score(self, year_built):
        """Score based on house age"""
        if year_built >= self.preferences['min_year_built']:
            # Bonus for newer houses
            years_newer = year_built - self.preferences['min_year_built']
            return min(1.0, 0.8 + years_newer * 0.01)
        else:
            age_penalty = (self.preferences['min_year_built'] - year_built) / 30
            return max(0, 1.0 - age_penalty)
    
    def calculate_location_score(self, neighborhood, school_rating, walk_score):
        """Score based on neighborhood quality"""
        # School rating (0-10 scale)
        school_score = school_rating / 10.0
        
        # Walk score (0-100 scale)  
        walk_score_norm = walk_score / 100.0
        
        # Premium neighborhoods bonus
        premium_neighborhoods = ['Maple Grove', 'Plymouth', 'Woodbury', 'Eagan']
        neighborhood_bonus = 0.2 if neighborhood in premium_neighborhoods else 0
        
        return min(1.0, (school_score * 0.6 + walk_score_norm * 0.4 + neighborhood_bonus))
    
    def calculate_market_timing_score(self, days_on_market, price_change):
        """Score based on market conditions"""
        # Days on market scoring
        if days_on_market < 7:
            dom_score = 1.0  # Hot property
        elif days_on_market < 21:
            dom_score = 0.8  # Normal
        elif days_on_market < 60:
            dom_score = 0.6  # Slower
        else:
            dom_score = 0.4  # Stale listing
        
        # Price change scoring
        if price_change < 0:
            price_change_score = 1.0  # Price reduction = opportunity
        elif price_change == 0:
            price_change_score = 0.8  # Stable
        else:
            price_change_score = 0.6  # Price increase
        
        return (dom_score * 0.7 + price_change_score * 0.3)
    
    def calculate_features_score(self, has_garage, bedrooms, lot_size):
        """Score based on specific features"""
        score = 0.5  # Base score
        
        # Garage requirement
        if self.preferences['needs_garage'] and has_garage:
            score += 0.3
        elif not self.preferences['needs_garage']:
            score += 0.3
        
        # Bedroom requirement
        if bedrooms >= self.preferences['min_bedrooms']:
            score += 0.2
        
        # Lot size (8000+ sqft is good for suburbs)
        if lot_size >= 8000:
            score += 0.2
        elif lot_size >= 6000:
            score += 0.1
        
        return min(1.0, score)
    
    def score_house(self, house):
        """Calculate comprehensive score for a house"""
        
        # Calculate individual component scores
        price_score = self.calculate_price_score(house['price'])
        commute_score = self.calculate_commute_score(house['latitude'], house['longitude'])
        size_score = self.calculate_size_score(house['sqft'])
        age_score = self.calculate_age_score(house['year_built'])
        location_score = self.calculate_location_score(
            house['neighborhood'], house['school_rating'], house['walk_score']
        )
        market_score = self.calculate_market_timing_score(
            house['days_on_market'], house['price_change']
        )
        features_score = self.calculate_features_score(
            house['has_garage'], house['bedrooms'], house['lot_size']
        )
        
        # Calculate weighted overall score
        overall_score = (
            price_score * self.weights['price'] +
            commute_score * self.weights['commute'] +
            size_score * self.weights['size'] +
            age_score * self.weights['age'] +
            location_score * self.weights['location'] +
            market_score * self.weights['market_timing'] +
            features_score * self.weights['features']
        )
        
        # Must meet basic requirements
        meets_requirements = (
            commute_score > 0 and  # Within commute range
            house['bedrooms'] >= self.preferences['min_bedrooms'] and
            (not self.preferences['needs_garage'] or house['has_garage'])
        )
        
        return {
            'overall_score': round(overall_score, 3),
            'price_score': round(price_score, 3),
            'commute_score': round(commute_score, 3),
            'size_score': round(size_score, 3),
            'age_score': round(age_score, 3),
            'location_score': round(location_score, 3),
            'market_score': round(market_score, 3),
            'features_score': round(features_score, 3),
            'meets_requirements': meets_requirements,
            'recommendation': self.get_recommendation(overall_score, meets_requirements)
        }
    
    def get_recommendation(self, score, meets_requirements):
        """Get AI recommendation based on score"""
        if not meets_requirements:
            return "❌ SKIP - Doesn't meet basic requirements"
        elif score >= 0.85:
            return "🔥 MUST SEE - Exceptional match!"
        elif score >= 0.75:
            return "⭐ HIGHLY RECOMMENDED"
        elif score >= 0.65:
            return "✅ GOOD OPTION - Worth considering"
        elif score >= 0.55:
            return "⚠️ DECENT - Has trade-offs"
        else:
            return "❌ BELOW THRESHOLD"

def analyze_market(houses_df):
    """Provide market analysis and insights"""
    
    print(f"\n📊 MINNEAPOLIS MARKET ANALYSIS")
    print("=" * 50)
    
    viable_houses = houses_df[houses_df['meets_requirements'] == True]
    
    if len(viable_houses) == 0:
        print("❌ No houses meet your requirements!")
        return
    
    # Market stats
    print(f"📈 Market Overview:")
    print(f"   Total Houses: {len(houses_df)}")
    print(f"   Meet Requirements: {len(viable_houses)}")
    print(f"   Avg Score: {viable_houses['overall_score'].mean():.1%}")
    print(f"   Price Range: ${viable_houses['price'].min():,} - ${viable_houses['price'].max():,}")
    print(f"   Avg Price: ${viable_houses['price'].mean():,.0f}")
    print(f"   Avg $/sqft: ${(viable_houses['price'] / viable_houses['sqft']).mean():.0f}")
    
    # Best opportunities
    print(f"\n🎯 BEST OPPORTUNITIES:")
    top_houses = viable_houses.nlargest(3, 'overall_score')
    for idx, house in top_houses.iterrows():
        print(f"   {house['address'][:45]} - Score: {house['overall_score']:.1%}")
    
    # Best values
    print(f"\n💰 BEST VALUES (Price/sqft):")
    viable_houses['price_per_sqft'] = viable_houses['price'] / viable_houses['sqft']
    best_values = viable_houses.nsmallest(3, 'price_per_sqft')
    for idx, house in best_values.iterrows():
        print(f"   {house['address'][:45]} - ${house['price_per_sqft']:.0f}/sqft")
    
    # Market timing opportunities
    print(f"\n⏰ MARKET TIMING OPPORTUNITIES:")
    price_drops = viable_houses[viable_houses['price_change'] < 0].nlargest(3, 'market_score')
    for idx, house in price_drops.iterrows():
        print(f"   {house['address'][:45]} - ${house['price_change']:,} price drop")

def print_detailed_results(houses_df, top_n=5):
    """Print detailed analysis of top houses"""
    
    viable_houses = houses_df[houses_df['meets_requirements'] == True]
    top_houses = viable_houses.nlargest(top_n, 'overall_score')
    
    print(f"\n🏆 TOP {top_n} HOUSE RECOMMENDATIONS")
    print("=" * 80)
    
    for rank, (idx, house) in enumerate(top_houses.iterrows(), 1):
        print(f"\n#{rank}. {house['address']}")
        print(f"    💰 ${house['price']:,} | 📐 {house['sqft']} sqft | 🏠 {house['bedrooms']} bed, {house['bathrooms']} bath")
        print(f"    🎯 AI SCORE: {house['overall_score']:.1%} | 📅 Built {house['year_built']} | 📍 {house['neighborhood']}")
        print(f"    🚗 Commute: ~{geodesic((house['latitude'], house['longitude']), (44.9778, -93.2650)).miles * 2:.0f} min | 🏫 School: {house['school_rating']}/10")
        print(f"    📊 Scores: Price({house['price_score']:.2f}) | Location({house['location_score']:.2f}) | Market({house['market_score']:.2f})")
        print(f"    🔍 {house['recommendation']}")
        print(f"    📝 {house['description']}")
        print("-" * 80)

def main():
    """Main function - complete house hunting analysis"""
    
    print("🏠 AI-POWERED HOUSE HUNTER")
    print("🎯 Complete Analysis: Data Collection + Scoring + Recommendations")
    print("=" * 60)
    
    # Step 1: Collect house data
    collector = HouseDataCollector()
    houses = collector.get_minneapolis_houses()
    print(f"✅ Collected {len(houses)} houses from Minneapolis area")
    
    # Step 2: Set up scorer with your preferences
    preferences = {
        'max_budget': 400000,      # YOUR MAX BUDGET
        'max_commute_minutes': 30, # YOUR MAX COMMUTE
        'min_bedrooms': 3,         # YOUR MIN BEDROOMS
        'min_sqft': 1200,          # YOUR MIN SQUARE FEET
        'min_year_built': 2000,    # YOUR MIN YEAR BUILT
        'needs_garage': True,      # DO YOU NEED A GARAGE?
        'needs_backyard': True,    # DO YOU NEED A BACKYARD?
        'water_proximity_important': True  # IS WATER PROXIMITY IMPORTANT?
    }
    
    scorer = AdvancedHouseScorer(preferences)
    print(f"⚙️ Configured scorer with your preferences")
    
    # Step 3: Score all houses
    scored_houses = []
    for house in houses:
        scores = scorer.score_house(house)
        house_with_scores = {**house, **scores}
        scored_houses.append(house_with_scores)
    
    # Step 4: Create DataFrame and analyze
    df = pd.DataFrame(scored_houses)
    df = df.sort_values('overall_score', ascending=False)
    print(f"🎯 Scored {len(df)} houses")
    
    # Step 5: Save results
    df.to_csv('ai_house_analysis.csv', index=False)
    print(f"💾 Results saved to 'ai_house_analysis.csv'")
    
    # Step 6: Show analysis
    analyze_market(df)
    print_detailed_results(df, top_n=5)
    
    # Step 7: Action items
    print(f"\n🎯 NEXT STEPS:")
    top_3 = df[df['meets_requirements'] == True].head(3)
    for idx, house in top_3.iterrows():
        print(f"   📞 Schedule tour: {house['address']}")
        print(f"      Score: {house['overall_score']:.1%} | ${house['price']:,}")
    
    return df

if __name__ == "__main__":
    results_df = main()