# live_dashboard.py
# Interactive Streamlit dashboard for house hunting - FIXED VERSION

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime
import json
import os
import glob

# Import your existing functions
try:
    from all_in_one_house_hunter import HouseDataCollector, AdvancedHouseScorer
    from test_real_data import ensure_scoring_compatibility
except ImportError:
    st.error("Please make sure all_in_one_house_hunter.py and test_real_data.py are in the same directory!")
    st.stop()

# Page config
st.set_page_config(
    page_title="AI House Hunter Dashboard", 
    page_icon="🏠", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ff6b6b;
    }
    .top-house {
        background-color: #e8f5e8;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# HELPER FUNCTIONS - DEFINED FIRST
def check_for_real_data():
    """Check what real data files are available"""
    
    st.sidebar.markdown("### 📁 Available Data Files")
    
    real_data_files = [
        'real_scored_houses.csv',
        'real_zillow_data.csv', 
        'market_data_*.csv',
        'ai_house_analysis.csv'
    ]
    
    found_files = []
    
    for pattern in real_data_files:
        if '*' in pattern:
            files = glob.glob(pattern)
            if files:
                found_files.extend(files)
        else:
            if os.path.exists(pattern):
                found_files.append(pattern)
    
    if found_files:
        for file in found_files:
            file_size = os.path.getsize(file) / 1024  # KB
            mod_time = datetime.fromtimestamp(os.path.getmtime(file))
            
            if 'real_' in file:
                st.sidebar.success(f"✅ {file} ({file_size:.1f}KB)")
            else:
                st.sidebar.info(f"📄 {file} ({file_size:.1f}KB)")
            
            st.sidebar.caption(f"   Modified: {mod_time.strftime('%m/%d %H:%M')}")
    else:
        st.sidebar.warning("⚠️ No data files found")
        st.sidebar.markdown("""
        **To get real data:**
        1. Run `python test_real_data.py`
        2. Refresh this dashboard
        """)

def refresh_data_button():
    """Add a refresh button to clear cache"""
    
    if st.sidebar.button("🔄 Refresh Data", help="Clear cache and reload data"):
        st.cache_data.clear()
        st.rerun()

def generate_fallback_data():
    """Generate fallback data if no real data available"""
    
    try:
        collector = HouseDataCollector()
        houses = collector.get_minneapolis_houses()
        
        scorer = AdvancedHouseScorer()
        scored_houses = []
        
        for house in houses:
            scores = scorer.score_house(house)
            house_with_scores = {**house, **scores}
            scored_houses.append(house_with_scores)
        
        df = pd.DataFrame(scored_houses)
        df = df.sort_values('overall_score', ascending=False)
        return df
        
    except Exception as e:
        st.error(f"❌ Could not generate fallback data: {e}")
        # Return empty DataFrame with required columns
        return pd.DataFrame(columns=['address', 'price', 'bedrooms', 'sqft', 'overall_score'])

def score_houses_if_needed(df):
    """Score houses if they don't have scores"""
    
    try:
        scorer = AdvancedHouseScorer()
        scored_houses = []
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for idx, (_, house) in enumerate(df.iterrows()):
            try:
                # Update progress
                progress = (idx + 1) / len(df)
                progress_bar.progress(progress)
                status_text.text(f"Scoring house {idx + 1}/{len(df)}: {house.get('address', 'Unknown')[:30]}...")
                
                # Ensure compatibility and score
                house_dict = house.to_dict()
                house_dict = ensure_scoring_compatibility(house_dict)
                scores = scorer.score_house(house_dict)
                house_with_scores = {**house_dict, **scores}
                scored_houses.append(house_with_scores)
                
            except Exception as e:
                st.warning(f"⚠️ Could not score {house.get('address', 'unknown')}: {e}")
                continue
        
        progress_bar.empty()
        status_text.empty()
        
        if scored_houses:
            scored_df = pd.DataFrame(scored_houses)
            scored_df = scored_df.sort_values('overall_score', ascending=False)
            
            # Save the scored data for future use
            scored_df.to_csv('dashboard_scored_houses.csv', index=False)
            st.success(f"✅ Scored {len(scored_df)} houses and saved results!")
            
            return scored_df
        else:
            st.error("❌ Could not score any houses")
            return df
        
    except ImportError as e:
        st.error(f"❌ Could not import scoring system: {e}")
        return df
    except Exception as e:
        st.error(f"❌ Scoring error: {e}")
        return df

@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_house_data():
    """Load house data - prioritize real Zillow data"""
    
    # Priority order: real data first!
    data_sources = [
        ('real_scored_houses.csv', 'Real Zillow Data (Scored)', '🔥'),
        ('real_zillow_data.csv', 'Real Zillow Data (Raw)', '📡'),
        ('market_data_*.csv', 'Recent Market Data', '📊'),
        ('ai_house_analysis.csv', 'Generated Sample Data', '🎭'),
    ]
    
    for filename_pattern, description, icon in data_sources:
        try:
            # Handle wildcard patterns
            if '*' in filename_pattern:
                files = glob.glob(filename_pattern)
                if files:
                    # Get the most recent file
                    filename = max(files, key=os.path.getctime)
                else:
                    continue
            else:
                filename = filename_pattern
                
            if os.path.exists(filename):
                df = pd.read_csv(filename)
                
                # If it's raw data without scores, score it
                if 'overall_score' not in df.columns:
                    st.info("🎯 Scoring real data...")
                    df = score_houses_if_needed(df)
                
                # Validate we have the required columns
                required_cols = ['address', 'price', 'bedrooms', 'sqft']
                if all(col in df.columns for col in required_cols):
                    st.sidebar.success(f"{icon} **Using:** {description}")
                    st.sidebar.info(f"🏠 **{len(df)} houses** loaded from `{filename}`")
                    st.sidebar.write(f"📅 Last modified: {datetime.fromtimestamp(os.path.getmtime(filename)).strftime('%Y-%m-%d %H:%M')}")
                    return df
                else:
                    st.sidebar.warning(f"⚠️ {filename} missing required columns")
                    continue
                
        except Exception as e:
            st.sidebar.warning(f"⚠️ Error loading {filename_pattern}: {e}")
            continue
    
    # If no real data found, show message and generate fallback
    st.sidebar.error("❌ **No real data found!**")
    st.sidebar.info("💡 Run `python test_real_data.py` to get real Zillow data")
    
    return generate_fallback_data()

def create_score_gauge(score, title):
    """Create a gauge chart for scores"""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = score * 100,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': title},
        delta = {'reference': 70},
        gauge = {
            'axis': {'range': [None, 100]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 50], 'color': "lightgray"},
                {'range': [50, 80], 'color': "yellow"},
                {'range': [80, 100], 'color': "green"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    fig.update_layout(height=300)
    return fig

# MAIN FUNCTION
def main():
    # Header
    st.title("🏠 AI-Powered House Hunter Dashboard")
    st.markdown("*Real-time market analysis with personalized AI scoring*")
    
    # Sidebar for controls
    with st.sidebar:
        st.header("🎯 Your Preferences")
        
        # Data management section
        check_for_real_data()
        refresh_data_button()
        
        st.markdown("---")
        
        # Load current data to get ranges
        df = load_house_data()
        
        if len(df) == 0:
            st.error("❌ No data available!")
            st.info("Run `python test_real_data.py` to get real Zillow data")
            st.stop()
        
        # Budget controls
        st.subheader("💰 Budget")
        
        # Show actual price range in your data
        price_min = int(df['price'].min()) if len(df) > 0 else 250000
        price_max = int(df['price'].max()) if len(df) > 0 else 500000
        
        st.write(f"💡 Your data range: ${price_min:,} - ${price_max:,}")
        
        max_budget = st.slider(
            "Maximum Budget", 
            min_value=price_min, 
            max_value=price_max + 50000,  # Add buffer
            value=min(400000, price_max),  # Use actual max if lower than 400k
            step=10000,
            format="$%d"
        )
        
        # Location controls
        st.subheader("📍 Location")
        max_commute = st.slider("Max Commute (minutes)", 15, 45, 30)
        
        neighborhoods = df['neighborhood'].unique() if 'neighborhood' in df.columns else ['Minneapolis']
        st.write(f"💡 Available neighborhoods: {len(neighborhoods)}")
        
        selected_neighborhoods = st.multiselect(
            "Preferred Neighborhoods", 
            neighborhoods, 
            default=list(neighborhoods)  # Select ALL by default
        )
        
        # House features
        st.subheader("🏡 House Features")
        
        # Show actual bedroom range
        bed_min = int(df['bedrooms'].min()) if len(df) > 0 else 2
        bed_max = int(df['bedrooms'].max()) if len(df) > 0 else 5
        st.write(f"💡 Bedrooms in data: {bed_min} - {bed_max}")
        
        min_bedrooms = st.selectbox("Min Bedrooms", 
                                   list(range(bed_min, bed_max + 1)), 
                                   index=0)  # Start with minimum available
        
        # Show actual sqft range
        sqft_min = int(df['sqft'].min()) if len(df) > 0 else 1000
        sqft_max = int(df['sqft'].max()) if len(df) > 0 else 3000
        st.write(f"💡 Size range: {sqft_min:,} - {sqft_max:,} sqft")
        
        min_sqft = st.number_input("Min Square Feet", 
                                  min_value=sqft_min, 
                                  max_value=sqft_max, 
                                  value=sqft_min,  # Start with minimum
                                  step=100)
        
        # Show actual year range
        year_min = int(df['year_built'].min()) if len(df) > 0 and 'year_built' in df.columns else 1990
        year_max = int(df['year_built'].max()) if len(df) > 0 and 'year_built' in df.columns else 2025
        st.write(f"💡 Year built range: {year_min} - {year_max}")
        
        min_year = st.number_input("Min Year Built", 
                                  min_value=year_min, 
                                  max_value=year_max, 
                                  value=year_min,  # Start with minimum
                                  step=5)
        
        # Garage filter - check if data exists
        has_garage_data = 'has_garage' in df.columns
        if has_garage_data:
            garage_count = df['has_garage'].sum() if pd.api.types.is_bool_dtype(df['has_garage']) else 0
            st.write(f"💡 Houses with garage: {garage_count}/{len(df)}")
            needs_garage = st.checkbox("Must have garage", value=False)  # Default to False
        else:
            needs_garage = False
            st.info("ℹ️ Garage data not available")
        
        # Scoring weights
        st.subheader("⚖️ Scoring Weights")
        st.markdown("*Adjust what's most important to you*")
        
        price_weight = st.slider("Price Importance", 0.0, 0.5, 0.25, 0.05)
        commute_weight = st.slider("Commute Importance", 0.0, 0.5, 0.20, 0.05)
        location_weight = st.slider("Neighborhood Importance", 0.0, 0.3, 0.15, 0.05)
        
        # Quick options
        st.subheader("⚡ Quick Options")
        
        if st.button("🌟 Show All Houses", help="Reset filters to show all available data"):
            st.cache_data.clear()
            st.rerun()
        
        show_all = st.checkbox("🔍 Ignore Filters (Show All)", help="Temporarily show all data regardless of filters")
        
        # Update button
        update_analysis = st.button("🔄 Update Analysis", type="primary")
    
    # Main content area
    col1, col2, col3, col4 = st.columns(4)
    
    # Filter data based on preferences with debug info
    # Use filtered or all data based on checkbox
    display_df = df if show_all else filtered_df
    st.sidebar.subheader("🔍 Filter Debug")
    
    # Start with all data
    filtered_df = df.copy()
    st.sidebar.write(f"📊 Starting with: {len(filtered_df)} houses")
    
    # Apply filters one by one and show impact
    price_filter = filtered_df['price'] <= max_budget
    filtered_df = filtered_df[price_filter]
    st.sidebar.write(f"💰 After price filter (≤${max_budget:,}): {len(filtered_df)} houses")
    
    bedroom_filter = filtered_df['bedrooms'] >= min_bedrooms
    filtered_df = filtered_df[bedroom_filter]
    st.sidebar.write(f"🏠 After bedroom filter (≥{min_bedrooms}): {len(filtered_df)} houses")
    
    sqft_filter = filtered_df['sqft'] >= min_sqft
    filtered_df = filtered_df[sqft_filter]
    st.sidebar.write(f"📐 After size filter (≥{min_sqft:,} sqft): {len(filtered_df)} houses")
    
    if 'year_built' in filtered_df.columns:
        year_filter = filtered_df['year_built'] >= min_year
        filtered_df = filtered_df[year_filter]
        st.sidebar.write(f"📅 After year filter (≥{min_year}): {len(filtered_df)} houses")
    
    if 'neighborhood' in filtered_df.columns and selected_neighborhoods:
        neighborhood_filter = filtered_df['neighborhood'].isin(selected_neighborhoods)
        filtered_df = filtered_df[neighborhood_filter]
        st.sidebar.write(f"🏘️ After neighborhood filter: {len(filtered_df)} houses")
    
    if needs_garage and 'has_garage' in filtered_df.columns:
        garage_filter = filtered_df['has_garage'] == True
        filtered_df = filtered_df[garage_filter]
        st.sidebar.write(f"🚗 After garage filter: {len(filtered_df)} houses")
    
    # Show final result
    if len(filtered_df) == 0:
        st.sidebar.error("❌ No houses match all filters!")
        st.sidebar.button("🔄 Reset Filters", help="Reset all filters to show all data")
    else:
        st.sidebar.success(f"✅ Final result: {len(filtered_df)} houses")
    
    st.sidebar.markdown("---")
    
    # Key metrics
    with col1:
        st.metric("🏠 Total Houses", len(display_df))
    
    with col2:
        viable_count = len(display_df[display_df['meets_requirements'] == True]) if 'meets_requirements' in display_df.columns else len(display_df)
        st.metric("✅ Meet Criteria", viable_count)
    
    with col3:
        if len(display_df) > 0:
            avg_price = display_df['price'].mean()
            st.metric("💰 Avg Price", f"${avg_price:,.0f}")
        else:
            st.metric("💰 Avg Price", "N/A")
    
    with col4:
        if len(display_df) > 0:
            avg_score = display_df['overall_score'].mean() if 'overall_score' in display_df.columns else 0
            st.metric("🎯 Avg Score", f"{avg_score:.1%}")
        else:
            st.metric("🎯 Avg Score", "N/A")
    
    # Data source info
    if len(display_df) > 0:
        data_sources = display_df['data_source'].value_counts() if 'data_source' in display_df.columns else pd.Series(['Unknown'])
        
        st.info(f"📊 **Data Source**: " + " | ".join([f"{source}: {count} houses" for source, count in data_sources.items()]))
        
        # Show real data indicator
        if 'zillow_rapidapi' in data_sources.index:
            st.success("🔥 **You're viewing REAL Zillow data!** All Zillow links will work.")
        else:
            st.warning("🎭 **Sample data** - Zillow links are search-based approximations.")
    
    # Show filter status
    if show_all:
        st.info("🔍 **Showing all data** (filters ignored)")
    elif len(filtered_df) != len(df):
        st.info(f"🔍 **Filtered view**: {len(display_df)}/{len(df)} houses shown")

    if len(display_df) == 0:
        st.warning("❌ No houses match your criteria. Try:")
        st.markdown("- Check the **🔍 Filter Debug** section in sidebar")
        st.markdown("- Use **🔍 Ignore Filters** checkbox to see all data")
        st.markdown("- Click **🌟 Show All Houses** to reset filters")
        return
    
    # Main dashboard tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🏆 Top Houses", "📊 Market Analysis", "🗺️ Map View", "📈 Trends"])
    
    with tab1:
        st.header("🏆 Top Recommended Houses")
        
        # Show top houses
        top_houses = display_df.nlargest(10, 'overall_score') if 'overall_score' in display_df.columns else display_df.head(10)
        
        for idx, (_, house) in enumerate(top_houses.iterrows()):
            with st.expander(
                f"#{idx+1} - {house['address']} - Score: {house.get('overall_score', 0):.1%} - ${house['price']:,}",
                expanded=(idx < 3)
            ):
                col_a, col_b, col_c = st.columns([2, 1, 1])
                
                with col_a:
                    st.write("**🏠 Property Details**")
                    st.write(f"📍 **Address**: {house['address']}")
                    st.write(f"💰 **Price**: ${house['price']:,}")
                    st.write(f"📐 **Size**: {house['sqft']} sqft")
                    st.write(f"🏠 **Bedrooms**: {house['bedrooms']} bed, {house.get('bathrooms', 'N/A')} bath")
                    st.write(f"📅 **Built**: {house.get('year_built', 'N/A')}")
                    st.write(f"🏘️ **Neighborhood**: {house.get('neighborhood', 'Unknown')}")
                    
                    # Add Zillow link
                    zillow_url = house.get('listing_url', '')
                    if zillow_url and zillow_url != 'nan' and 'zillow.com' in str(zillow_url):
                        st.markdown(f"🔗 **[View on Zillow]({zillow_url})**")
                    else:
                        # Create search URL
                        address_clean = house.get('address', '').replace(' ', '-').replace(',', '')
                        search_url = f"https://www.zillow.com/homes/{address_clean}_rb/"
                        st.markdown(f"🔍 **[Search on Zillow]({search_url})**")
                    
                    if 'description' in house and house['description']:
                        st.write(f"📝 **Description**: {house['description']}")
                    
                    # Add data source info
                    if 'data_source' in house:
                        if house['data_source'] == 'zillow_rapidapi':
                            st.success("🔥 Real Zillow Data")
                        else:
                            st.info(f"📊 Source: {house['data_source']}")
                    
                    # Add last updated info
                    if 'last_updated' in house:
                        try:
                            last_updated = datetime.fromisoformat(house['last_updated'].replace('Z', '+00:00'))
                            st.caption(f"🕒 Updated: {last_updated.strftime('%m/%d/%Y %H:%M')}")
                        except:
                            pass
                
                with col_b:
                    st.write("**📊 AI Analysis**")
                    st.write(f"🎯 Overall Score: **{house.get('overall_score', 0):.1%}**")
                    if 'price_score' in house:
                        st.write(f"💰 Price Score: {house['price_score']:.2f}")
                    if 'location_score' in house:
                        st.write(f"📍 Location Score: {house['location_score']:.2f}")
                    if 'commute_score' in house:
                        st.write(f"🚗 Commute Score: {house['commute_score']:.2f}")
                    if 'size_score' in house:
                        st.write(f"📏 Size Score: {house['size_score']:.2f}")
                    if 'market_score' in house:
                        st.write(f"⏰ Market Score: {house['market_score']:.2f}")
                
                with col_c:
                    # Score gauge
                    if 'overall_score' in house:
                        gauge_fig = create_score_gauge(house['overall_score'], "Overall Score")
                        st.plotly_chart(gauge_fig, use_container_width=True, key=f"gauge_{idx}")
                
                # Recommendation
                if 'recommendation' in house:
                    rec_color = "🔥" if house.get('overall_score', 0) > 0.8 else "✅" if house.get('overall_score', 0) > 0.7 else "⚠️"
                    st.info(f"{rec_color} **{house['recommendation']}**")
                
                # Action buttons
                col_x, col_y, col_z = st.columns(3)
                with col_x:
                    if st.button(f"📞 Schedule Tour", key=f"tour_{idx}"):
                        st.info("Feature coming soon!")
                with col_y:
                    if st.button(f"❤️ Save Favorite", key=f"save_{idx}"):
                        st.success("Added to favorites!")
                with col_z:
                    # Zillow link button
                    zillow_url = house.get('listing_url', '')
                    if zillow_url and zillow_url != 'nan' and 'zillow.com' in str(zillow_url):
                        st.link_button(f"🏠 View on Zillow", zillow_url, help="Open listing on Zillow")
                    else:
                        # Create a search URL if no direct link
                        address = house.get('address', '').replace(' ', '-').replace(',', '')
                        search_url = f"https://www.zillow.com/homes/{address}_rb/"
                        st.link_button(f"🔍 Search Zillow", search_url, help="Search for this house on Zillow")

    with tab2:
        st.header("📊 Market Analysis")
        
        col_charts1, col_charts2 = st.columns(2)
        
        with col_charts1:
            # Price distribution
            fig_price = px.histogram(
                display_df, 
                x='price', 
                title="💰 Price Distribution",
                nbins=10,
                color_discrete_sequence=['#ff6b6b']
            )
            fig_price.update_layout(height=400)
            st.plotly_chart(fig_price, use_container_width=True, key="price_histogram")
            
            # Score vs Price scatter
            if 'overall_score' in display_df.columns:
                fig_scatter = px.scatter(
                    display_df,
                    x='price',
                    y='overall_score',
                    size='sqft',
                    color='overall_score',
                    hover_data=['neighborhood', 'bedrooms'] if 'neighborhood' in display_df.columns else ['bedrooms'],
                    title="🎯 Score vs Price",
                    color_continuous_scale='RdYlGn'
                )
                fig_scatter.update_layout(height=400)
                st.plotly_chart(fig_scatter, use_container_width=True, key="score_vs_price_scatter")
        
        with col_charts2:
            # Neighborhood comparison
            if 'neighborhood' in display_df.columns and 'overall_score' in display_df.columns:
                neighborhood_stats = display_df.groupby('neighborhood').agg({
                    'overall_score': 'mean',
                    'price': 'mean',
                    'sqft': 'mean'
                }).round(3)
                
                fig_neighborhood = px.bar(
                    neighborhood_stats.reset_index(),
                    x='neighborhood',
                    y='overall_score',
                    title="🏘️ Average Score by Neighborhood",
                    color='overall_score',
                    color_continuous_scale='RdYlGn'
                )
                fig_neighborhood.update_layout(height=400)
                st.plotly_chart(fig_neighborhood, use_container_width=True, key="neighborhood_scores")
            
            # Size vs Age scatter
            if 'year_built' in display_df.columns:
                fig_age_size = px.scatter(
                    display_df,
                    x='year_built',
                    y='sqft',
                    size='price',
                    color='overall_score' if 'overall_score' in display_df.columns else 'price',
                    title="📅 House Age vs Size",
                    color_continuous_scale='RdYlGn'
                )
                fig_age_size.update_layout(height=400)
                st.plotly_chart(fig_age_size, use_container_width=True, key="age_vs_size_scatter")
    
    # Add more tabs...
    with tab3:
        st.header("🗺️ House Locations")
        st.info("Map view coming soon! Need latitude/longitude data.")
    
    with tab4:
        st.header("📈 Market Trends")
        st.info("Trend analysis coming soon!")
    
    # Footer with refresh info
    st.markdown("---")
    st.markdown(f"*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Data refreshes every 5 minutes*")

if __name__ == "__main__":
    main()