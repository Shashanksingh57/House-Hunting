# enhanced_dynamic_dashboard.py
# Enhanced dashboard that loads all available Zillow data sources and removes garage filtering

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime
import os
import json
import glob

# Page config
st.set_page_config(
    page_title="AI House Hunter - Enhanced", 
    page_icon="🏠", 
    layout="wide"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-container {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
    }
    .score-high { background-color: #d4edda; border-left-color: #28a745; }
    .score-medium { background-color: #fff3cd; border-left-color: #ffc107; }
    .score-low { background-color: #f8d7da; border-left-color: #dc3545; }
</style>
""", unsafe_allow_html=True)

class ComprehensiveDataLoader:
    """Load all available house data from multiple sources"""
    
    def __init__(self):
        self.data_files = self.discover_data_files()
    
    def discover_data_files(self):
        """Find all available data files"""
        
        # Define patterns for different data files
        patterns = [
            'real_scored_houses.csv',
            'real_zillow_data.csv',
            'comprehensive_houses_*.csv',
            'zillow_houses_*.csv',
            'ai_house_analysis.csv',
            'collected_houses.csv'
        ]
        
        found_files = []
        
        for pattern in patterns:
            if '*' in pattern:
                # Use glob for wildcard patterns
                files = glob.glob(pattern)
                found_files.extend(files)
            else:
                # Check for exact file names
                if os.path.exists(pattern):
                    found_files.append(pattern)
        
        # Sort by modification time (newest first)
        found_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        
        return found_files
    
    def load_all_data(self):
        """Load and combine data from all sources"""
        
        if not self.data_files:
            return pd.DataFrame(), {}
        
        all_dataframes = []
        file_info = {}
        
        for file_path in self.data_files:
            try:
                df = pd.read_csv(file_path)
                
                if len(df) == 0:
                    continue
                
                # Add source tracking
                df['source_file'] = file_path
                df['file_date'] = datetime.fromtimestamp(os.path.getmtime(file_path))
                
                # Standardize column names
                df = self.standardize_columns(df)
                
                all_dataframes.append(df)
                
                file_info[file_path] = {
                    'houses': len(df),
                    'size_kb': os.path.getsize(file_path) / 1024,
                    'modified': datetime.fromtimestamp(os.path.getmtime(file_path)),
                    'columns': list(df.columns)
                }
                
                print(f"✅ Loaded {len(df)} houses from {file_path}")
                
            except Exception as e:
                print(f"⚠️ Error loading {file_path}: {e}")
                continue
        
        if not all_dataframes:
            return pd.DataFrame(), file_info
        
        # Combine all dataframes
        combined_df = pd.concat(all_dataframes, ignore_index=True, sort=False)
        
        # Remove duplicates - prefer newer data
        if 'zpid' in combined_df.columns:
            # Remove duplicates by zpid, keeping the most recent
            combined_df = combined_df.sort_values('file_date', ascending=False)
            combined_df = combined_df.drop_duplicates(subset=['zpid'], keep='first')
        elif 'address' in combined_df.columns:
            # Remove duplicates by address if no zpid
            combined_df = combined_df.sort_values('file_date', ascending=False)
            combined_df = combined_df.drop_duplicates(subset=['address'], keep='first')
        
        # Final data cleaning
        combined_df = self.clean_data(combined_df)
        
        print(f"🎯 Final dataset: {len(combined_df)} unique houses from {len(self.data_files)} files")
        
        return combined_df, file_info
    
    def standardize_columns(self, df):
        """Standardize column names across different data sources"""
        
        # Column mapping for different naming conventions
        column_mappings = {
            'square_footage': 'sqft',
            'livingArea': 'sqft',
            'living_area': 'sqft',
            'lotAreaValue': 'lot_size',
            'yearBuilt': 'year_built',
            'daysOnZillow': 'days_on_market',
            'homeStatus': 'listing_status',
            'homeType': 'property_type',
            'detailUrl': 'listing_url',
            'imgSrc': 'photos'
        }
        
        # Apply mappings
        for old_name, new_name in column_mappings.items():
            if old_name in df.columns and new_name not in df.columns:
                df[new_name] = df[old_name]
        
        return df
    
    def clean_data(self, df):
        """Clean and validate the combined dataset"""
        
        # Ensure required columns exist with defaults
        required_columns = {
            'address': 'Unknown Address',
            'price': 0,
            'bedrooms': 3,
            'bathrooms': 2,
            'sqft': 1500,
            'year_built': 2000,
            'latitude': 44.9778,  # Minneapolis default
            'longitude': -93.2650,
            'neighborhood': 'Minneapolis',
            'property_type': 'Single Family',
            'listing_status': 'For Sale'
        }
        
        for col, default_val in required_columns.items():
            if col not in df.columns:
                df[col] = default_val
            else:
                # Fill missing values
                df[col] = df[col].fillna(default_val)
        
        # Convert numeric columns
        numeric_columns = ['price', 'bedrooms', 'bathrooms', 'sqft', 'year_built', 
                          'latitude', 'longitude', 'lot_size', 'days_on_market']
        
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
                # Fill NaN with reasonable defaults
                if col == 'price':
                    df[col] = df[col].fillna(350000)
                elif col == 'sqft':
                    df[col] = df[col].fillna(1500)
                elif col == 'bedrooms':
                    df[col] = df[col].fillna(3)
                elif col == 'bathrooms':
                    df[col] = df[col].fillna(2)
                elif col == 'year_built':
                    df[col] = df[col].fillna(2000)
                elif col == 'latitude':
                    df[col] = df[col].fillna(44.9778)
                elif col == 'longitude':
                    df[col] = df[col].fillna(-93.2650)
                else:
                    df[col] = df[col].fillna(0)
        
        # Validate data ranges
        df = df[
            (df['price'] >= 50000) & (df['price'] <= 2000000) &
            (df['sqft'] >= 500) & (df['sqft'] <= 10000) &
            (df['bedrooms'] >= 1) & (df['bedrooms'] <= 10) &
            (df['bathrooms'] >= 1) & (df['bathrooms'] <= 10) &
            (df['year_built'] >= 1900) & (df['year_built'] <= 2025)
        ]
        
        # Calculate price per sqft if not exists
        if 'price_per_sqft' not in df.columns:
            df['price_per_sqft'] = (df['price'] / df['sqft']).round(0)
        
        return df

class EnhancedHouseScorer:
    """Enhanced scoring system without garage requirements"""
    
    def __init__(self):
        self.downtown_minneapolis = (44.9778, -93.2650)
    
    def calculate_score(self, house, preferences, weights):
        """Calculate score based on user preferences (no garage requirement)"""
        
        from geopy.distance import geodesic
        
        scores = {}
        
        # Price score - MORE DISCRIMINATING
        max_budget = preferences['max_budget']
        min_budget = preferences['min_budget']
        
        if house['price'] <= max_budget:
            if house['price'] <= min_budget:
                scores['price'] = 0.75
            else:
                budget_range = max_budget - min_budget
                if budget_range > 0:
                    position = (house['price'] - min_budget) / budget_range
                    if 0.3 <= position <= 0.7:
                        scores['price'] = 0.85 + (0.15 * (1 - abs(position - 0.5) * 4))
                    elif 0.1 <= position <= 0.9:
                        scores['price'] = 0.70 + (0.15 * (1 - abs(position - 0.5) * 2))
                    else:
                        scores['price'] = 0.55 + (0.15 * (1 - abs(position - 0.5)))
                else:
                    scores['price'] = 0.80
        else:
            overage_ratio = (house['price'] - max_budget) / max_budget
            if overage_ratio <= 0.1:
                scores['price'] = 0.60
            elif overage_ratio <= 0.2:
                scores['price'] = 0.40
            else:
                scores['price'] = max(0.1, 0.40 - overage_ratio)
        
        # Commute score
        if 'latitude' in house and 'longitude' in house and house['latitude'] and house['longitude']:
            try:
                house_location = (house['latitude'], house['longitude'])
                distance_miles = geodesic(house_location, self.downtown_minneapolis).miles
                commute_minutes = distance_miles * 2
                
                max_commute = preferences['max_commute']
                
                if commute_minutes <= max_commute * 0.6:
                    scores['commute'] = 0.90 + (0.10 * (1 - commute_minutes / (max_commute * 0.6)))
                elif commute_minutes <= max_commute * 0.8:
                    ratio = (commute_minutes - max_commute * 0.6) / (max_commute * 0.2)
                    scores['commute'] = 0.75 + (0.15 * (1 - ratio))
                elif commute_minutes <= max_commute:
                    ratio = (commute_minutes - max_commute * 0.8) / (max_commute * 0.2)
                    scores['commute'] = 0.55 + (0.20 * (1 - ratio))
                else:
                    over_ratio = (commute_minutes - max_commute) / max_commute
                    scores['commute'] = max(0.1, 0.55 - over_ratio * 0.5)
            except:
                scores['commute'] = 0.40
        else:
            scores['commute'] = 0.40
        
        # Size score
        min_sqft = preferences['min_sqft']
        ideal_sqft = min_sqft * 1.3
        
        if house['sqft'] >= ideal_sqft:
            if house['sqft'] <= ideal_sqft * 1.5:
                scores['size'] = 0.85 + (0.15 * (1 - (house['sqft'] - ideal_sqft) / (ideal_sqft * 0.5)))
            else:
                excess_ratio = (house['sqft'] - ideal_sqft * 1.5) / (ideal_sqft * 0.5)
                scores['size'] = max(0.60, 0.85 - excess_ratio * 0.25)
        elif house['sqft'] >= min_sqft:
            ratio = (house['sqft'] - min_sqft) / (ideal_sqft - min_sqft)
            scores['size'] = 0.65 + (0.20 * ratio)
        else:
            deficit_ratio = (min_sqft - house['sqft']) / min_sqft
            scores['size'] = max(0.15, 0.65 - deficit_ratio * 0.5)
        
        # Age score
        min_year = preferences['min_year_built']
        house_year = house.get('year_built', min_year)
        
        if house_year >= min_year + 10:
            years_new = min(house_year - min_year, 20)
            scores['age'] = 0.80 + (0.20 * (years_new / 20))
        elif house_year >= min_year:
            years_over = house_year - min_year
            scores['age'] = 0.60 + (0.20 * (years_over / 10))
        else:
            years_old = min_year - house_year
            if years_old <= 10:
                scores['age'] = 0.50 - (years_old / 10) * 0.15
            else:
                scores['age'] = max(0.20, 0.35 - (years_old - 10) / 30 * 0.15)
        
        # Bedrooms score
        min_beds = preferences['min_bedrooms']
        if house['bedrooms'] == min_beds:
            scores['bedrooms'] = 0.75
        elif house['bedrooms'] == min_beds + 1:
            scores['bedrooms'] = 0.90
        elif house['bedrooms'] >= min_beds + 2:
            scores['bedrooms'] = 0.85
        else:
            deficit = min_beds - house['bedrooms']
            scores['bedrooms'] = max(0.25, 0.75 - deficit * 0.25)
        
        # Neighborhood score
        preferred_neighborhoods = preferences.get('preferred_neighborhoods', [])
        if not preferred_neighborhoods:
            scores['neighborhood'] = 0.80
        elif house.get('neighborhood', '') in preferred_neighborhoods:
            scores['neighborhood'] = 0.85
        else:
            scores['neighborhood'] = 0.55
        
        # Calculate weighted overall score with normalization
        raw_overall = (
            scores['price'] * weights['price'] +
            scores['commute'] * weights['commute'] +
            scores['size'] * weights['size'] +
            scores['age'] * weights['age'] +
            scores['bedrooms'] * weights['bedrooms'] +
            scores['neighborhood'] * weights['neighborhood']
        )
        
        # Add some randomness to break ties
        import random
        noise = random.uniform(-0.02, 0.02)
        overall_score = max(0.1, min(1.0, raw_overall + noise))
        
        scores['overall'] = overall_score
        
        # More stringent recommendation thresholds
        if overall_score >= 0.88:
            scores['recommendation'] = "🔥 MUST SEE - Perfect Match!"
        elif overall_score >= 0.78:
            scores['recommendation'] = "⭐ HIGHLY RECOMMENDED"
        elif overall_score >= 0.65:
            scores['recommendation'] = "✅ GOOD OPTION"
        elif overall_score >= 0.50:
            scores['recommendation'] = "⚠️ DECENT - Has Trade-offs"
        else:
            scores['recommendation'] = "❌ BELOW THRESHOLD"
        
        return scores

@st.cache_data
def load_comprehensive_house_data():
    """Load house data from all available sources"""
    
    loader = ComprehensiveDataLoader()
    df, file_info = loader.load_all_data()
    
    return df, file_info, loader.data_files

def create_enhanced_preferences_panel():
    """Create enhanced preferences panel without garage filter"""
    
    st.sidebar.markdown('<div class="main-header"><h2>🎯 Your Preferences</h2></div>', unsafe_allow_html=True)
    
    # Load data to get ranges
    df, file_info, data_files = load_comprehensive_house_data()
    
    # Data source info
    if data_files:
        st.sidebar.success(f"🔥 Using {len(data_files)} data sources: {len(df)} houses")
        with st.sidebar.expander(f"📁 Data Sources ({len(data_files)} files)"):
            for file_path in data_files:
                file_houses = file_info.get(file_path, {}).get('houses', 0)
                file_age = file_info.get(file_path, {}).get('modified', None)
                age_str = ""
                if file_age:
                    days_ago = (datetime.now() - file_age).days
                    age_str = f" ({days_ago}d ago)"
                st.write(f"📄 {os.path.basename(file_path)}: {file_houses} houses{age_str}")
    else:
        st.sidebar.error("❌ No data files found")
        return None, None, None
    
    if len(df) == 0:
        st.sidebar.error("❌ No valid house data loaded")
        return None, None, None
    
    # Debug info
    with st.sidebar.expander("🔍 Data Debug Info"):
        st.write(f"📊 **Loaded Data Overview:**")
        st.write(f"   💰 Price: ${df['price'].min():,} - ${df['price'].max():,}")
        st.write(f"   🏠 Bedrooms: {df['bedrooms'].min()} - {df['bedrooms'].max()}")
        st.write(f"   📐 Size: {df['sqft'].min():,} - {df['sqft'].max():,} sqft")
        if 'year_built' in df.columns:
            st.write(f"   📅 Year: {df['year_built'].min()} - {df['year_built'].max()}")
        if 'neighborhood' in df.columns:
            neighborhoods = df['neighborhood'].unique()
            st.write(f"   🏘️ Areas: {len(neighborhoods)} neighborhoods")
            st.write(f"   Top 5: {', '.join(neighborhoods[:5])}")
    
    st.sidebar.markdown("### 💰 Budget & Financial")
    
    # Budget settings
    price_min = int(df['price'].min()) if len(df) > 0 else 100000
    price_max = int(df['price'].max()) if len(df) > 0 else 500000
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        min_budget = st.number_input(
            "Min Budget", 
            min_value=price_min, 
            max_value=price_max,
            value=max(price_min, 200000),
            step=10000,
            format="%d"
        )
    with col2:
        max_budget = st.number_input(
            "Max Budget", 
            min_value=min_budget, 
            max_value=price_max + 200000,
            value=min(400000, price_max + 50000),
            step=10000,
            format="%d"
        )
    
    st.sidebar.markdown("### 🏡 House Requirements")
    
    # House requirements
    bed_min = int(df['bedrooms'].min()) if len(df) > 0 else 1
    bed_max = int(df['bedrooms'].max()) if len(df) > 0 else 5
    
    if bed_max <= bed_min:
        bed_max = bed_min + 3
    
    min_bedrooms = st.sidebar.selectbox(
        "Minimum Bedrooms",
        options=list(range(bed_min, bed_max + 2)),
        index=min(2, len(range(bed_min, bed_max + 2)) - 1)
    )
    
    sqft_min = int(df['sqft'].min()) if len(df) > 0 else 800
    sqft_max = int(df['sqft'].max()) if len(df) > 0 else 3000
    
    if sqft_max <= sqft_min:
        sqft_max = sqft_min + 1000
    
    min_sqft = st.sidebar.slider(
        "Minimum Square Feet",
        min_value=sqft_min,
        max_value=sqft_max + 500,
        value=max(1200, sqft_min),
        step=50
    )
    
    year_min = int(df['year_built'].min()) if 'year_built' in df.columns and len(df) > 0 else 1980
    year_max = int(df['year_built'].max()) if 'year_built' in df.columns and len(df) > 0 else 2025
    
    if year_max <= year_min:
        year_max = year_min + 25
    
    min_year_built = st.sidebar.slider(
        "Minimum Year Built",
        min_value=year_min,
        max_value=year_max,
        value=max(2000, year_min),
        step=5
    )
    
    st.sidebar.markdown("### 📍 Location Preferences")
    
    max_commute = st.sidebar.slider(
        "Max Commute Time (minutes)",
        min_value=15,
        max_value=60,
        value=30,
        step=5
    )
    
    # Neighborhood selection
    neighborhoods = []
    if 'neighborhood' in df.columns:
        neighborhoods = sorted(df['neighborhood'].dropna().unique().tolist())
    
    if neighborhoods:
        preferred_neighborhoods = st.sidebar.multiselect(
            "Preferred Neighborhoods",
            options=neighborhoods,
            default=neighborhoods if len(neighborhoods) <= 10 else neighborhoods[:10]
        )
    else:
        preferred_neighborhoods = []
    
    st.sidebar.markdown("### ⚖️ Scoring Weights")
    st.sidebar.markdown("*Adjust what's most important to you*")
    
    # Scoring weights - removed garage weight
    st.sidebar.markdown("📊 **Importance Weights** (must sum to 100%)")
    
    price_weight = st.sidebar.slider("💰 Price Importance", 0.0, 0.5, 0.30, 0.05)
    commute_weight = st.sidebar.slider("🚗 Commute Importance", 0.0, 0.4, 0.25, 0.05)
    size_weight = st.sidebar.slider("📐 Size Importance", 0.0, 0.3, 0.20, 0.05)
    age_weight = st.sidebar.slider("📅 Age Importance", 0.0, 0.3, 0.15, 0.05)
    
    # Auto-calculate remaining weights (removed garage from calculation)
    remaining = 1.0 - (price_weight + commute_weight + size_weight + age_weight)
    bedrooms_weight = remaining * 0.6
    neighborhood_weight = remaining * 0.4
    
    # Show the auto-calculated weights
    st.sidebar.markdown(f"📊 **Auto-calculated weights:**")
    st.sidebar.caption(f"Bedrooms: {bedrooms_weight:.2f}")
    st.sidebar.caption(f"Neighborhood: {neighborhood_weight:.2f}")
    
    # Total weight check
    total_weight = price_weight + commute_weight + size_weight + age_weight + bedrooms_weight + neighborhood_weight
    if abs(total_weight - 1.0) > 0.01:
        st.sidebar.warning(f"⚠️ Weights sum to {total_weight:.2f} (should be 1.0)")
    else:
        st.sidebar.success(f"✅ Weights sum to {total_weight:.2f}")
    
    preferences = {
        'min_budget': min_budget,
        'max_budget': max_budget,
        'min_bedrooms': min_bedrooms,
        'min_sqft': min_sqft,
        'min_year_built': min_year_built,
        'max_commute': max_commute,
        'preferred_neighborhoods': preferred_neighborhoods
    }
    
    weights = {
        'price': price_weight,
        'commute': commute_weight,
        'size': size_weight,
        'age': age_weight,
        'bedrooms': bedrooms_weight,
        'neighborhood': neighborhood_weight
    }
    
    return preferences, weights, df

def apply_enhanced_scoring(df, preferences, weights):
    """Apply enhanced scoring to all houses (no garage filtering)"""
    
    scorer = EnhancedHouseScorer()
    
    st.info(f"🧠 **Recalculating scores** for {len(df)} houses based on your preferences...")
    
    # Show current preferences being used
    with st.expander("🔍 Current Scoring Parameters"):
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Your Preferences:**")
            st.write(f"💰 Budget: ${preferences['min_budget']:,} - ${preferences['max_budget']:,}")
            st.write(f"🏠 Min Bedrooms: {preferences['min_bedrooms']}")
            st.write(f"📐 Min Size: {preferences['min_sqft']:,} sqft")
            st.write(f"📅 Min Year: {preferences['min_year_built']}")
            st.write(f"🚗 Max Commute: {preferences['max_commute']} min")
            if preferences['preferred_neighborhoods']:
                st.write(f"🏘️ Preferred Areas: {len(preferences['preferred_neighborhoods'])} selected")
        
        with col2:
            st.write("**Scoring Weights:**")
            st.write(f"💰 Price: {weights['price']:.0%}")
            st.write(f"🚗 Commute: {weights['commute']:.0%}")
            st.write(f"📐 Size: {weights['size']:.0%}")
            st.write(f"📅 Age: {weights['age']:.0%}")
            st.write(f"🏠 Bedrooms: {weights['bedrooms']:.0%}")
            st.write(f"🏘️ Neighborhood: {weights['neighborhood']:.0%}")
    
    with st.spinner("🎯 Recalculating scores based on your preferences..."):
        scored_houses = []
        
        progress_bar = st.progress(0)
        total_houses = len(df)
        
        for count, (idx, house) in enumerate(df.iterrows()):
            house_dict = house.to_dict()
            scores = scorer.calculate_score(house_dict, preferences, weights)
            
            # Combine original data with new scores
            scored_house = house_dict.copy()
            scored_house.update({
                'overall_score': scores['overall'],
                'price_score': scores['price'],
                'commute_score': scores['commute'],
                'size_score': scores['size'],
                'age_score': scores['age'],
                'bedrooms_score': scores['bedrooms'],
                'neighborhood_score': scores['neighborhood'],
                'recommendation': scores['recommendation']
            })
            
            scored_houses.append(scored_house)
            
            # Update progress using count instead of idx
            progress_value = min(1.0, (count + 1) / total_houses)
            progress_bar.progress(progress_value)
        
        progress_bar.empty()
    
    scored_df = pd.DataFrame(scored_houses)
    scored_df = scored_df.sort_values('overall_score', ascending=False)
    
    st.success(f"✅ **Scoring complete!** Houses are now ranked by fit to your preferences.")
    
    return scored_df

def display_enhanced_results(scored_df, preferences):
    """Display the enhanced scored results (no garage filtering)"""
    
    # Show all houses that meet basic criteria, let scoring handle the rest
    st.info(f"📊 Showing {len(scored_df)} houses ranked by your preferences")
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🏠 Total Houses", len(scored_df))
    
    with col2:
        if len(scored_df) > 0:
            avg_score = scored_df['overall_score'].mean()
            st.metric("🎯 Avg Score", f"{avg_score:.1%}")
        else:
            st.metric("🎯 Avg Score", "N/A")
    
    with col3:
        if len(scored_df) > 0:
            avg_price = scored_df['price'].mean()
            st.metric("💰 Avg Price", f"${avg_price:,.0f}")
        else:
            st.metric("💰 Avg Price", "N/A")
    
    with col4:
        high_score_count = len(scored_df[scored_df['overall_score'] >= 0.75])
        st.metric("🔥 High-Score Houses", high_score_count)
    
    # Show score distribution
    if len(scored_df) > 0:
        score_ranges = {
            "🔥 Excellent (85%+)": len(scored_df[scored_df['overall_score'] >= 0.85]),
            "⭐ Very Good (75-84%)": len(scored_df[(scored_df['overall_score'] >= 0.75) & (scored_df['overall_score'] < 0.85)]),
            "✅ Good (65-74%)": len(scored_df[(scored_df['overall_score'] >= 0.65) & (scored_df['overall_score'] < 0.75)]),
            "⚠️ Fair (50-64%)": len(scored_df[(scored_df['overall_score'] >= 0.50) & (scored_df['overall_score'] < 0.65)]),
            "❌ Poor (<50%)": len(scored_df[scored_df['overall_score'] < 0.50])
        }
        
        col_score1, col_score2, col_score3, col_score4, col_score5 = st.columns(5)
        
        with col_score1:
            st.metric("🔥 Excellent", score_ranges["🔥 Excellent (85%+)"])
        with col_score2:
            st.metric("⭐ Very Good", score_ranges["⭐ Very Good (75-84%)"])
        with col_score3:
            st.metric("✅ Good", score_ranges["✅ Good (65-74%)"])
        with col_score4:
            st.metric("⚠️ Fair", score_ranges["⚠️ Fair (50-64%)"])
        with col_score5:
            st.metric("❌ Poor", score_ranges["❌ Poor (<50%)"])
    
    # Show preference impact
    with st.expander("🎯 How Your Preferences Affect Scoring"):
        st.write("**Your current preferences:**")
        st.write(f"💰 Budget: ${preferences['min_budget']:,} - ${preferences['max_budget']:,}")
        st.write(f"🏠 Bedrooms: {preferences['min_bedrooms']}+")
        st.write(f"📐 Size: {preferences['min_sqft']:,}+ sqft")
        st.write(f"📅 Year: {preferences['min_year_built']}+")
        st.write(f"🚗 Commute: {preferences['max_commute']} min max")
        
        if preferences['preferred_neighborhoods']:
            st.write(f"🏘️ Preferred Areas: {len(preferences['preferred_neighborhoods'])} neighborhoods")
        
        st.write("**Note:** Houses outside your preferred ranges get LOWER scores, not filtered out. This way you can see all options ranked by fit to your preferences!")
    
    # Show top recommendations with better visibility
    st.markdown("### 🏆 All Houses Ranked by Your Preferences")
    
    # Add a toggle for showing all vs top 15
    show_all_houses = st.checkbox("📋 Show all houses (not just top 15)", value=False)
    display_count = len(scored_df) if show_all_houses else min(15, len(scored_df))
    
    for idx, (_, house) in enumerate(scored_df.head(display_count).iterrows()):
        score = house['overall_score']
        
        # Choose color based on score
        if score >= 0.85:
            score_class = "score-high"
        elif score >= 0.65:
            score_class = "score-medium"
        else:
            score_class = "score-low"
        
        with st.expander(
            f"#{idx+1} - {house['address']} - Score: {score:.1%} - ${house['price']:,}",
            expanded=(idx < 3)
        ):
            col_a, col_b, col_c = st.columns([2, 1, 1])
            
            with col_a:
                st.markdown(f'<div class="metric-container {score_class}">', unsafe_allow_html=True)
                st.write("**🏠 Property Details**")
                st.write(f"📍 **Address**: {house['address']}")
                st.write(f"💰 **Price**: ${house['price']:,}")
                st.write(f"🏠 **Layout**: {house['bedrooms']} bed, {house.get('bathrooms', 'N/A')} bath")
                st.write(f"📐 **Size**: {house['sqft']} sqft")
                if 'year_built' in house:
                    st.write(f"📅 **Built**: {house['year_built']}")
                if 'neighborhood' in house:
                    st.write(f"🏘️ **Area**: {house['neighborhood']}")
                if 'source_file' in house:
                    st.write(f"📁 **Source**: {os.path.basename(house['source_file'])}")
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Zillow link
                if 'listing_url' in house and house['listing_url']:
                    url = house['listing_url']
                    if 'zillow.com' in str(url):
                        st.markdown(f"🔗 **[View on Zillow]({url})**")
                    else:
                        search_query = house['address'].replace(' ', '+').replace(',', '')
                        search_url = f"https://www.zillow.com/homes/{search_query}_rb/"
                        st.markdown(f"🔍 **[Search on Zillow]({search_url})**")
            
            with col_b:
                st.write("**🎯 Score Breakdown**")
                st.write(f"**Overall: {score:.1%}**")
                st.write(f"💰 Price: {house.get('price_score', 0):.2f}")
                st.write(f"🚗 Commute: {house.get('commute_score', 0):.2f}")
                st.write(f"📐 Size: {house.get('size_score', 0):.2f}")
                st.write(f"📅 Age: {house.get('age_score', 0):.2f}")
                st.write(f"🏠 Bedrooms: {house.get('bedrooms_score', 0):.2f}")
                st.write(f"🏘️ Area: {house.get('neighborhood_score', 0):.2f}")
            
            with col_c:
                # Better score visualization - horizontal bars
                st.write("**🎯 Visual Scores**")
                
                # Overall score with color coding
                score_color = "#28a745" if score >= 0.85 else "#ffc107" if score >= 0.65 else "#dc3545"
                st.markdown(f"""
                <div style="background: {score_color}; padding: 10px; border-radius: 5px; text-align: center; margin-bottom: 10px;">
                    <h3 style="color: white; margin: 0;">Overall: {score:.1%}</h3>
                </div>
                """, unsafe_allow_html=True)
                
                # Individual score bars
                score_components = [
                    ("💰 Price", house.get('price_score', 0), "#e74c3c"),
                    ("🚗 Commute", house.get('commute_score', 0), "#3498db"),
                    ("📐 Size", house.get('size_score', 0), "#2ecc71"),
                    ("📅 Age", house.get('age_score', 0), "#f39c12"),
                    ("🏠 Bedrooms", house.get('bedrooms_score', 0), "#9b59b6"),
                    ("🏘️ Area", house.get('neighborhood_score', 0), "#34495e")
                ]
                
                for label, value, color in score_components:
                    bar_width = int(value * 100)
                    st.markdown(f"""
                    <div style="margin: 5px 0;">
                        <div style="display: flex; align-items: center; justify-content: space-between;">
                            <span style="font-size: 12px; font-weight: bold;">{label}</span>
                            <span style="font-size: 12px; font-weight: bold;">{value:.2f}</span>
                        </div>
                        <div style="background: #e0e0e0; border-radius: 10px; height: 8px; margin: 2px 0;">
                            <div style="background: {color}; height: 8px; width: {bar_width}%; border-radius: 10px;"></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Recommendation with better styling
                rec_colors = {
                    "🔥 MUST SEE - Perfect Match!": "#28a745",
                    "⭐ HIGHLY RECOMMENDED": "#17a2b8", 
                    "✅ GOOD OPTION": "#ffc107",
                    "⚠️ DECENT - Has Trade-offs": "#fd7e14",
                    "❌ BELOW THRESHOLD": "#dc3545"
                }
                
                rec_color = rec_colors.get(house['recommendation'], "#6c757d")
                st.markdown(f"""
                <div style="background: {rec_color}; color: white; padding: 8px; border-radius: 5px; text-align: center; margin-top: 10px; font-weight: bold; font-size: 14px;">
                    {house['recommendation']}
                </div>
                """, unsafe_allow_html=True)
    
    # Analysis charts
    st.markdown("### 📊 Market Analysis")
    
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        # Score distribution with better sizing
        fig_scores = px.histogram(
            scored_df, 
            x='overall_score',
            title="🎯 Score Distribution",
            nbins=10,
            color_discrete_sequence=['#667eea'],
            labels={'overall_score': 'Overall Score', 'count': 'Number of Houses'}
        )
        fig_scores.update_layout(
            height=500,
            title_font_size=16,
            showlegend=False,
            xaxis_title_font_size=14,
            yaxis_title_font_size=14
        )
        st.plotly_chart(fig_scores, use_container_width=True)
    
    with col_chart2:
        # Price vs Score with better sizing
        fig_price_score = px.scatter(
            scored_df,
            x='price',
            y='overall_score',
            size='sqft',
            color='overall_score',
            title="💰 Price vs Score",
            color_continuous_scale='RdYlGn',
            labels={'price': 'Price ($)', 'overall_score': 'Overall Score', 'sqft': 'Square Feet'},
            hover_data=['address', 'bedrooms', 'neighborhood']
        )
        fig_price_score.update_layout(
            height=500,
            title_font_size=16,
            xaxis_title_font_size=14,
            yaxis_title_font_size=14
        )
        st.plotly_chart(fig_price_score, use_container_width=True)
    
    # Neighborhood analysis if available
    if 'neighborhood' in scored_df.columns:
        st.markdown("### 🏘️ Neighborhood Analysis")
        
        neighborhood_stats = scored_df.groupby('neighborhood').agg({
            'overall_score': 'mean',
            'price': 'mean',
            'address': 'count'
        }).round(3)
        neighborhood_stats.columns = ['Avg Score', 'Avg Price', 'House Count']
        neighborhood_stats = neighborhood_stats.sort_values('Avg Score', ascending=False)
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_neighborhood = px.bar(
                neighborhood_stats.head(10),
                y=neighborhood_stats.head(10).index,
                x='Avg Score',
                orientation='h',
                title="🏘️ Top Neighborhoods by Average Score",
                color='Avg Score',
                color_continuous_scale='RdYlGn'
            )
            fig_neighborhood.update_layout(height=400)
            st.plotly_chart(fig_neighborhood, use_container_width=True)
        
        with col2:
            st.write("**📊 Neighborhood Summary:**")
            st.dataframe(neighborhood_stats, use_container_width=True)
    
    # Add a summary table for quick scanning
    st.markdown("### 📋 Quick Comparison Table")
    
    # Create a clean summary table
    summary_cols = ['address', 'price', 'overall_score', 'bedrooms', 'sqft', 'neighborhood', 'recommendation']
    available_cols = [col for col in summary_cols if col in scored_df.columns]
    summary_df = scored_df[available_cols].head(20).copy()
    
    # Format for better display
    if 'price' in summary_df.columns:
        summary_df['price'] = summary_df['price'].apply(lambda x: f"${x:,.0f}")
    if 'overall_score' in summary_df.columns:
        summary_df['overall_score'] = summary_df['overall_score'].apply(lambda x: f"{x:.1%}")
    if 'sqft' in summary_df.columns:
        summary_df['sqft'] = summary_df['sqft'].apply(lambda x: f"{x:,.0f}")
    
    # Rename columns for display
    column_renames = {
        'address': 'Address', 
        'price': 'Price', 
        'overall_score': 'Score', 
        'bedrooms': 'Beds', 
        'sqft': 'Sq Ft', 
        'neighborhood': 'Area', 
        'recommendation': 'Recommendation'
    }
    
    summary_df = summary_df.rename(columns=column_renames)
    
    st.dataframe(
        summary_df,
        use_container_width=True,
        height=600
    )

def main():
    """Main enhanced dashboard function"""
    
    st.markdown('<div class="main-header"><h1>🏠 AI House Hunter - Enhanced Data Integration</h1><p>Access ALL your Zillow data sources with intelligent scoring!</p></div>', unsafe_allow_html=True)
    
    # Create enhanced preferences panel
    preferences, weights, df = create_enhanced_preferences_panel()
    
    if preferences is None:
        st.error("❌ No data available. Please ensure you have house data files in your directory.")
        st.info("""
        **Looking for these data files:**
        - real_scored_houses.csv
        - real_zillow_data.csv 
        - comprehensive_houses_*.csv
        - zillow_houses_*.csv
        - ai_house_analysis.csv
        - collected_houses.csv
        
        Run your data collectors to generate these files.
        """)
        return
    
    # Add refresh button
    if st.sidebar.button("🔄 Recalculate All Scores", type="primary"):
        st.cache_data.clear()
        st.rerun()
    
    # Apply enhanced scoring
    scored_df = apply_enhanced_scoring(df, preferences, weights)
    
    # Display enhanced results
    display_enhanced_results(scored_df, preferences)
    
    # Show preferences summary
    with st.expander("📋 Current Preferences Summary"):
        st.json(preferences)
    
    # Data source summary
    with st.expander("📁 Data Sources Summary"):
        df, file_info, data_files = load_comprehensive_house_data()
        
        st.write(f"**Loaded {len(data_files)} data files:**")
        for file_path in data_files:
            info = file_info.get(file_path, {})
            st.write(f"• **{os.path.basename(file_path)}**: {info.get('houses', 0)} houses, {info.get('size_kb', 0):.1f}KB")
        
        st.write(f"**Total unique houses:** {len(df)}")
        
        # Show column availability
        important_columns = ['price', 'bedrooms', 'sqft', 'year_built', 'neighborhood', 'latitude', 'longitude']
        available_columns = [col for col in important_columns if col in df.columns]
        missing_columns = [col for col in important_columns if col not in df.columns]
        
        if available_columns:
            st.write(f"**✅ Available columns:** {', '.join(available_columns)}")
        if missing_columns:
            st.write(f"**❌ Missing columns:** {', '.join(missing_columns)}")

if __name__ == "__main__":
    main()