# dynamic_dashboard.py
# Interactive dashboard with dynamic parameter selection and real-time scoring

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime
import os
import json

# Page config
st.set_page_config(
    page_title="AI House Hunter - Dynamic", 
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

class DynamicHouseScorer:
    """Real-time scoring system that updates based on user parameters"""
    
    def __init__(self):
        self.downtown_minneapolis = (44.9778, -93.2650)
    
    def calculate_score(self, house, preferences, weights):
        """Calculate score based on current user preferences and weights with realistic distribution"""
        
        from geopy.distance import geodesic
        
        scores = {}
        
        # Price score - MORE DISCRIMINATING
        max_budget = preferences['max_budget']
        min_budget = preferences['min_budget']
        
        if house['price'] <= max_budget:
            if house['price'] <= min_budget:
                # Below min budget gets good but not perfect score (might be too cheap = issues)
                scores['price'] = 0.75
            else:
                # Sweet spot scoring - best score in middle of range
                budget_range = max_budget - min_budget
                if budget_range > 0:
                    # Find position in range (0 to 1)
                    position = (house['price'] - min_budget) / budget_range
                    # Bell curve: best score around 30-70% of budget range
                    if 0.3 <= position <= 0.7:
                        scores['price'] = 0.85 + (0.15 * (1 - abs(position - 0.5) * 4))  # 85-100%
                    elif 0.1 <= position <= 0.9:
                        scores['price'] = 0.70 + (0.15 * (1 - abs(position - 0.5) * 2))  # 70-85%
                    else:
                        scores['price'] = 0.55 + (0.15 * (1 - abs(position - 0.5)))      # 55-70%
                else:
                    scores['price'] = 0.80
        else:
            # Over budget gets progressively worse score
            overage_ratio = (house['price'] - max_budget) / max_budget
            if overage_ratio <= 0.1:  # 10% over
                scores['price'] = 0.60
            elif overage_ratio <= 0.2:  # 20% over
                scores['price'] = 0.40
            else:
                scores['price'] = max(0.1, 0.40 - overage_ratio)
        
        # Commute score - MORE REALISTIC
        if 'latitude' in house and 'longitude' in house and house['latitude'] and house['longitude']:
            try:
                house_location = (house['latitude'], house['longitude'])
                distance_miles = geodesic(house_location, self.downtown_minneapolis).miles
                commute_minutes = distance_miles * 2
                
                max_commute = preferences['max_commute']
                
                if commute_minutes <= max_commute * 0.6:  # 60% of max = excellent
                    scores['commute'] = 0.90 + (0.10 * (1 - commute_minutes / (max_commute * 0.6)))
                elif commute_minutes <= max_commute * 0.8:  # 80% of max = very good
                    ratio = (commute_minutes - max_commute * 0.6) / (max_commute * 0.2)
                    scores['commute'] = 0.75 + (0.15 * (1 - ratio))
                elif commute_minutes <= max_commute:  # Within max = acceptable
                    ratio = (commute_minutes - max_commute * 0.8) / (max_commute * 0.2)
                    scores['commute'] = 0.55 + (0.20 * (1 - ratio))
                else:
                    # Over max commute
                    over_ratio = (commute_minutes - max_commute) / max_commute
                    scores['commute'] = max(0.1, 0.55 - over_ratio * 0.5)
            except:
                scores['commute'] = 0.40  # Lower default for missing data
        else:
            scores['commute'] = 0.40
        
        # Size score - MORE NUANCED
        min_sqft = preferences['min_sqft']
        ideal_sqft = min_sqft * 1.3  # 30% bigger than minimum is ideal
        
        if house['sqft'] >= ideal_sqft:
            # Too big can be bad (harder to maintain, expensive utilities)
            if house['sqft'] <= ideal_sqft * 1.5:
                scores['size'] = 0.85 + (0.15 * (1 - (house['sqft'] - ideal_sqft) / (ideal_sqft * 0.5)))
            else:
                # Getting too big
                excess_ratio = (house['sqft'] - ideal_sqft * 1.5) / (ideal_sqft * 0.5)
                scores['size'] = max(0.60, 0.85 - excess_ratio * 0.25)
        elif house['sqft'] >= min_sqft:
            # Between minimum and ideal
            ratio = (house['sqft'] - min_sqft) / (ideal_sqft - min_sqft)
            scores['size'] = 0.65 + (0.20 * ratio)
        else:
            # Below minimum
            deficit_ratio = (min_sqft - house['sqft']) / min_sqft
            scores['size'] = max(0.15, 0.65 - deficit_ratio * 0.5)
        
        # Age score - MORE REALISTIC DEPRECIATION
        min_year = preferences['min_year_built']
        current_year = 2025
        house_year = house.get('year_built', min_year)
        
        if house_year >= min_year + 10:  # 10+ years newer than minimum
            # Very new houses
            years_new = min(house_year - min_year, 20)  # Cap at 20 years difference
            scores['age'] = 0.80 + (0.20 * (years_new / 20))
        elif house_year >= min_year:
            # Within acceptable range
            years_over = house_year - min_year
            scores['age'] = 0.60 + (0.20 * (years_over / 10))
        else:
            # Older than preferred
            years_old = min_year - house_year
            if years_old <= 10:
                scores['age'] = 0.50 - (years_old / 10) * 0.15
            else:
                scores['age'] = max(0.20, 0.35 - (years_old - 10) / 30 * 0.15)
        
        # Bedrooms score - STRICTER
        min_beds = preferences['min_bedrooms']
        if house['bedrooms'] == min_beds:
            scores['bedrooms'] = 0.75  # Meets minimum but not excellent
        elif house['bedrooms'] == min_beds + 1:
            scores['bedrooms'] = 0.90  # One extra bedroom is ideal
        elif house['bedrooms'] >= min_beds + 2:
            scores['bedrooms'] = 0.85  # Too many bedrooms can be wasteful
        else:
            # Fewer than minimum
            deficit = min_beds - house['bedrooms']
            scores['bedrooms'] = max(0.25, 0.75 - deficit * 0.25)
        
        # Garage score - BINARY BUT IMPACT VARIES
        if preferences['needs_garage']:
            scores['garage'] = 0.85 if house.get('has_garage', False) else 0.30
        else:
            scores['garage'] = 0.90 if house.get('has_garage', False) else 0.75
        
        # Neighborhood score - MORE VARIED
        preferred_neighborhoods = preferences.get('preferred_neighborhoods', [])
        if not preferred_neighborhoods:
            scores['neighborhood'] = 0.80  # Neutral when no preference
        elif house.get('neighborhood', '') in preferred_neighborhoods:
            # Even preferred neighborhoods aren't perfect
            scores['neighborhood'] = 0.85
        else:
            scores['neighborhood'] = 0.55  # Non-preferred but not terrible
        
        # Calculate weighted overall score with normalization
        raw_overall = (
            scores['price'] * weights['price'] +
            scores['commute'] * weights['commute'] +
            scores['size'] * weights['size'] +
            scores['age'] * weights['age'] +
            scores['bedrooms'] * weights['bedrooms'] +
            scores['garage'] * weights['garage'] +
            scores['neighborhood'] * weights['neighborhood']
        )
        
        # Add some randomness to break ties and create more realistic distribution
        import random
        noise = random.uniform(-0.02, 0.02)  # ±2% random variation
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
def load_house_data():
    """Load house data"""
    
    data_files = [
        'real_scored_houses.csv',
        'real_zillow_data.csv',
        'comprehensive_houses_*.csv',
        'ai_house_analysis.csv'
    ]
    
    for filename_pattern in data_files:
        if '*' in filename_pattern:
            import glob
            files = glob.glob(filename_pattern)
            if files:
                filename = max(files, key=os.path.getctime)
            else:
                continue
        else:
            filename = filename_pattern
        
        if os.path.exists(filename):
            try:
                df = pd.read_csv(filename)
                required_cols = ['address', 'price', 'bedrooms', 'sqft']
                if all(col in df.columns for col in required_cols):
                    return df, filename
            except:
                continue
    
    # Fallback sample data
    sample_data = {
        'address': [
            '4125 Fernbrook Ln, Plymouth, MN 55446',
            '8945 Tamarack Dr, Woodbury, MN 55125', 
            '12567 Elm Creek Blvd, Maple Grove, MN 55369',
            '2834 Northern Pine Dr, Blaine, MN 55449',
            '1567 Victoria St, Roseville, MN 55113'
        ],
        'price': [349900, 329000, 389000, 298000, 365000],
        'bedrooms': [3, 4, 3, 3, 3],
        'bathrooms': [2.5, 2.5, 2, 2, 2],
        'sqft': [1456, 1620, 1385, 1344, 1298],
        'year_built': [2014, 2016, 2018, 2011, 2009],
        'neighborhood': ['Plymouth', 'Woodbury', 'Maple Grove', 'Blaine', 'Roseville'],
        'has_garage': [True, True, True, True, True],
        'latitude': [45.0123, 44.9234, 45.0697, 45.1608, 45.0061],
        'longitude': [-93.4501, -92.9591, -93.4568, -93.2349, -93.1567],
        'listing_url': [
            'https://www.zillow.com/homedetails/sample1',
            'https://www.zillow.com/homedetails/sample2', 
            'https://www.zillow.com/homedetails/sample3',
            'https://www.zillow.com/homedetails/sample4',
            'https://www.zillow.com/homedetails/sample5'
        ]
    }
    
    return pd.DataFrame(sample_data), 'sample_data'

def create_preferences_panel():
    """Create dynamic preferences panel"""
    
    st.sidebar.markdown('<div class="main-header"><h2>🎯 Your Preferences</h2></div>', unsafe_allow_html=True)
    
    # Load data to get ranges
    df, data_source = load_house_data()
    
    # Data source info with debug details
    if 'real_' in data_source:
        st.sidebar.success(f"🔥 Using Real Data: {len(df)} houses")
    else:
        st.sidebar.info(f"🎭 Sample Data: {len(df)} houses")
    
    # Debug info
    with st.sidebar.expander("🔍 Data Debug Info"):
        st.write(f"📊 **Data ranges:**")
        st.write(f"   💰 Price: ${df['price'].min():,} - ${df['price'].max():,}")
        st.write(f"   🏠 Bedrooms: {df['bedrooms'].min()} - {df['bedrooms'].max()}")
        st.write(f"   📐 Size: {df['sqft'].min():,} - {df['sqft'].max():,} sqft")
        if 'year_built' in df.columns:
            st.write(f"   📅 Year: {df['year_built'].min()} - {df['year_built'].max()}")
        if 'neighborhood' in df.columns:
            neighborhoods = df['neighborhood'].unique()
            st.write(f"   🏘️ Areas: {', '.join(neighborhoods[:3])}{'...' if len(neighborhoods) > 3 else ''}")
    
    st.sidebar.markdown("### 💰 Budget & Financial")
    
    # Budget settings
    price_min = int(df['price'].min())
    price_max = int(df['price'].max())
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        min_budget = st.number_input(
            "Min Budget", 
            min_value=price_min, 
            max_value=price_max,
            value=price_min,
            step=10000,
            format="%d"
        )
    with col2:
        max_budget = st.number_input(
            "Max Budget", 
            min_value=min_budget, 
            max_value=price_max + 100000,
            value=min(400000, price_max),
            step=10000,
            format="%d"
        )
    
    st.sidebar.markdown("### 🏡 House Requirements")
    
    # House requirements
    bed_min = int(df['bedrooms'].min())
    bed_max = int(df['bedrooms'].max())
    
    # Fix for when min and max are the same
    if bed_max <= bed_min:
        bed_max = bed_min + 3  # Add 3 bedroom range
    
    min_bedrooms = st.sidebar.selectbox(
        "Minimum Bedrooms",
        options=list(range(bed_min, bed_max + 2)),
        index=min(2, len(range(bed_min, bed_max + 2)) - 1)
    )
    
    sqft_min = int(df['sqft'].min())
    sqft_max = int(df['sqft'].max())
    
    # Fix for when min and max are the same
    if sqft_max <= sqft_min:
        sqft_max = sqft_min + 1000  # Add 1000 sqft range
    
    min_sqft = st.sidebar.slider(
        "Minimum Square Feet",
        min_value=sqft_min,
        max_value=sqft_max + 500,
        value=max(1200, sqft_min),
        step=50
    )
    
    year_min = int(df['year_built'].min()) if 'year_built' in df.columns else 1990
    year_max = int(df['year_built'].max()) if 'year_built' in df.columns else 2025
    
    # Fix for when min and max are the same
    if year_max <= year_min:
        year_max = year_min + 25  # Add 25 years range
    
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
    neighborhoods = df['neighborhood'].unique().tolist() if 'neighborhood' in df.columns else []
    if neighborhoods:
        preferred_neighborhoods = st.sidebar.multiselect(
            "Preferred Neighborhoods",
            options=neighborhoods,
            default=neighborhoods
        )
    else:
        preferred_neighborhoods = []
    
    st.sidebar.markdown("### ⚙️ Features")
    
    needs_garage = st.sidebar.checkbox("Must have garage", value=True)
    
    st.sidebar.markdown("### ⚖️ Scoring Weights")
    st.sidebar.markdown("*Adjust what's most important to you*")
    
    # Scoring weights with constraint that they sum to 1
    st.sidebar.markdown("📊 **Importance Weights** (must sum to 100%)")
    
    price_weight = st.sidebar.slider("💰 Price Importance", 0.0, 0.5, 0.25, 0.05)
    commute_weight = st.sidebar.slider("🚗 Commute Importance", 0.0, 0.4, 0.20, 0.05)
    size_weight = st.sidebar.slider("📐 Size Importance", 0.0, 0.3, 0.15, 0.05)
    age_weight = st.sidebar.slider("📅 Age Importance", 0.0, 0.3, 0.15, 0.05)
    
    # Auto-calculate remaining weights
    remaining = 1.0 - (price_weight + commute_weight + size_weight + age_weight)
    bedrooms_weight = remaining * 0.4
    garage_weight = remaining * 0.3
    neighborhood_weight = remaining * 0.3
    
    # Show the auto-calculated weights
    st.sidebar.markdown(f"📊 **Auto-calculated weights:**")
    st.sidebar.caption(f"Bedrooms: {bedrooms_weight:.2f}")
    st.sidebar.caption(f"Garage: {garage_weight:.2f}")
    st.sidebar.caption(f"Neighborhood: {neighborhood_weight:.2f}")
    
    # Total weight check
    total_weight = price_weight + commute_weight + size_weight + age_weight + bedrooms_weight + garage_weight + neighborhood_weight
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
        'preferred_neighborhoods': preferred_neighborhoods,
        'needs_garage': needs_garage
    }
    
    weights = {
        'price': price_weight,
        'commute': commute_weight,
        'size': size_weight,
        'age': age_weight,
        'bedrooms': bedrooms_weight,
        'garage': garage_weight,
        'neighborhood': neighborhood_weight
    }
    
    return preferences, weights, df

