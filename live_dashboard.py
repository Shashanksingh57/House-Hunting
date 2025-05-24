# simple_working_dashboard.py
# Simplified dashboard that definitely works

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime
import json
import os
import glob

# Page config
st.set_page_config(
    page_title="AI House Hunter Dashboard", 
    page_icon="🏠", 
    layout="wide"
)

@st.cache_data(ttl=300)
def load_house_data():
    """Load house data - prioritize real Zillow data"""
    
    # Check for real data files first
    data_files = [
        'real_scored_houses.csv',
        'real_zillow_data.csv',
        'ai_house_analysis.csv'
    ]
    
    for filename in data_files:
        if os.path.exists(filename):
            try:
                df = pd.read_csv(filename)
                
                # Basic validation
                required_cols = ['address', 'price', 'bedrooms', 'sqft']
                if all(col in df.columns for col in required_cols):
                    st.sidebar.success(f"✅ Loaded: {filename}")
                    st.sidebar.info(f"🏠 {len(df)} houses")
                    return df, filename
            except Exception as e:
                st.sidebar.warning(f"Error loading {filename}: {e}")
    
    # If no files found, create sample data
    st.sidebar.warning("❌ No data files found - using sample data")
    st.sidebar.info("💡 Run `python test_real_data.py` to get real data")
    
    sample_data = {
        'address': ['123 Oak St, Plymouth, MN', '456 Pine Ave, Woodbury, MN', '789 Elm Dr, Maple Grove, MN'],
        'price': [350000, 325000, 375000],
        'bedrooms': [3, 4, 3],
        'bathrooms': [2.5, 2.5, 2],
        'sqft': [1450, 1600, 1400],
        'year_built': [2015, 2012, 2018],
        'neighborhood': ['Plymouth', 'Woodbury', 'Maple Grove'],
        'overall_score': [0.85, 0.78, 0.82],
        'data_source': ['sample', 'sample', 'sample'],
        'listing_url': ['https://zillow.com/sample1', 'https://zillow.com/sample2', 'https://zillow.com/sample3']
    }
    
    return pd.DataFrame(sample_data), 'sample_data'

