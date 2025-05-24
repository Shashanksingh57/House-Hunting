# data_update_explainer.py
# Explains current limitations and how to get more data

import os
import pandas as pd
from datetime import datetime

def check_current_data_status():
    """Check what data you currently have and its limitations"""
    
    print("🔍 CURRENT DATA STATUS ANALYSIS")
    print("=" * 40)
    
    files_to_check = [
        'real_zillow_data.csv',
        'real_scored_houses.csv'
    ]
    
    for filename in files_to_check:
        if os.path.exists(filename):
            try:
                df = pd.read_csv(filename)
                file_age = datetime.now() - datetime.fromtimestamp(os.path.getmtime(filename))
                
                print(f"\n📄 {filename}:")
                print(f"   🏠 Houses: {len(df)}")
                print(f"   📅 Last updated: {file_age.days} days, {file_age.seconds//3600} hours ago")
                
                # Check data source
                if 'data_source' in df.columns:
                    sources = df['data_source'].value_counts()
                    for source, count in sources.items():
                        if source == 'zillow_rapidapi':
                            print(f"   🔥 Real Zillow data: {count} houses")
                        else:
                            print(f"   📊 {source}: {count} houses")
                
                # Check for unique identifiers
                if 'zpid' in df.columns:
                    unique_zpids = df['zpid'].nunique()
                    print(f"   🆔 Unique properties: {unique_zpids}")
                
                # Show sample of addresses to verify
                if 'address' in df.columns:
                    print(f"   📍 Sample addresses:")
                    for addr in df['address'].head(3):
                        print(f"      • {addr}")
                
                # Check price range
                if 'price' in df.columns:
                    print(f"   💰 Price range: ${df['price'].min():,} - ${df['price'].max():,}")
                
            except Exception as e:
                print(f"❌ Error reading {filename}: {e}")
        else:
            print(f"❌ {filename} not found")

def explain_current_limitations():
    """Explain why you're seeing limited data"""
    
    print("\n📋 CURRENT LIMITATIONS EXPLAINED")
    print("=" * 35)
    
    limitations = {
        "🔢 House Count Limit": {
            "issue": "You're seeing ~25-50 houses max",
            "why": "RapidAPI Zillow endpoints have built-in pagination limits",
            "impact": "Missing many available properties"
        },
        "🔄 No Auto-Updates": {
            "issue": "Data doesn't refresh automatically", 
            "why": "No scheduled automation set up yet",
            "impact": "Missing new listings and price changes"
        },
        "🗺️ Geographic Scope": {
            "issue": "Limited to basic Minneapolis search",
            "why": "Single search query vs comprehensive area coverage",
            "impact": "Missing properties in surrounding areas"
        },
        "📊 API Rate Limits": {
            "issue": "Can't fetch unlimited data",
            "why": "RapidAPI free/paid tiers have request limits",
            "impact": "Can't get full market coverage"
        }
    }
    
    for category, details in limitations.items():
        print(f"\n{category}")
        print(f"   ❌ Issue: {details['issue']}")
        print(f"   🔍 Why: {details['why']}")
        print(f"   📈 Impact: {details['impact']}")

def show_solutions():
    """Show how to get more comprehensive data"""
    
    print("\n🚀 SOLUTIONS TO GET MORE DATA")
    print("=" * 30)
    
    solutions = [
        {
            "name": "🔄 Set Up Auto-Updates",
            "description": "Automatically refresh data every few hours",
            "command": "python advanced_house_hunter.py",
            "benefit": "Never miss new listings or price drops"
        },
        {
            "name": "📈 Increase Data Volume", 
            "description": "Multiple API calls to get more properties",
            "command": "python comprehensive_data_collector.py",
            "benefit": "Get 200+ houses instead of 25-50"
        },
        {
            "name": "🗺️ Multi-Area Search",
            "description": "Search multiple neighborhoods separately",
            "command": "python multi_area_search.py", 
            "benefit": "Cover entire Minneapolis metro area"
        },
        {
            "name": "💰 Upgrade API Plan",
            "description": "Get higher rate limits and more data",
            "command": "Upgrade on RapidAPI dashboard",
            "benefit": "10x more data, faster updates"
        }
    ]
    
    for i, solution in enumerate(solutions, 1):
        print(f"\n{i}. {solution['name']}")
        print(f"   📝 {solution['description']}")
        print(f"   ⚡ Command: {solution['command']}")
        print(f"   ✅ Benefit: {solution['benefit']}")

def create_comprehensive_collector():
    """Create a script to get more comprehensive data"""
    
    script_content = '''# comprehensive_data_collector.py
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
        print(f"\\n📡 Search {i+1}/{len(search_configs)}: {config['location']}")
        
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
        
        print(f"\\n🎯 Total unique houses collected: {len(df)}")
        
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
            
            print(f"\\n💾 Saved {len(comprehensive_df)} scored houses to {filename}")
            
            # Show top opportunities
            print(f"\\n🏆 TOP 5 OPPORTUNITIES:")
            for idx, house in comprehensive_df.head(5).iterrows():
                print(f"   {idx+1}. {house['address']}")
                print(f"      💰 ${house['price']:,} | 🎯 {house['overall_score']:.1%}")
            
            return comprehensive_df
    
    return None

if __name__ == "__main__":
    result = get_comprehensive_data()
    if result is not None:
        print(f"\\n🎉 Success! Check your dashboard for {len(result)} houses")
    else:
        print("\\n❌ No data collected")
'''
    
    with open('comprehensive_data_collector.py', 'w') as f:
        f.write(script_content)
    
    print(f"\n💾 Created 'comprehensive_data_collector.py'")
    print(f"🚀 Run it with: python comprehensive_data_collector.py")

if __name__ == "__main__":
    check_current_data_status()
    explain_current_limitations()
    show_solutions()
    create_comprehensive_collector()