def apply_dynamic_scoring(df, preferences, weights):
    """Apply dynamic scoring to all houses"""
    
    scorer = DynamicHouseScorer()
    
    # Show what's happening
    st.info(f"🧠 **Recalculating scores** for {len(df)} houses based on your current preferences...")
    
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
            st.write(f"🅿️ Garage: {'Required' if preferences['needs_garage'] else 'Optional'}")
        
        with col2:
            st.write("**Scoring Weights:**")
            st.write(f"💰 Price: {weights['price']:.0%}")
            st.write(f"🚗 Commute: {weights['commute']:.0%}")
            st.write(f"📐 Size: {weights['size']:.0%}")
            st.write(f"📅 Age: {weights['age']:.0%}")
            st.write(f"🏠 Bedrooms: {weights['bedrooms']:.0%}")
            st.write(f"🅿️ Garage: {weights['garage']:.0%}")
            st.write(f"🏘️ Neighborhood: {weights['neighborhood']:.0%}")
    
    with st.spinner("🎯 Recalculating scores based on your preferences..."):
        scored_houses = []
        
        progress_bar = st.progress(0)
        for idx, house in df.iterrows():
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
                'garage_score': scores['garage'],
                'neighborhood_score': scores['neighborhood'],
                'recommendation': scores['recommendation']
            })
            
            scored_houses.append(scored_house)
            
            # Update progress
            progress_bar.progress((idx + 1) / len(df))
        
        progress_bar.empty()
    
    scored_df = pd.DataFrame(scored_houses)
    scored_df = scored_df.sort_values('overall_score', ascending=False)
    
    st.success(f"✅ **Scoring complete!** Houses are now ranked by fit to your preferences.")
    
    return scored_df

