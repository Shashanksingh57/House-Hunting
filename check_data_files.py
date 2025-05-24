# check_data_files.py
# Quick script to check what data files you have

import os
import pandas as pd
from datetime import datetime
import glob

def check_data_files():
    """Check all available data files"""
    
    print("🔍 CHECKING DATA FILES")
    print("=" * 30)
    
    # Files to check
    data_files = [
        'real_scored_houses.csv',
        'real_zillow_data.csv',
        'ai_house_analysis.csv',
        'market_data_*.csv',
        'house_analysis_*.csv'
    ]
    
    found_files = []
    
    for pattern in data_files:
        if '*' in pattern:
            files = glob.glob(pattern)
            found_files.extend(files)
        else:
            if os.path.exists(pattern):
                found_files.append(pattern)
    
    if not found_files:
        print("❌ No data files found!")
        print("💡 Run 'python test_real_data.py' to get real data")
        return
    
    print(f"📁 Found {len(found_files)} data files:\n")
    
    for file in sorted(found_files):
        try:
            # Get file info
            size_kb = os.path.getsize(file) / 1024
            mod_time = datetime.fromtimestamp(os.path.getmtime(file))
            
            # Load and check data
            df = pd.read_csv(file)
            
            # Determine data type
            if 'data_source' in df.columns:
                data_type = "🔥 REAL ZILLOW DATA"
            elif 'zpid' in df.columns and 'sample_' in str(df.iloc[0].get('zpid', '')):
                data_type = "🎭 Generated Sample Data"
            else:
                data_type = "📊 Market Data"
            
            print(f"✅ {file}")
            print(f"   {data_type}")
            print(f"   📏 {len(df)} houses | 💾 {size_kb:.1f}KB")
            print(f"   📅 Modified: {mod_time.strftime('%Y-%m-%d %H:%M')}")
            
            # Show sample addresses to verify
            if len(df) > 0 and 'address' in df.columns:
                sample_addresses = df['address'].head(2).tolist()
                for addr in sample_addresses:
                    print(f"   🏠 {addr[:60]}...")
            
            # Check if scored
            if 'overall_score' in df.columns:
                avg_score = df['overall_score'].mean()
                print(f"   🎯 Avg AI Score: {avg_score:.1%}")
            else:
                print(f"   ⚠️ Not yet scored")
            
            print()
            
        except Exception as e:
            print(f"❌ {file}: Error reading - {e}\n")
    
    # Recommend best file for dashboard
    print("🎯 RECOMMENDATION FOR DASHBOARD:")
    
    priority_files = [
        'real_scored_houses.csv',
        'real_zillow_data.csv'
    ]
    
    for priority_file in priority_files:
        if priority_file in found_files:
            print(f"✅ Use {priority_file} - this is your real Zillow data!")
            break
    else:
        print("⚠️ No real Zillow data found")
        print("💡 Run 'python test_real_data.py' first")

def show_data_sample(filename='real_scored_houses.csv'):
    """Show a sample of your real data"""
    
    if not os.path.exists(filename):
        print(f"❌ {filename} not found")
        return
    
    try:
        df = pd.read_csv(filename)
        
        print(f"\n📋 SAMPLE DATA FROM {filename}:")
        print("=" * 50)
        
        # Show top 3 houses
        display_cols = ['address', 'price', 'bedrooms', 'sqft', 'neighborhood']
        if 'overall_score' in df.columns:
            display_cols.append('overall_score')
            df = df.sort_values('overall_score', ascending=False)
        
        available_cols = [col for col in display_cols if col in df.columns]
        
        for idx, (_, house) in enumerate(df.head(3).iterrows()):
            print(f"\n🏠 House {idx + 1}:")
            for col in available_cols:
                value = house[col]
                if col == 'price':
                    print(f"   💰 {col}: ${value:,}")
                elif col == 'overall_score':
                    print(f"   🎯 {col}: {value:.1%}")
                else:
                    print(f"   📝 {col}: {value}")
        
        print(f"\n📊 SUMMARY:")
        print(f"   🏠 Total houses: {len(df)}")
        print(f"   💰 Price range: ${df['price'].min():,} - ${df['price'].max():,}")
        
        if 'overall_score' in df.columns:
            print(f"   🎯 Avg score: {df['overall_score'].mean():.1%}")
            high_score = len(df[df['overall_score'] > 0.8])
            print(f"   🔥 High-score houses (>80%): {high_score}")
    
    except Exception as e:
        print(f"❌ Error reading {filename}: {e}")

if __name__ == "__main__":
    check_data_files()
    
    # If real data exists, show sample
    if os.path.exists('real_scored_houses.csv'):
        show_data_sample('real_scored_houses.csv')
    elif os.path.exists('real_zillow_data.csv'):
        show_data_sample('real_zillow_data.csv')