def main():
    st.title("🏠 AI-Powered House Hunter Dashboard")
    st.markdown("*Real-time market analysis with personalized AI scoring*")
    
    # Load data
    df, data_source = load_house_data()
    
    # Sidebar controls
    with st.sidebar:
        st.header("🎯 Your Preferences")
        
        # Show data info
        if 'real_' in data_source:
            st.success("🔥 Using REAL Zillow data!")
        else:
            st.info("🎭 Using sample data")
        
        # Get data ranges for smart defaults
        price_min = int(df['price'].min())
        price_max = int(df['price'].max())
        bed_min = int(df['bedrooms'].min())
        bed_max = int(df['bedrooms'].max())
        sqft_min = int(df['sqft'].min())
        sqft_max = int(df['sqft'].max())
        
        # Controls with smart defaults
        st.subheader("💰 Budget")
        st.write(f"Data range: ${price_min:,} - ${price_max:,}")
        max_budget = st.slider("Max Budget", price_min, price_max + 50000, price_max, 10000, format="$%d")
        
        st.subheader("🏡 House Features")
        st.write(f"Bedrooms available: {bed_min} - {bed_max}")
        min_bedrooms = st.selectbox("Min Bedrooms", list(range(bed_min, bed_max + 1)), index=0)
        
        st.write(f"Size range: {sqft_min:,} - {sqft_max:,} sqft")
        min_sqft = st.slider("Min Square Feet", sqft_min, sqft_max, sqft_min, 100)
        
        # Quick options
        st.subheader("⚡ Quick Options")
        show_all = st.checkbox("🔍 Show All Data (Ignore Filters)")
        
        if st.button("🔄 Refresh Data"):
            st.cache_data.clear()
            st.rerun()
    
    # Apply filters (this happens AFTER all variables are defined)
    if show_all:
        display_df = df.copy()
        st.info("🔍 Showing all data (filters ignored)")
    else:
        # Apply filters step by step
        display_df = df.copy()
        
        # Price filter
        display_df = display_df[display_df['price'] <= max_budget]
        
        # Bedroom filter
        display_df = display_df[display_df['bedrooms'] >= min_bedrooms]
        
        # Size filter
        display_df = display_df[display_df['sqft'] >= min_sqft]
        
        # Show filter results
        if len(display_df) != len(df):
            st.info(f"🔍 Showing {len(display_df)}/{len(df)} houses after filtering")
    
    # Display results
    if len(display_df) == 0:
        st.warning("❌ No houses match your criteria!")
        st.info("💡 Try checking the 'Show All Data' option or adjusting filters")
        return
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🏠 Houses", len(display_df))
    with col2:
        avg_price = display_df['price'].mean()
        st.metric("💰 Avg Price", f"${avg_price:,.0f}")
    with col3:
        avg_sqft = display_df['sqft'].mean()
        st.metric("📐 Avg Size", f"{avg_sqft:.0f} sqft")
    with col4:
        if 'overall_score' in display_df.columns:
            avg_score = display_df['overall_score'].mean()
            st.metric("🎯 Avg Score", f"{avg_score:.1%}")
        else:
            st.metric("🎯 Avg Score", "N/A")
    
    # Show data source
    if 'data_source' in display_df.columns:
        sources = display_df['data_source'].value_counts()
        if 'zillow_rapidapi' in sources.index:
            st.success("🔥 Viewing REAL Zillow data! All links will work.")
        else:
            st.warning("🎭 Sample data - Links are approximations")
    
    # Main tabs
    tab1, tab2 = st.tabs(["🏆 House Listings", "📊 Market Analysis"])
    
    with tab1:
        st.header("🏆 Available Houses")
        
        # Sort by score if available
        if 'overall_score' in display_df.columns:
            display_df = display_df.sort_values('overall_score', ascending=False)
        
        # Show houses
        for idx, (_, house) in enumerate(display_df.iterrows()):
            with st.expander(f"#{idx+1} - {house['address']} - ${house['price']:,}", expanded=(idx < 3)):
                col_a, col_b = st.columns([2, 1])
                
                with col_a:
                    st.write("**🏠 Property Details**")
                    st.write(f"📍 **Address**: {house['address']}")
                    st.write(f"💰 **Price**: ${house['price']:,}")
                    st.write(f"🏠 **Layout**: {house['bedrooms']} bed, {house.get('bathrooms', 'N/A')} bath")
                    st.write(f"📐 **Size**: {house['sqft']} sqft")
                    if 'year_built' in house:
                        st.write(f"📅 **Built**: {house['year_built']}")
                    if 'neighborhood' in house:
                        st.write(f"🏘️ **Area**: {house['neighborhood']}")
                    
                    # Zillow link
                    if 'listing_url' in house and house['listing_url']:
                        url = house['listing_url']
                        if 'zillow.com' in str(url):
                            st.markdown(f"🔗 **[View on Zillow]({url})**")
                        else:
                            # Create search link
                            search_query = house['address'].replace(' ', '+').replace(',', '')
                            search_url = f"https://www.zillow.com/homes/{search_query}_rb/"
                            st.markdown(f"🔍 **[Search on Zillow]({search_url})**")
                
                with col_b:
                    if 'overall_score' in house:
                        st.write("**🎯 AI Analysis**")
                        score = house['overall_score']
                        st.write(f"Overall Score: **{score:.1%}**")
                        
                        # Simple score gauge
                        if score >= 0.8:
                            st.success("🔥 HIGHLY RECOMMENDED")
                        elif score >= 0.7:
                            st.info("✅ GOOD OPTION")
                        elif score >= 0.6:
                            st.warning("⚠️ DECENT")
                        else:
                            st.error("❌ BELOW THRESHOLD")
                    
                    # Action buttons
                    if st.button(f"❤️ Save", key=f"save_{idx}"):
                        st.success("Saved!")
                    
                    if st.button(f"📞 Tour", key=f"tour_{idx}"):
                        st.info("Coming soon!")
    
    with tab2:
        st.header("📊 Market Analysis")
        
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            # Price distribution
            fig_price = px.histogram(display_df, x='price', title="💰 Price Distribution", nbins=8)
            st.plotly_chart(fig_price, use_container_width=True)
        
        with col_chart2:
            # Size vs Price
            fig_scatter = px.scatter(display_df, x='sqft', y='price', title="📐 Size vs Price")
            st.plotly_chart(fig_scatter, use_container_width=True)
        
        # Summary stats
        st.subheader("📈 Market Summary")
        
        if len(display_df) > 0:
            st.write(f"**Price Range**: ${display_df['price'].min():,} - ${display_df['price'].max():,}")
            st.write(f"**Average Price**: ${display_df['price'].mean():,.0f}")
            st.write(f"**Price per Sqft**: ${(display_df['price'] / display_df['sqft']).mean():.0f}")
            
            if 'neighborhood' in display_df.columns:
                neighborhood_counts = display_df['neighborhood'].value_counts()
                st.write(f"**Top Areas**: {', '.join(neighborhood_counts.head(3).index.tolist())}")

if __name__ == "__main__":
    main()