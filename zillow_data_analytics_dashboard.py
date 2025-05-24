# zillow_data_analytics_dashboard.py
# Comprehensive analytics dashboard for Zillow data collection

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import json
import os
import glob
from datetime import datetime, timedelta
import folium
from streamlit_folium import st_folium

st.set_page_config(
    page_title="Zillow Data Analytics",
    page_icon="📊",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    .classification-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #28a745;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

class ZillowDataAnalyzer:
    """Analyze collected Zillow data"""
    
    def __init__(self):
        self.data_files = self.find_data_files()
        self.api_log = self.load_api_usage_log()
    
    def find_data_files(self):
        """Find all Zillow data files"""
        patterns = [
            'real_scored_houses.csv',
            'real_zillow_data.csv',
            'zillow_houses_*.csv',
            'comprehensive_houses_*.csv'
        ]
        
        found_files = []
        for pattern in patterns:
            if '*' in pattern:
                found_files.extend(glob.glob(pattern))
            else:
                if os.path.exists(pattern):
                    found_files.append(pattern)
        
        return found_files
    
    def load_api_usage_log(self):
        """Load or create API usage log"""
        log_file = 'zillow_api_usage.json'
        
        if os.path.exists(log_file):
            try:
                with open(log_file, 'r') as f:
                    return json.load(f)
            except:
                return {'calls': [], 'total_calls': 0, 'total_cost': 0}
        else:
            return {'calls': [], 'total_calls': 0, 'total_cost': 0}
    
    def load_all_house_data(self):
        """Load and combine all house data"""
        all_houses = []
        file_sources = {}
        
        for file in self.data_files:
            try:
                df = pd.read_csv(file)
                
                # Add source tracking
                df['source_file'] = file
                df['file_date'] = datetime.fromtimestamp(os.path.getmtime(file))
                
                all_houses.append(df)
                file_sources[file] = {
                    'houses': len(df),
                    'size_kb': os.path.getsize(file) / 1024,
                    'modified': datetime.fromtimestamp(os.path.getmtime(file))
                }
                
            except Exception as e:
                st.warning(f"Could not load {file}: {e}")
        
        if all_houses:
            combined_df = pd.concat(all_houses, ignore_index=True)
            
            # Remove duplicates based on address or zpid
            if 'zpid' in combined_df.columns:
                combined_df = combined_df.drop_duplicates(subset=['zpid'], keep='last')
            else:
                combined_df = combined_df.drop_duplicates(subset=['address'], keep='last')
            
            return combined_df, file_sources
        else:
            return pd.DataFrame(), {}
    
    def classify_houses(self, df):
        """Classify houses into categories"""
        
        if len(df) == 0:
            return {}
        
        classifications = {}
        
        # Price categories
        if 'price' in df.columns:
            price_ranges = {
                'Budget-Friendly': (0, 250000),
                'Mid-Range': (250000, 400000),
                'Premium': (400000, 600000),
                'Luxury': (600000, float('inf'))
            }
            
            price_classification = {}
            for category, (min_price, max_price) in price_ranges.items():
                count = len(df[(df['price'] >= min_price) & (df['price'] < max_price)])
                price_classification[category] = count
            
            classifications['Price Ranges'] = price_classification
        
        # Size categories
        if 'sqft' in df.columns:
            size_ranges = {
                'Cozy (<1200 sqft)': (0, 1200),
                'Medium (1200-1800 sqft)': (1200, 1800),
                'Spacious (1800-2500 sqft)': (1800, 2500),
                'Large (2500+ sqft)': (2500, float('inf'))
            }
            
            size_classification = {}
            for category, (min_size, max_size) in size_ranges.items():
                count = len(df[(df['sqft'] >= min_size) & (df['sqft'] < max_size)])
                size_classification[category] = count
            
            classifications['Size Categories'] = size_classification
        
        # Age categories
        if 'year_built' in df.columns:
            current_year = datetime.now().year
            age_ranges = {
                'New (2015+)': (2015, current_year + 1),
                'Modern (2000-2014)': (2000, 2015),
                'Established (1980-1999)': (1980, 2000),
                'Vintage (<1980)': (0, 1980)
            }
            
            age_classification = {}
            for category, (min_year, max_year) in age_ranges.items():
                count = len(df[(df['year_built'] >= min_year) & (df['year_built'] < max_year)])
                age_classification[category] = count
            
            classifications['Age Categories'] = age_classification
        
        # Neighborhood distribution
        if 'neighborhood' in df.columns:
            neighborhood_counts = df['neighborhood'].value_counts().to_dict()
            classifications['Neighborhoods'] = neighborhood_counts
        
        # Property type
        if 'property_type' in df.columns:
            property_counts = df['property_type'].value_counts().to_dict()
            classifications['Property Types'] = property_counts
        
        return classifications
    
    def estimate_api_costs(self, df):
        """Estimate API costs based on data collected"""
        
        # RapidAPI Zillow pricing (approximate)
        cost_per_request = 0.01  # $0.01 per request (example)
        
        # Estimate requests based on unique locations and searches
        if 'neighborhood' in df.columns:
            unique_locations = df['neighborhood'].nunique()
        else:
            unique_locations = 1
        
        # Estimate requests: locations × search variations
        estimated_requests = unique_locations * 3  # Assume 3 searches per location
        estimated_cost = estimated_requests * cost_per_request
        
        return {
            'estimated_requests': estimated_requests,
            'estimated_cost': estimated_cost,
            'cost_per_house': estimated_cost / len(df) if len(df) > 0 else 0
        }

def display_api_metrics(analyzer):
    """Display API usage metrics"""
    
    st.header("📡 API Usage Analytics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Load data to estimate metrics
    df, file_sources = analyzer.load_all_house_data()
    api_estimates = analyzer.estimate_api_costs(df)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>Total API Calls</h3>
            <h2>{}</h2>
        </div>
        """.format(api_estimates['estimated_requests']), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3>Estimated Cost</h3>
            <h2>${:.2f}</h2>
        </div>
        """.format(api_estimates['estimated_cost']), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3>Cost per House</h3>
            <h2>${:.3f}</h2>
        </div>
        """.format(api_estimates['cost_per_house']), unsafe_allow_html=True)
    
    with col4:
        data_files_count = len(analyzer.data_files)
        st.markdown("""
        <div class="metric-card">
            <h3>Data Files</h3>
            <h2>{}</h2>
        </div>
        """.format(data_files_count), unsafe_allow_html=True)
    
    # Data collection timeline
    if file_sources:
        st.subheader("📅 Data Collection Timeline")
        
        timeline_data = []
        for file, info in file_sources.items():
            timeline_data.append({
                'File': file.split('/')[-1],  # Just filename
                'Date': info['modified'],
                'Houses': info['houses'],
                'Size (KB)': info['size_kb']
            })
        
        timeline_df = pd.DataFrame(timeline_data)
        timeline_df = timeline_df.sort_values('Date')
        
        # Create timeline chart
        fig = px.scatter(timeline_df, 
                        x='Date', 
                        y='Houses',
                        size='Size (KB)',
                        hover_data=['File'],
                        title="Data Collection Over Time")
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

def display_house_classifications(analyzer):
    """Display house classification analytics"""
    
    st.header("🏠 House Classifications")
    
    df, _ = analyzer.load_all_house_data()
    
    if len(df) == 0:
        st.warning("No house data found to analyze")
        return
    
    classifications = analyzer.classify_houses(df)
    
    # Create tabs for different classifications
    if classifications:
        tabs = st.tabs(list(classifications.keys()))
        
        for i, (category, data) in enumerate(classifications.items()):
            with tabs[i]:
                if isinstance(data, dict) and data:
                    # Create pie chart
                    labels = list(data.keys())
                    values = list(data.values())
                    
                    fig = px.pie(values=values, 
                                names=labels, 
                                title=f"{category} Distribution")
                    fig.update_traces(textposition='inside', textinfo='percent+label')
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Display as cards
                    cols = st.columns(min(3, len(data)))
                    for j, (item, count) in enumerate(data.items()):
                        col_idx = j % len(cols)
                        with cols[col_idx]:
                            percentage = (count / sum(values)) * 100
                            st.markdown(f"""
                            <div class="classification-card">
                                <h4>{item}</h4>
                                <h3>{count} houses</h3>
                                <p>{percentage:.1f}% of total</p>
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    st.info(f"No data available for {category}")

def display_geographic_map(analyzer):
    """Display houses on an interactive map"""
    
    st.header("🗺️ Geographic Distribution")
    
    df, _ = analyzer.load_all_house_data()
    
    if len(df) == 0 or 'latitude' not in df.columns or 'longitude' not in df.columns:
        st.warning("No geographic data available for mapping")
        return
    
    # Filter out houses without coordinates
    map_df = df.dropna(subset=['latitude', 'longitude'])
    
    if len(map_df) == 0:
        st.warning("No houses have coordinate data for mapping")
        return
    
    st.info(f"Showing {len(map_df)} houses on map")
    
    # Create map centered on Minneapolis
    center_lat = map_df['latitude'].mean()
    center_lon = map_df['longitude'].mean()
    
    m = folium.Map(location=[center_lat, center_lon], zoom_start=11)
    
    # Color code by price if available
    if 'price' in map_df.columns:
        price_min = map_df['price'].min()
        price_max = map_df['price'].max()
        
        def get_color(price):
            # Color scale from green (cheap) to red (expensive)
            normalized = (price - price_min) / (price_max - price_min)
            if normalized < 0.33:
                return 'green'
            elif normalized < 0.67:
                return 'orange'
            else:
                return 'red'
    
    # Add markers
    for idx, house in map_df.iterrows():
        # Create popup content
        popup_content = f"""
        <b>{house.get('address', 'Unknown Address')}</b><br>
        💰 Price: ${house.get('price', 0):,}<br>
        🏠 {house.get('bedrooms', '?')} bed, {house.get('bathrooms', '?')} bath<br>
        📐 {house.get('sqft', '?')} sqft<br>
        📅 Built: {house.get('year_built', '?')}<br>
        🏘️ {house.get('neighborhood', '?')}
        """
        
        if 'price' in house and pd.notna(house['price']):
            color = get_color(house['price'])
        else:
            color = 'blue'
        
        folium.CircleMarker(
            location=[house['latitude'], house['longitude']],
            radius=8,
            popup=folium.Popup(popup_content, max_width=300),
            color='white',
            weight=2,
            fillColor=color,
            fillOpacity=0.7
        ).add_to(m)
    
    # Add legend
    if 'price' in map_df.columns:
        legend_html = f'''
        <div style="position: fixed; 
                    bottom: 50px; left: 50px; width: 200px; height: 90px; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:14px; padding: 10px">
        <p><b>Price Range</b></p>
        <p><i class="fa fa-circle" style="color:green"></i> ${price_min:,.0f} - ${price_min + (price_max-price_min)/3:,.0f}</p>
        <p><i class="fa fa-circle" style="color:orange"></i> ${price_min + (price_max-price_min)/3:,.0f} - ${price_min + 2*(price_max-price_min)/3:,.0f}</p>
        <p><i class="fa fa-circle" style="color:red"></i> ${price_min + 2*(price_max-price_min)/3:,.0f} - ${price_max:,.0f}</p>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(legend_html))
    
    # Display map
    map_data = st_folium(m, width=1000, height=600)
    
    # Show neighborhood summary
    if 'neighborhood' in map_df.columns:
        st.subheader("📍 Neighborhood Summary")
        
        neighborhood_summary = map_df.groupby('neighborhood').agg({
            'price': ['count', 'mean', 'min', 'max'],
            'sqft': 'mean'
        }).round(0)
        
        neighborhood_summary.columns = ['Count', 'Avg Price', 'Min Price', 'Max Price', 'Avg SqFt']
        neighborhood_summary = neighborhood_summary.sort_values('Count', ascending=False)
        
        st.dataframe(neighborhood_summary, use_container_width=True)

def display_market_insights(analyzer):
    """Display market insights and trends"""
    
    st.header("📈 Market Insights")
    
    df, _ = analyzer.load_all_house_data()
    
    if len(df) == 0:
        st.warning("No data available for market analysis")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Price distribution
        if 'price' in df.columns:
            st.subheader("💰 Price Distribution")
            fig = px.histogram(df, x='price', nbins=20, title="Distribution of House Prices")
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            # Price statistics
            st.write("**Price Statistics:**")
            st.write(f"• Average: ${df['price'].mean():,.0f}")
            st.write(f"• Median: ${df['price'].median():,.0f}")
            st.write(f"• Range: ${df['price'].min():,.0f} - ${df['price'].max():,.0f}")
    
    with col2:
        # Size vs Price correlation
        if 'sqft' in df.columns and 'price' in df.columns:
            st.subheader("📐 Size vs Price")
            fig = px.scatter(df, x='sqft', y='price', 
                           hover_data=['address', 'neighborhood'] if 'neighborhood' in df.columns else ['address'],
                           title="Square Footage vs Price")
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            # Calculate price per sqft
            if df['sqft'].sum() > 0:
                avg_price_per_sqft = (df['price'] / df['sqft']).mean()
                st.write(f"**Average Price per SqFt:** ${avg_price_per_sqft:.0f}")
    
    # Market trends over time (if we have date data)
    if 'file_date' in df.columns:
        st.subheader("📅 Collection Trends")
        
        # Group by date and count houses
        daily_counts = df.groupby(df['file_date'].dt.date).size().reset_index()
        daily_counts.columns = ['Date', 'Houses Collected']
        
        fig = px.line(daily_counts, x='Date', y='Houses Collected', 
                     title="Houses Collected Over Time")
        st.plotly_chart(fig, use_container_width=True)
    
    # Data quality metrics
    st.subheader("📊 Data Quality")
    
    quality_metrics = []
    
    key_fields = ['price', 'bedrooms', 'bathrooms', 'sqft', 'year_built', 'latitude', 'longitude']
    
    for field in key_fields:
        if field in df.columns:
            missing_count = df[field].isna().sum()
            missing_percent = (missing_count / len(df)) * 100
            quality_metrics.append({
                'Field': field,
                'Missing Count': missing_count,
                'Missing %': f"{missing_percent:.1f}%",
                'Data Quality': '✅ Good' if missing_percent < 10 else '⚠️ Fair' if missing_percent < 25 else '❌ Poor'
            })
    
    if quality_metrics:
        quality_df = pd.DataFrame(quality_metrics)
        st.dataframe(quality_df, use_container_width=True)

def main():
    """Main dashboard application"""
    
    st.title("📊 Zillow Data Analytics Dashboard")
    st.markdown("*Comprehensive analytics for your house hunting data collection*")
    
    # Initialize analyzer
    analyzer = ZillowDataAnalyzer()
    
    # Check if we have any data
    if not analyzer.data_files:
        st.error("❌ No Zillow data files found!")
        st.info("""
        **No data detected.** Please collect some house data first:
        
        1. Run `python zillow_collection_interface.py` to collect data
        2. Or run `python fixed_zillow_collector.py` 
        3. Or make sure your CSV files are in the current directory
        
        Looking for files like:
        - `real_zillow_data.csv`
        - `zillow_houses_*.csv`
        - `comprehensive_houses_*.csv`
        """)
        st.stop()
    
    # Load data for overview
    df, file_sources = analyzer.load_all_house_data()
    
    # Sidebar with data overview
    with st.sidebar:
        st.header("📁 Data Overview")
        st.metric("Total Houses", len(df))
        st.metric("Data Files", len(analyzer.data_files))
        
        if len(df) > 0:
            latest_file = max(file_sources.items(), key=lambda x: x[1]['modified'])
            st.write(f"**Latest:** {latest_file[0].split('/')[-1]}")
            st.write(f"**Updated:** {latest_file[1]['modified'].strftime('%m/%d %H:%M')}")
        
        st.markdown("---")
        
        # Data files list
        st.write("**Available Files:**")
        for file in analyzer.data_files:
            file_size = os.path.getsize(file) / 1024
            st.caption(f"📄 {file.split('/')[-1]} ({file_size:.1f}KB)")
        
        if st.button("🔄 Refresh Data"):
            st.cache_data.clear()
            st.rerun()
    
    # Main dashboard tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📡 API Metrics", "🏠 Classifications", "🗺️ Map View", "📈 Market Insights"])
    
    with tab1:
        display_api_metrics(analyzer)
    
    with tab2:
        display_house_classifications(analyzer)
    
    with tab3:
        display_geographic_map(analyzer)
    
    with tab4:
        display_market_insights(analyzer)
    
    # Footer with refresh timestamp
    st.markdown("---")
    st.caption(f"Dashboard last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()