def display_results(scored_df, preferences):
    """Display the dynamically scored results"""
    
    # Apply MINIMAL filtering - only hard requirements
    filtered_df = scored_df.copy()
    
    # Only filter for absolute deal-breakers
    if preferences['needs_garage']:
        garage_count_before = len(filtered_df)
        filtered_df = filtered_df[filtered_df.get('has_garage', False) == True]
        garage_count_after = len(filtered_df)
        if garage_count_before != garage_count_after:
            st.info(f"🚗 Filtered out {garage_count_before - garage_count_after} houses without garages")
    
    # Show all houses that meet basic criteria, let scoring handle the rest
    st.info(f"📊 Showing {len(filtered_df)} houses ranked by your preferences (scores recalculated based on your settings)")
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🏠 Total Houses", len(filtered_df))
    
    with col2:
        if len(filtered_df) > 0:
            avg_score = filtered_df['overall_score'].mean()
            st.metric("🎯 Avg Score", f"{avg_score:.1%}")
        else:
            st.metric("🎯 Avg Score", "N/A")
    
    with col3:
        if len(filtered_df) > 0:
            avg_price = filtered_df['price'].mean()
            st.metric("💰 Avg Price", f"${avg_price:,.0f}")
        else:
            st.metric("💰 Avg Price", "N/A")
    
    with col4:
        high_score_count = len(filtered_df[filtered_df['overall_score'] >= 0.75])
        st.metric("🔥 High-Score Houses", high_score_count)
    
    # Show filter impact
    if len(filtered_df) > 0:
        score_ranges = {
            "🔥 Excellent (85%+)": len(filtered_df[filtered_df['overall_score'] >= 0.85]),
            "⭐ Very Good (75-84%)": len(filtered_df[(filtered_df['overall_score'] >= 0.75) & (filtered_df['overall_score'] < 0.85)]),
            "✅ Good (65-74%)": len(filtered_df[(filtered_df['overall_score'] >= 0.65) & (filtered_df['overall_score'] < 0.75)]),
            "⚠️ Fair (50-64%)": len(filtered_df[(filtered_df['overall_score'] >= 0.50) & (filtered_df['overall_score'] < 0.65)]),
            "❌ Poor (<50%)": len(filtered_df[filtered_df['overall_score'] < 0.50])
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
    
    if len(filtered_df) == 0:
        st.warning("❌ No houses match your HARD requirements (garage, etc). Try unchecking 'Must have garage' or adjusting other hard filters.")
        return
    
    # Show preference impact
    with st.expander("🎯 How Your Preferences Affect Scoring"):
        st.write("**Your current preferences:**")
        st.write(f"💰 Budget: ${preferences['min_budget']:,} - ${preferences['max_budget']:,}")
        st.write(f"🏠 Bedrooms: {preferences['min_bedrooms']}+")
        st.write(f"📐 Size: {preferences['min_sqft']:,}+ sqft")
        st.write(f"📅 Year: {preferences['min_year_built']}+")
        st.write(f"🚗 Commute: {preferences['max_commute']} min max")
        st.write(f"🚗 Garage: {'Required' if preferences['needs_garage'] else 'Optional'}")
        
        st.write("**Note:** Houses outside your preferred ranges get LOWER scores, not filtered out. This way you can see all options ranked by fit to your preferences!")
    
    # Show top recommendations with better visibility
    st.markdown("### 🏆 All Houses Ranked by Your Preferences")
    
    # Add a toggle for showing all vs top 10
    show_all_houses = st.checkbox("📋 Show all houses (not just top 10)", value=False)
    display_count = len(filtered_df) if show_all_houses else min(10, len(filtered_df))
    
    for idx, (_, house) in enumerate(filtered_df.head(display_count).iterrows()):
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
                st.write(f"💰 Price: {house['price_score']:.2f}")
                st.write(f"🚗 Commute: {house['commute_score']:.2f}")
                st.write(f"📐 Size: {house['size_score']:.2f}")
                st.write(f"📅 Age: {house['age_score']:.2f}")
                st.write(f"🏠 Bedrooms: {house['bedrooms_score']:.2f}")
                st.write(f"🚗 Garage: {house['garage_score']:.2f}")
                st.write(f"🏘️ Area: {house['neighborhood_score']:.2f}")
            
            with col_c:
                # Better score visualization - horizontal bars instead of tiny gauge
                st.write("**🎯 Score Breakdown**")
                
                # Overall score with color coding
                score_color = "#28a745" if score >= 0.85 else "#ffc107" if score >= 0.65 else "#dc3545"
                st.markdown(f"""
                <div style="background: {score_color}; padding: 10px; border-radius: 5px; text-align: center; margin-bottom: 10px;">
                    <h3 style="color: white; margin: 0;">Overall: {score:.1%}</h3>
                </div>
                """, unsafe_allow_html=True)
                
                # Individual score bars
                score_components = [
                    ("💰 Price", house['price_score'], "#e74c3c"),
                    ("🚗 Commute", house['commute_score'], "#3498db"),
                    ("📐 Size", house['size_score'], "#2ecc71"),
                    ("📅 Age", house['age_score'], "#f39c12"),
                    ("🏠 Bedrooms", house['bedrooms_score'], "#9b59b6"),
                    ("🅿️ Garage", house['garage_score'], "#1abc9c"),
                    ("🏘️ Area", house['neighborhood_score'], "#34495e")
                ]
                
                for label, value, color in score_components:
                    # Create a horizontal bar chart effect
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
            filtered_df, 
            x='overall_score',
            title="🎯 Score Distribution",
            nbins=10,
            color_discrete_sequence=['#667eea'],
            labels={'overall_score': 'Overall Score', 'count': 'Number of Houses'}
        )
        fig_scores.update_layout(
            height=500,  # Bigger chart
            title_font_size=16,
            showlegend=False,
            xaxis_title_font_size=14,
            yaxis_title_font_size=14
        )
        st.plotly_chart(fig_scores, use_container_width=True)
    
    with col_chart2:
        # Price vs Score with better sizing
        fig_price_score = px.scatter(
            filtered_df,
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
            height=500,  # Bigger chart
            title_font_size=16,
            xaxis_title_font_size=14,
            yaxis_title_font_size=14
        )
        st.plotly_chart(fig_price_score, use_container_width=True)
    
    # Add a summary table for quick scanning
    st.markdown("### 📋 Quick Comparison Table")
    
    # Create a clean summary table
    summary_cols = ['address', 'price', 'overall_score', 'bedrooms', 'sqft', 'neighborhood', 'recommendation']
    summary_df = filtered_df[summary_cols].head(15).copy()
    
    # Format for better display
    summary_df['price'] = summary_df['price'].apply(lambda x: f"${x:,.0f}")
    summary_df['overall_score'] = summary_df['overall_score'].apply(lambda x: f"{x:.1%}")
    summary_df['sqft'] = summary_df['sqft'].apply(lambda x: f"{x:,.0f}")
    
    # Rename columns for display
    summary_df.columns = ['Address', 'Price', 'Score', 'Beds', 'Sq Ft', 'Area', 'Recommendation']
    
    st.dataframe(
        summary_df,
        use_container_width=True,
        height=500  # Bigger table
    )

def main():
    """Main dashboard function"""
    
    st.markdown('<div class="main-header"><h1>🏠 AI House Hunter - Dynamic Preferences</h1><p>Adjust your preferences and see results update in real-time!</p></div>', unsafe_allow_html=True)
    
    # Create preferences panel and get user inputs
    preferences, weights, df = create_preferences_panel()
    
    # Add refresh button
    if st.sidebar.button("🔄 Recalculate All Scores", type="primary"):
        st.cache_data.clear()
        st.rerun()
    
    # Apply dynamic scoring
    scored_df = apply_dynamic_scoring(df, preferences, weights)
    
    # Display results
    display_results(scored_df, preferences)
    
    # Show preferences summary
    with st.expander("📋 Current Preferences Summary"):
        st.json(preferences)

if __name__ == "__main__":
    main()