# comprehensive_data_collector.py
# Get much more comprehensive Zillow data

import time
import pandas as pd
from test_real_data import ZillowRapidAPI, ensure_scoring_compatibility
from all_in_one_house_hunter import AdvancedHouseScorer

def get_comprehensive_data():
    """Get comprehensive data from multiple searches"""
    
    print("🔍 Starting comprehensive data collection...")
    
    zillow = ZillowRapidAPI()
    all_houses = []
    
    # Search multiple areas and price ranges
    search_configs = [
        {"location": "Plymouth, MN", "max_price": 400000, "min_beds": 3},
        {"location": "Woodbury, MN", "max_price": 400000, "min_beds": 3},
        {"location": "Maple Grove, MN", "max_price": 400000, "min_beds": 3},
        {"location": "Blaine, MN", "max_price": 400000, "min_beds": 3},
        {"location": "Eagan, MN", "max_price": 400000, "min_beds": 3},
        {"location": "Roseville, MN", "max_price": 400000, "min_beds": 3},
        
        # Different price ranges
        {"location": "Minneapolis, MN", "max_price": 350000, "min_beds": 3},
        {"location": "Minneapolis, MN", "max_price": 450000, "min_beds": 3},
        {"location": "Minneapolis, MN", "max_price": 500000, "min_beds": 4},
    ]
    
    for i, config in enumerate(search_configs):
        print(f"\n📡 Search {i+1}/{len(search_configs)}: {config['location']}")
        
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
            
            # Rate limiting - be respectful
            time.sleep(3)
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            continue
    
    if all_houses:
        # Remove duplicates based on zpid
        df = pd.DataFrame(all_houses)
        df = df.drop_duplicates(subset=['zpid'], keep='first')
        
        print(f"\n🎯 Total unique houses collected: {len(df)}")
        
        # Score all houses
        scorer = AdvancedHouseScorer()
        scored_houses = []
        
        print("🎯 Scoring all houses...")
        for house in df.to_dict('records'):
            try:
                house = ensure_scoring_compatibility(house)
                scores = scorer.score_house(house)
                house_with_scores = {**house, **scores}
                scored_houses.append(house_with_scores)
            except Exception as e:
                print(f"⚠️ Scoring error: {e}")
                continue
        
        # Save comprehensive data
        if scored_houses:
            comprehensive_df = pd.DataFrame(scored_houses)
            comprehensive_df = comprehensive_df.sort_values('overall_score', ascending=False)
            
            filename = f'comprehensive_houses_{pd.Timestamp.now().strftime("%Y%m%d_%H%M")}.csv'
            comprehensive_df.to_csv(filename, index=False)
            
            print(f"\n💾 Saved {len(comprehensive_df)} scored houses to {filename}")
            
            # Show top opportunities
            print(f"\n🏆 TOP 5 OPPORTUNITIES:")
            for idx, house in comprehensive_df.head(5).iterrows():
                print(f"   {idx+1}. {house['address']}")
                print(f"      💰 ${house['price']:,} | 🎯 {house['overall_score']:.1%}")
            
            return comprehensive_df
    
    return None

if __name__ == "__main__":
    result = get_comprehensive_data()
    if result is not None:
        print(f"\n🎉 Success! Check your dashboard for {len(result)} houses")
    else:
        print("\n❌ No data collected")
