# quick_start_scorer.py
import pandas as pd
import numpy as np
from geopy.distance import geodesic

class QuickHouseScorer:
    """Simplified version to get you started immediately"""
    
    def __init__(self):
        # Your specific preferences - CUSTOMIZE THESE
        self.max_budget = 400000
        self.max_commute_minutes = 30
        self.min_bedrooms = 3
        self.min_sqft = 1200
        self.min_year_built = 2000
        
        # Scoring weights - ADJUST THESE
        self.weights = {
            'price': 0.25,      # Lower price is better
            'commute': 0.20,    # Shorter commute is better
            'size': 0.15,       # Larger is better
            'age': 0.15,        # Newer is better
            'value': 0.15,      # Better price per sqft
            'requirements': 0.10 # Meets basic requirements
        }
        
        self.downtown_minneapolis = (44.9778, -93.2650)
    
    def score_price(self, price):
        """Score based on price (lower is better)"""
        if price <= self.max_budget:
            return 1.0 - (price / self.max_budget) * 0.5  # Best score for lowest prices
        else:
            # Penalty for over budget
            overage = (price - self.max_budget) / self.max_budget
            return max(0, 1.0 - overage)
    
    def score_commute(self, lat, lon):
        """Score based on commute time"""
        house_location = (lat, lon)
        distance_miles = geodesic(house_location, self.downtown_minneapolis).miles
        commute_minutes = distance_miles * 2  # Rough estimate
        
        if commute_minutes <= self.max_commute_minutes:
            return 1.0 - (commute_minutes / self.max_commute_minutes) * 0.7
        else:
            return 0.0  # Deal breaker
    
    def score_size(self, sqft):
        """Score based on square footage"""
        if sqft >= self.min_sqft:
            # Bonus for larger houses, but diminishing returns
            bonus = (sqft - self.min_sqft) / self.min_sqft
            return min(1.0, 0.7 + bonus * 0.3)
        else:
            return sqft / self.min_sqft
    
    def score_age(self, year_built):
        """Score based on house age"""
        if year_built >= self.min_year_built:
            # Bonus for newer houses
            years_newer = year_built - self.min_year_built
            return min(1.0, 0.8 + years_newer * 0.01)
        else:
            age_penalty = (self.min_year_built - year_built) / 25
            return max(0, 1.0 - age_penalty)
    
    def score_value(self, price, sqft):
        """Score based on price per square foot"""
        price_per_sqft = price / sqft
        
        # Benchmark: $200-250/sqft is good value in Minneapolis suburbs
        if price_per_sqft <= 200:
            return 1.0
        elif price_per_sqft <= 250:
            return 0.8
        elif price_per_sqft <= 300:
            return 0.6
        else:
            return max(0, 0.6 - (price_per_sqft - 300) / 100 * 0.2)
    
    def score_requirements(self, bedrooms, has_garage, year_built):
        """Score for meeting basic requirements"""
        score = 1.0
        
        if bedrooms < self.min_bedrooms:
            score *= 0.5  # Major penalty
        
        if not has_garage:
            score *= 0.7  # You wanted a garage
        
        if year_built < 1990:  # Very old house
            score *= 0.8
        
        return score
    
    def score_house(self, house_data):
        """Calculate overall score for a house"""
        
        # Individual scores
        price_score = self.score_price(house_data['price'])
        commute_score = self.score_commute(house_data['latitude'], house_data['longitude'])
        size_score = self.score_size(house_data['sqft'])
        age_score = self.score_age(house_data['year_built'])
        value_score = self.score_value(house_data['price'], house_data['sqft'])
        req_score = self.score_requirements(
            house_data['bedrooms'], 
            house_data.get('has_garage', False),
            house_data['year_built']
        )
        
        # Calculate weighted overall score
        overall_score = (
            price_score * self.weights['price'] +
            commute_score * self.weights['commute'] +
            size_score * self.weights['size'] +
            age_score * self.weights['age'] +
            value_score * self.weights['value'] +
            req_score * self.weights['requirements']
        )
        
        return {
            'overall_score': round(overall_score, 3),
            'price_score': round(price_score, 3),
            'commute_score': round(commute_score, 3),
            'size_score': round(size_score, 3),
            'age_score': round(age_score, 3),
            'value_score': round(value_score, 3),
            'requirements_score': round(req_score, 3),
            'is_viable': commute_score > 0 and overall_score > 0.6  # Your threshold
        }

def analyze_houses(csv_file='sample_houses.csv'):
    """Analyze houses from CSV file"""
    
    # Load house data
    df = pd.read_csv(csv_file)
    scorer = QuickHouseScorer()
    
    # Score each house
    results = []
    for idx, house in df.iterrows():
        scores = scorer.score_house(house.to_dict())
        
        # Combine original data with scores
        result = house.to_dict()
        result.update(scores)
        results.append(result)
    
    # Create results DataFrame
    results_df = pd.DataFrame(results)
    
    # Sort by overall score
    results_df = results_df.sort_values('overall_score', ascending=False)
    
    return results_df

def print_top_houses(results_df, n=5):
    """Print top N houses with analysis"""
    
    print(f"\n🏆 TOP {n} HOUSES BY AI SCORE\n" + "="*50)
    
    for idx, house in results_df.head(n).iterrows():
        print(f"\n#{results_df.index.get_loc(idx) + 1}. {house['address']}")
        print(f"   💰 Price: ${house['price']:,} | 📐 {house['sqft']} sqft | 🚗 {house.get('estimated_commute_minutes', 'N/A')} min commute")
        print(f"   🎯 AI SCORE: {house['overall_score']:.1%} | 🏠 {house['bedrooms']} bed, {house['bathrooms']} bath")
        
        # Score breakdown
        print(f"   📊 Breakdown: Price({house['price_score']:.2f}) | Commute({house['commute_score']:.2f}) | Size({house['size_score']:.2f}) | Age({house['age_score']:.2f})")
        
        # Quick analysis
        if house['overall_score'] > 0.8:
            print("   ⭐ EXCELLENT MATCH - Highly recommended!")
        elif house['overall_score'] > 0.7:
            print("   ✅ GOOD MATCH - Worth serious consideration")
        elif house['overall_score'] > 0.6:
            print("   ⚠️  DECENT OPTION - Has some trade-offs")
        else:
            print("   ❌ BELOW THRESHOLD - Major issues")
        
        print("-" * 50)

if __name__ == "__main__":
    # Make sure you have sample_houses.csv first
    try:
        results = analyze_houses()
        
        print(f"📈 Analyzed {len(results)} houses")
        print(f"🎯 {len(results[results['is_viable']])} meet your criteria")
        
        # Show top houses
        print_top_houses(results)
        
        # Save detailed results
        results.to_csv('scored_houses.csv', index=False)
        print(f"\n💾 Detailed results saved to 'scored_houses.csv'")
        
        # Quick stats
        viable_houses = results[results['is_viable']]
        if len(viable_houses) > 0:
            avg_score = viable_houses['overall_score'].mean()
            avg_price = viable_houses['price'].mean()
            print(f"\n📊 STATS FOR VIABLE HOUSES:")
            print(f"   Average Score: {avg_score:.1%}")
            print(f"   Average Price: ${avg_price:,.0f}")
            print(f"   Price Range: ${viable_houses['price'].min():,} - ${viable_houses['price'].max():,}")
        
    except FileNotFoundError:
        print("❌ sample_houses.csv not found!")
        print("👉 First run the manual_data_collection.py script to create sample data")