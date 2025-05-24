# zillow_collection_interface.py
# Streamlit interface for managing the enhanced comprehensive_data_collector.py

import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from comprehensive_data_collector import EnhancedDataCollector

st.set_page_config(
    page_title="Comprehensive Data Collection Manager",
    page_icon="🏠",
    layout="wide"
)

@st.cache_resource
def get_collector():
    """Get enhanced collector instance"""
    return EnhancedDataCollector(max_calls_per_session=5)

def load_database_data():
    """Load data from the comprehensive houses SQLite database"""
    
    try:
        collector = get_collector()
        conn = sqlite3.connect(collector.db_path)
        
        # Load active houses with all scoring data
        houses_df = pd.read_sql_query('''
            SELECT * FROM houses 
            WHERE is_active = 1 
            ORDER BY overall_score DESC, last_updated DESC
        ''', conn)
        
        # Load collection activity log
        activity_df = pd.read_sql_query('''
            SELECT * FROM collection_log 
            ORDER BY date DESC
            LIMIT 30
        ''', conn)
        
        conn.close()
        
        return houses_df, activity_df
        
    except Exception as e:
        st.error(f"Error loading database: {e}")
        return pd.DataFrame(), pd.DataFrame()

def get_database_stats():
    """Get comprehensive database statistics"""
    
    try:
        collector = get_collector()
        conn = sqlite3.connect(collector.db_path)
        cursor = conn.cursor()
        
        # Total and active houses
        cursor.execute("SELECT COUNT(*) FROM houses")
        total_houses = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM houses WHERE is_active = 1")
        active_houses = cursor.fetchone()[0]
        
        # Recent activity (last 7 days)
        cutoff_date = (datetime.now() - timedelta(days=7)).isoformat()
        cursor.execute("SELECT COUNT(*) FROM houses WHERE last_updated > ?", (cutoff_date,))
        recent_houses = cursor.fetchone()[0]
        
        # Price statistics
        cursor.execute("""
            SELECT MIN(price), MAX(price), AVG(price), COUNT(*) 
            FROM houses WHERE is_active = 1 AND price > 0
        """)
        price_stats = cursor.fetchone()
        
        # Top neighborhoods
        cursor.execute("""
            SELECT neighborhood, COUNT(*) as count 
            FROM houses WHERE is_active = 1 
            GROUP BY neighborhood 
            ORDER BY count DESC 
            LIMIT 5
        """)
        top_neighborhoods = cursor.fetchall()
        
        # Today's activity
        today = datetime.now().date().isoformat()
        cursor.execute("SELECT api_calls_made, houses_collected, efficiency_ratio FROM collection_log WHERE date = ?", (today,))
        today_activity = cursor.fetchone()
        
        conn.close()
        
        return {
            "total_houses": total_houses,
            "active_houses": active_houses,
            "recent_houses": recent_houses,
            "price_min": price_stats[0] if price_stats[0] else 0,
            "price_max": price_stats[1] if price_stats[1] else 0,
            "price_avg": price_stats[2] if price_stats[2] else 0,
            "priced_houses": price_stats[3] if price_stats[3] else 0,
            "top_neighborhoods": top_neighborhoods,
            "today_calls": today_activity[0] if today_activity else 0,
            "today_houses": today_activity[1] if today_activity else 0,
            "today_efficiency": today_activity[2] if today_activity else 0
        }
        
    except Exception as e:
        st.error(f"Error getting database stats: {e}")
        return {}

def main():
    st.title("🏠 Comprehensive Data Collection Manager")
    st.markdown("*Enhanced efficiency manager for comprehensive_data_collector.py*")
    
    # Initialize collector
    collector = get_collector()
    
    # Sidebar with controls and status
    with st.sidebar:
        st.header("🎛️ Collection Controls")
        
        # Get current stats
        db_stats = get_database_stats()
        
        # Current status
        st.subheader("📊 Current Status")
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Active Houses", db_stats.get('active_houses', 0))
            st.metric("API Calls Today", db_stats.get('today_calls', 0))
        
        with col2:
            st.metric("Houses Today", db_stats.get('today_houses', 0))
            if db_stats.get('today_efficiency', 0) > 0:
                st.metric("Efficiency", f"{db_stats['today_efficiency']:.1f}/call")
            else:
                st.metric("Efficiency", "N/A")
        
        # Monthly budget simulation
        st.subheader("📈 Monthly Budget")
        monthly_calls_used = db_stats.get('today_calls', 0)  # Simplified for demo
        monthly_budget = 100
        remaining_calls = monthly_budget - monthly_calls_used
        
        progress = min(monthly_calls_used / monthly_budget, 1.0)
        st.progress(progress)
        st.write(f"**{monthly_calls_used}/{monthly_budget} calls used**")
        st.write(f"**{remaining_calls} calls remaining**")
        
        # Collection settings
        st.subheader("⚙️ Session Settings")
        
        max_calls = st.slider("Max API Calls This Session", 1, 15, 5)
        
        collection_strategy = st.selectbox(
            "Collection Strategy",
            ["Balanced (Collect + Validate)", "Collection Heavy", "Validation Heavy"]
        )
        
        st.info(f"**Expected Result:**\n{max_calls * 25}-{max_calls * 35} houses")
        
        # Main action buttons
        st.subheader("🚀 Actions")
        
        if st.button("🔄 Run Full Collection", type="primary", help="Run comprehensive collection with validation"):
            with st.spinner("Running comprehensive data collection..."):
                # Update collector settings
                collector.max_calls = max_calls
                
                # Run collection
                results = collector.run_comprehensive_collection()
                
                st.success("✅ Collection Complete!")
                
                # Show results
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("API Calls Used", results['api_calls_used'])
                    st.metric("Houses Collected", results['houses_collected'])
                
                with col2:
                    st.metric("Houses Validated", results['houses_validated'])
                    st.metric("Efficiency", f"{results['efficiency']:.1f}/call")
                
                st.info(f"📁 Data exported to: {results['csv_file']}")
                st.rerun()
        
        if st.button("✅ Validate Only", help="Only validate existing listings"):
            with st.spinner("Validating existing listings..."):
                results = collector.validate_existing_listings(max_calls)
                
                st.success("✅ Validation Complete!")
                st.json(results)
                st.rerun()
        
        if st.button("📊 Show Collector Status"):
            collector.show_current_status()
        
        if st.button("📁 Export Current Data"):
            csv_file = collector.export_comprehensive_data()
            st.success(f"✅ Exported to: {csv_file}")
    
    # Main content tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "🏠 House Browser", "📈 Collection Analytics", "⚙️ Management"])
    
    with tab1:
        st.header("📊 Collection Dashboard")
        
        # Load current data
        houses_df, activity_df = load_database_data()
        db_stats = get_database_stats()
        
        # Key metrics row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Active Houses", 
                db_stats.get('active_houses', 0),
                delta=db_stats.get('recent_houses', 0)
            )
        
        with col2:
            avg_price = db_stats.get('price_avg', 0)
            if avg_price > 0:
                st.metric("Average Price", f"${avg_price:,.0f}")
            else:
                st.metric("Average Price", "No data")
        
        with col3:
            if len(houses_df) > 0 and 'overall_score' in houses_df.columns:
                avg_score = houses_df['overall_score'].mean()
                st.metric("Average AI Score", f"{avg_score:.1%}")
            else:
                st.metric("Average AI Score", "No scores")
        
        with col4:
            if db_stats.get('today_efficiency', 0) > 0:
                st.metric("Today's Efficiency", f"{db_stats['today_efficiency']:.1f} houses/call")
            else:
                st.metric("Today's Efficiency", "No calls today")
        
        # Charts row
        if len(houses_df) > 0:
            col1, col2 = st.columns(2)
            
            with col1:
                # Price distribution
                fig_price = px.histogram(
                    houses_df, 
                    x='price', 
                    title="💰 Price Distribution of Active Houses",
                    nbins=25,
                    color_discrete_sequence=['#1f77b4']
                )
                fig_price.update_layout(height=400)
                st.plotly_chart(fig_price, use_container_width=True)
            
            with col2:
                # Score distribution
                if 'overall_score' in houses_df.columns:
                    fig_scores = px.histogram(
                        houses_df,
                        x='overall_score',
                        title="🎯 AI Score Distribution",
                        nbins=20,
                        color_discrete_sequence=['#ff7f0e']
                    )
                    fig_scores.update_layout(height=400)
                    st.plotly_chart(fig_scores, use_container_width=True)
        
        # Top neighborhoods
        if db_stats.get('top_neighborhoods'):
            st.subheader("🏘️ Top Neighborhoods by House Count")
            
            neighborhoods = [n[0] for n in db_stats['top_neighborhoods']]
            counts = [n[1] for n in db_stats['top_neighborhoods']]
            
            fig_neighborhoods = px.bar(
                x=counts,
                y=neighborhoods,
                orientation='h',
                title="Houses by Neighborhood",
                color_discrete_sequence=['#2ca02c']
            )
            fig_neighborhoods.update_layout(height=300)
            st.plotly_chart(fig_neighborhoods, use_container_width=True)
        
        # Collection efficiency over time
        if len(activity_df) > 1:
            st.subheader("📈 Collection Efficiency Trend")
            
            activity_df['date'] = pd.to_datetime(activity_df['date'])
            
            fig_efficiency = go.Figure()
            
            fig_efficiency.add_trace(go.Scatter(
                x=activity_df['date'],
                y=activity_df['efficiency_ratio'],
                mode='lines+markers',
                name='Houses per API Call',
                line=dict(color='green', width=3),
                marker=dict(size=8)
            ))
            
            fig_efficiency.update_layout(
                title="Collection Efficiency Over Time",
                xaxis_title="Date",
                yaxis_title="Houses per API Call",
                height=300,
                showlegend=False
            )
            
            st.plotly_chart(fig_efficiency, use_container_width=True)
    
    with tab2:
        st.header("🏠 House Browser")
        
        houses_df, _ = load_database_data()
        
        if len(houses_df) > 0:
            # Filters
            st.subheader("🔍 Filters")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if 'price' in houses_df.columns:
                    price_range = st.slider(
                        "Price Range",
                        min_value=int(houses_df['price'].min()),
                        max_value=int(houses_df['price'].max()),
                        value=(int(houses_df['price'].min()), int(houses_df['price'].max())),
                        format="$%d"
                    )
                else:
                    price_range = (0, 1000000)
            
            with col2:
                if 'neighborhood' in houses_df.columns:
                    neighborhoods = sorted(houses_df['neighborhood'].unique())
                    selected_neighborhoods = st.multiselect(
                        "Neighborhoods",
                        neighborhoods,
                        default=neighborhoods[:10]  # Limit default selection
                    )
                else:
                    selected_neighborhoods = []
            
            with col3:
                if 'bedrooms' in houses_df.columns:
                    min_beds = st.selectbox("Min Bedrooms", [1, 2, 3, 4, 5], index=0)
                else:
                    min_beds = 1
            
            with col4:
                if 'overall_score' in houses_df.columns:
                    min_score = st.slider("Min AI Score", 0.0, 1.0, 0.0, 0.05, format="%.0%%")
                else:
                    min_score = 0.0
            
            # Apply filters
            filtered_df = houses_df.copy()
            
            if 'price' in filtered_df.columns:
                filtered_df = filtered_df[
                    (filtered_df['price'] >= price_range[0]) &
                    (filtered_df['price'] <= price_range[1])
                ]
            
            if 'bedrooms' in filtered_df.columns:
                filtered_df = filtered_df[filtered_df['bedrooms'] >= min_beds]
            
            if selected_neighborhoods and 'neighborhood' in filtered_df.columns:
                filtered_df = filtered_df[filtered_df['neighborhood'].isin(selected_neighborhoods)]
            
            if 'overall_score' in filtered_df.columns:
                filtered_df = filtered_df[filtered_df['overall_score'] >= min_score]
            
            st.write(f"**Showing {len(filtered_df)} houses** (filtered from {len(houses_df)} total)")
            
            # Display options
            col1, col2 = st.columns([3, 1])
            
            with col1:
                view_mode = st.radio("View Mode", ["Table", "Cards"], horizontal=True)
            
            with col2:
                sort_by = st.selectbox("Sort By", 
                    ["Overall Score", "Price", "Last Updated", "Bedrooms", "Square Feet"])
            
            # Sort data
            sort_mapping = {
                "Overall Score": "overall_score",
                "Price": "price", 
                "Last Updated": "last_updated",
                "Bedrooms": "bedrooms",
                "Square Feet": "sqft"
            }
            
            sort_col = sort_mapping.get(sort_by, "overall_score")
            if sort_col in filtered_df.columns:
                filtered_df = filtered_df.sort_values(sort_col, ascending=False)
            
            # Display data
            if view_mode == "Table":
                # Table view
                display_columns = [
                    'address', 'price', 'bedrooms', 'bathrooms', 'sqft', 
                    'neighborhood', 'overall_score', 'recommendation', 'last_updated'
                ]
                
                available_columns = [col for col in display_columns if col in filtered_df.columns]
                display_df = filtered_df[available_columns].copy()
                
                # Format columns
                if 'price' in display_df.columns:
                    display_df['price'] = display_df['price'].apply(lambda x: f"${x:,.0f}")
                if 'overall_score' in display_df.columns:
                    display_df['overall_score'] = display_df['overall_score'].apply(lambda x: f"{x:.1%}")
                if 'last_updated' in display_df.columns:
                    display_df['last_updated'] = pd.to_datetime(display_df['last_updated']).dt.strftime('%m/%d/%Y')
                
                st.dataframe(
                    display_df,
                    use_container_width=True,
                    height=600
                )
            
            else:
                # Card view - show top 10
                st.subheader("🏆 Top Houses (Card View)")
                
                for idx, (_, house) in enumerate(filtered_df.head(10).iterrows()):
                    with st.expander(
                        f"#{idx+1} - {house.get('address', 'No address')} - "
                        f"${house.get('price', 0):,.0f} - "
                        f"Score: {house.get('overall_score', 0):.1%}",
                        expanded=(idx < 3)
                    ):
                        col1, col2, col3 = st.columns([2, 1, 1])
                        
                        with col1:
                            st.write("**🏠 Property Details**")
                            st.write(f"📍 **Address:** {house.get('address', 'N/A')}")
                            st.write(f"💰 **Price:** ${house.get('price', 0):,.0f}")
                            st.write(f"🏠 **Layout:** {house.get('bedrooms', 0)} bed, {house.get('bathrooms', 0)} bath")
                            st.write(f"📐 **Size:** {house.get('sqft', 0):,} sqft")
                            st.write(f"📅 **Built:** {house.get('year_built', 'N/A')}")
                            st.write(f"🏘️ **Area:** {house.get('neighborhood', 'N/A')}")
                            
                            if house.get('listing_url'):
                                st.markdown(f"🔗 **[View on Zillow]({house['listing_url']})**")
                        
                        with col2:
                            st.write("**🎯 AI Analysis**")
                            if house.get('overall_score'):
                                st.metric("Overall Score", f"{house['overall_score']:.1%}")
                            
                            if house.get('recommendation'):
                                st.write(f"**Recommendation:**")
                                st.write(house['recommendation'])
                        
                        with col3:
                            st.write("**📊 Score Breakdown**")
                            score_fields = ['price_score', 'commute_score', 'size_score', 'age_score', 'location_score']
                            
                            for field in score_fields:
                                if house.get(field) is not None:
                                    field_name = field.replace('_score', '').title()
                                    st.write(f"{field_name}: {house[field]:.2f}")
            
            # Download filtered data
            if len(filtered_df) > 0:
                csv_data = filtered_df.to_csv(index=False)
                st.download_button(
                    "📥 Download Filtered Data",
                    csv_data,
                    file_name=f"filtered_houses_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                    mime="text/csv"
                )
        
        else:
            st.info("📭 No house data available. Run data collection to populate the database.")
            if st.button("🚀 Start Data Collection"):
                st.rerun()
    
    with tab3:
        st.header("📈 Collection Analytics")
        
        _, activity_df = load_database_data()
        
        if len(activity_df) > 0:
            # Summary metrics
            col1, col2, col3, col4 = st.columns(4)
            
            total_calls = activity_df['api_calls_made'].sum()
            total_houses = activity_df['houses_collected'].sum()
            total_validated = activity_df['houses_validated'].sum()
            avg_efficiency = activity_df['efficiency_ratio'].mean()
            
            with col1:
                st.metric("Total API Calls", total_calls)
            
            with col2:
                st.metric("Total Houses Collected", total_houses)
            
            with col3:
                st.metric("Houses Validated", total_validated)
            
            with col4:
                st.metric("Average Efficiency", f"{avg_efficiency:.1f} houses/call")
            
            # Activity charts
            activity_df['date'] = pd.to_datetime(activity_df['date'])
            
            # Daily activity chart
            fig_activity = go.Figure()
            
            fig_activity.add_trace(go.Bar(
                x=activity_df['date'],
                y=activity_df['api_calls_made'],
                name='API Calls',
                marker_color='lightcoral',
                yaxis='y'
            ))
            
            fig_activity.add_trace(go.Bar(
                x=activity_df['date'],
                y=activity_df['houses_collected'],
                name='Houses Collected',
                marker_color='lightblue',
                yaxis='y'
            ))
            
            fig_activity.add_trace(go.Scatter(
                x=activity_df['date'],
                y=activity_df['efficiency_ratio'],
                mode='lines+markers',
                name='Efficiency (houses/call)',
                line=dict(color='green', width=3),
                yaxis='y2'
            ))
            
            fig_activity.update_layout(
                title="Collection Activity Over Time",
                xaxis_title="Date",
                yaxis=dict(title="Count", side="left"),
                yaxis2=dict(title="Efficiency", side="right", overlaying="y"),
                barmode='group',
                height=500
            )
            
            st.plotly_chart(fig_activity, use_container_width=True)
            
            # Performance analysis
            if len(activity_df) > 1:
                st.subheader("🎯 Performance Analysis")
                
                best_day = activity_df.loc[activity_df['efficiency_ratio'].idxmax()]
                recent_avg = activity_df.head(7)['efficiency_ratio'].mean()
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.success("**Best Performance Day**")
                    st.write(f"📅 Date: {best_day['date'].strftime('%m/%d/%Y')}")
                    st.write(f"🎯 Efficiency: {best_day['efficiency_ratio']:.1f} houses/call")
                    st.write(f"🏠 Houses: {best_day['houses_collected']}")
                    st.write(f"📞 API Calls: {best_day['api_calls_made']}")
                
                with col2:
                    st.info("**Recent Performance (7 days)**")
                    st.write(f"📈 Avg Efficiency: {recent_avg:.1f} houses/call")
                    recent_calls = activity_df.head(7)['api_calls_made'].sum()
                    recent_houses = activity_df.head(7)['houses_collected'].sum()
                    st.write(f"📞 Total Calls: {recent_calls}")
                    st.write(f"🏠 Total Houses: {recent_houses}")
                
                with col3:
                    # Trend analysis
                    if len(activity_df) >= 5:
                        recent_5 = activity_df.head(5)['efficiency_ratio'].mean()
                        older_5 = activity_df.tail(5)['efficiency_ratio'].mean()
                        trend = "📈 Improving" if recent_5 > older_5 else "📉 Declining" if recent_5 < older_5 else "➡️ Stable"
                        
                        st.warning("**Trend Analysis**")
                        st.write(f"📊 Trend: {trend}")
                        st.write(f"🔄 Recent 5 days: {recent_5:.1f}")
                        st.write(f"📜 Previous 5 days: {older_5:.1f}")
        
        else:
            st.info("📈 No analytics data available. Start collecting data to see performance metrics.")
    
    with tab4:
        st.header("⚙️ Management Tools")
        
        # Database information
        st.subheader("🗄️ Database Information")
        
        db_stats = get_database_stats()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.info("**Database Statistics**")
            st.write(f"📊 Total houses: {db_stats.get('total_houses', 0)}")
            st.write(f"✅ Active houses: {db_stats.get('active_houses', 0)}")
            st.write(f"🆕 Recent houses (7 days): {db_stats.get('recent_houses', 0)}")
            st.write(f"💰 Price range: ${db_stats.get('price_min', 0):,.0f} - ${db_stats.get('price_max', 0):,.0f}")
        
        with col2:
            st.success("**Collection Status**")
            st.write(f"📞 API calls today: {db_stats.get('today_calls', 0)}")
            st.write(f"🏠 Houses today: {db_stats.get('today_houses', 0)}")
            st.write(f"⚡ Today's efficiency: {db_stats.get('today_efficiency', 0):.1f} houses/call")
            
            # Database file info
            try:
                import os
                db_size = os.path.getsize(get_collector().db_path) / 1024 / 1024  # MB
                st.write(f"💾 Database size: {db_size:.1f} MB")
            except:
                st.write("💾 Database size: Unknown")
        
        # Manual operations
        st.subheader("🔧 Manual Operations")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🧹 Clean Database", help="Remove inactive listings older than 30 days"):
                # Placeholder for cleanup operation
                st.info("Database cleanup would remove old inactive listings")
        
        with col2:
            if st.button("🔄 Refresh All Scores", help="Recalculate AI scores for all houses"):
                st.info("This would recalculate all AI scores using current parameters")
        
        with col3:
            if st.button("📊 Database Statistics", help="Show detailed database statistics"):
                houses_df, activity_df = load_database_data()
                
                if len(houses_df) > 0:
                    st.write("**Detailed Statistics:**")
                    st.write(f"Houses with scores: {len(houses_df[houses_df['overall_score'].notna()])}")
                    st.write(f"Average score: {houses_df['overall_score'].mean():.1%}")
                    st.write(f"Neighborhoods: {houses_df['neighborhood'].nunique()}")
                    st.write(f"Price per sqft avg: ${(houses_df['price'] / houses_df['sqft']).mean():.0f}")
        
        # Export options
        st.subheader("📁 Export Options")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📥 Export All Active Houses"):
                try:
                    csv_file = collector.export_comprehensive_data()
                    st.success(f"✅ Exported to: {csv_file}")
                except Exception as e:
                    st.error(f"Export failed: {e}")
        
        with col2:
            if st.button("📊 Export Collection Log"):
                try:
                    _, activity_df = load_database_data()
                    csv_data = activity_df.to_csv(index=False)
                    st.download_button(
                        "📥 Download Collection Log",
                        csv_data,
                        file_name=f"collection_log_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
                except Exception as e:
                    st.error(f"Export failed: {e}")


if __name__ == "__main__":
    main()

st.set_page_config(
    page_title="Zillow Data Collection Manager",
    page_icon="🏠",
    layout="wide"
)

@st.cache_resource
def get_collector():
    """Get collector instance"""
    return EfficientZillowCollector()

def load_database_data():
    """Load data from SQLite database"""
    
    try:
        collector = get_collector()
        conn = sqlite3.connect(collector.db_path)
        
        # Load houses
        houses_df = pd.read_sql_query('''
            SELECT * FROM houses 
            WHERE is_active = 1 
            ORDER BY last_updated DESC
        ''', conn)
        
        # Load API usage
        usage_df = pd.read_sql_query('''
            SELECT * FROM api_usage 
            ORDER BY date DESC
            LIMIT 30
        ''', conn)
        
        conn.close()
        
        return houses_df, usage_df
        
    except Exception as e:
        st.error(f"Error loading database: {e}")
        return pd.DataFrame(), pd.DataFrame()

def main():
    st.title("🏠 Efficient Zillow Data Collection Manager")
    st.markdown("*Maximize data collection while minimizing API calls*")
    
    # Initialize collector
    collector = get_collector()
    
    # Sidebar with controls
    with st.sidebar:
        st.header("🎛️ Collection Controls")
        
        # API usage tracking
        usage_today = collector.get_api_usage_today()
        st.metric("API Calls Today", usage_today['calls_made'])
        st.metric("Houses Collected Today", usage_today['houses_collected'])
        
        if usage_today['calls_made'] > 0:
            efficiency = usage_today['houses_collected'] / usage_today['calls_made']
            st.metric("Efficiency", f"{efficiency:.1f} houses/call")
        
        # Monthly budget tracking
        st.markdown("### 📊 Monthly Budget")
        monthly_calls = usage_today['calls_made']  # Simplified for demo
        remaining_calls = 100 - monthly_calls
        
        progress = monthly_calls / 100
        st.progress(progress)
        st.write(f"Used: {monthly_calls}/100 calls ({remaining_calls} remaining)")
        
        # Collection settings
        st.markdown("### ⚙️ Collection Settings")
        
        max_calls = st.slider("Max Calls This Session", 1, 10, 5)
        
        collection_mode = st.selectbox(
            "Collection Mode",
            ["Balanced", "Validation Heavy", "Collection Heavy"]
        )
        
        # Action buttons
        st.markdown("### 🚀 Actions")
        
        if st.button("🔄 Run Data Collection", type="primary"):
            with st.spinner("Running efficient data collection..."):
                collector.max_calls_per_session = max_calls
                results = collector.run_efficient_collection()
                
                st.success("Collection complete!")
                st.json(results)
                st.rerun()
        
        if st.button("✅ Validate Listings Only"):
            with st.spinner("Validating existing listings..."):
                results = collector.validate_existing_listings(max_calls)
                st.success("Validation complete!")
                st.json(results)
                st.rerun()
        
        if st.button("📊 Database Stats"):
            stats = collector.get_current_database_stats()
            st.json(stats)
        
        if st.button("📁 Export CSV"):
            csv_file = collector.export_to_csv()
            st.success(f"Exported to {csv_file}")
    
    # Main content area
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "🏠 House Data", "📈 API Usage", "⚙️ Management"])
    
    with tab1:
        st.header("📊 Collection Dashboard")
        
        # Load current data
        houses_df, usage_df = load_database_data()
        db_stats = collector.get_current_database_stats()
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Active Houses", db_stats['active_houses'])
        
        with col2:
            if db_stats['price_avg'] > 0:
                st.metric("Average Price", f"${db_stats['price_avg']:,.0f}")
            else:
                st.metric("Average Price", "N/A")
        
        with col3:
            recent_count = len(houses_df[houses_df['last_updated'] > (datetime.now() - timedelta(days=7)).isoformat()])
            st.metric("New This Week", recent_count)
        
        with col4:
            if usage_today['calls_made'] > 0:
                efficiency = usage_today['houses_collected'] / usage_today['calls_made']
                st.metric("Collection Efficiency", f"{efficiency:.1f} houses/call")
            else:
                st.metric("Collection Efficiency", "No calls today")
        
        # Charts
        if len(houses_df) > 0:
            col1, col2 = st.columns(2)
            
            with col1:
                # Price distribution
                fig_price = px.histogram(
                    houses_df, 
                    x='price', 
                    title="💰 Price Distribution",
                    nbins=20,
                    color_discrete_sequence=['#1f77b4']
                )
                fig_price.update_layout(height=400)
                st.plotly_chart(fig_price, use_container_width=True)
            
            with col2:
                # Neighborhood distribution
                if 'neighborhood' in houses_df.columns:
                    neighborhood_counts = houses_df['neighborhood'].value_counts().head(10)
                    fig_neighborhoods = px.bar(
                        x=neighborhood_counts.values,
                        y=neighborhood_counts.index,
                        orientation='h',
                        title="🏘️ Houses by Neighborhood",
                        color_discrete_sequence=['#ff7f0e']
                    )
                    fig_neighborhoods.update_layout(height=400)
                    st.plotly_chart(fig_neighborhoods, use_container_width=True)
        
        # API usage efficiency chart
        if len(usage_df) > 0:
            st.subheader("📈 API Usage Efficiency Over Time")
            
            usage_df['date'] = pd.to_datetime(usage_df['date'])
            
            fig_efficiency = go.Figure()
            
            fig_efficiency.add_trace(go.Scatter(
                x=usage_df['date'],
                y=usage_df['efficiency_ratio'],
                mode='lines+markers',
                name='Houses per API Call',
                line=dict(color='green', width=3)
            ))
            
            fig_efficiency.update_layout(
                title="Collection Efficiency Trend",
                xaxis_title="Date",
                yaxis_title="Houses per API Call",
                height=300
            )
            
            st.plotly_chart(fig_efficiency, use_container_width=True)
    
    with tab2:
        st.header("🏠 House Data")
        
        houses_df, _ = load_database_data()
        
        if len(houses_df) > 0:
            # Filters
            col1, col2, col3 = st.columns(3)
            
            with col1:
                price_range = st.slider(
                    "Price Range",
                    min_value=int(houses_df['price'].min()),
                    max_value=int(houses_df['price'].max()),
                    value=(int(houses_df['price'].min()), int(houses_df['price'].max())),
                    format="$%d"
                )
            
            with col2:
                neighborhoods = houses_df['neighborhood'].unique() if 'neighborhood' in houses_df.columns else []
                selected_neighborhoods = st.multiselect(
                    "Neighborhoods",
                    neighborhoods,
                    default=neighborhoods
                )
            
            with col3:
                min_beds = st.selectbox("Min Bedrooms", [1, 2, 3, 4, 5], index=0)
            
            # Apply filters
            filtered_df = houses_df[
                (houses_df['price'] >= price_range[0]) &
                (houses_df['price'] <= price_range[1]) &
                (houses_df['bedrooms'] >= min_beds)
            ]
            
            if selected_neighborhoods and 'neighborhood' in filtered_df.columns:
                filtered_df = filtered_df[filtered_df['neighborhood'].isin(selected_neighborhoods)]
            
            st.write(f"Showing {len(filtered_df)} houses")
            
            # Display data
            display_columns = [
                'address', 'price', 'bedrooms', 'bathrooms', 'sqft', 
                'neighborhood', 'days_on_market', 'last_updated'
            ]
            
            available_columns = [col for col in display_columns if col in filtered_df.columns]
            
            # Format data for display
            display_df = filtered_df[available_columns].copy()
            if 'price' in display_df.columns:
                display_df['price'] = display_df['price'].apply(lambda x: f"${x:,.0f}")
            if 'last_updated' in display_df.columns:
                display_df['last_updated'] = pd.to_datetime(display_df['last_updated']).dt.strftime('%m/%d/%Y')
            
            st.dataframe(
                display_df,
                use_container_width=True,
                height=500
            )
            
            # Download filtered data
            csv_data = filtered_df.to_csv(index=False)
            st.download_button(
                "📥 Download Filtered Data",
                csv_data,
                file_name=f"filtered_houses_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        
        else:
            st.info("No house data available. Run data collection to populate the database.")
    
    with tab3:
        st.header("📈 API Usage Analytics")
        
        _, usage_df = load_database_data()
        
        if len(usage_df) > 0:
            # Usage metrics
            total_calls = usage_df['calls_made'].sum()
            total_houses = usage_df['houses_collected'].sum()
            avg_efficiency = usage_df['efficiency_ratio'].mean()
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total API Calls", total_calls)
            
            with col2:
                st.metric("Total Houses Collected", total_houses)
            
            with col3:
                st.metric("Average Efficiency", f"{avg_efficiency:.1f} houses/call")
            
            # Usage over time
            usage_df['date'] = pd.to_datetime(usage_df['date'])
            
            fig_usage = go.Figure()
            
            fig_usage.add_trace(go.Bar(
                x=usage_df['date'],
                y=usage_df['calls_made'],
                name='API Calls',
                marker_color='lightcoral'
            ))
            
            fig_usage.add_trace(go.Bar(
                x=usage_df['date'],
                y=usage_df['houses_collected'],
                name='Houses Collected',
                marker_color='lightblue'
            ))
            
            fig_usage.update_layout(
                title="Daily API Usage vs Houses Collected",
                xaxis_title="Date",
                yaxis_title="Count",
                barmode='group',
                height=400
            )
            
            st.plotly_chart(fig_usage, use_container_width=True)
            
            # Efficiency analysis
            st.subheader("🎯 Collection Efficiency Analysis")
            
            if len(usage_df) > 1:
                best_day = usage_df.loc[usage_df['efficiency_ratio'].idxmax()]
                worst_day = usage_df.loc[usage_df['efficiency_ratio'].idxmin()]
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.success("**Best Performance**")
                    st.write(f"Date: {best_day['date']}")
                    st.write(f"Efficiency: {best_day['efficiency_ratio']:.1f} houses/call")
                    st.write(f"Houses: {best_day['houses_collected']}")
                
                with col2:
                    st.warning("**Needs Improvement**")
                    st.write(f"Date: {worst_day['date']}")
                    st.write(f"Efficiency: {worst_day['efficiency_ratio']:.1f} houses/call")
                    st.write(f"Houses: {worst_day['houses_collected']}")
        
        else:
            st.info("No API usage data available. Start collecting data to see analytics.")
    
    with tab4:
        st.header("⚙️ Data Management")
        
        # Database management
        st.subheader("🗄️ Database Management")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔍 Show Database Schema"):
                schema_info = """
                **Houses Table:**
                - zpid (Primary Key)
                - address, price, bedrooms, bathrooms
                - sqft, lot_size, year_built
                - latitude, longitude, neighborhood
                - listing_url, photos, description
                - data_source, last_updated, last_validated
                - is_active (for tracking delisted properties)
                
                **API Usage Table:**
                - date, calls_made, houses_collected
                - efficiency_ratio
                """
                st.info(schema_info)
        
        with col2:
            if st.button("🧹 Clean Database"):
                # Remove duplicate entries
                st.info("Database cleaning functionality would go here")
        
        # Strategic search configuration
        st.subheader("🎯 Search Strategy Configuration")
        
        search_configs = collector.get_strategic_search_configs()
        
        st.write("**Current Search Configurations:**")
        for i, config in enumerate(search_configs[:5]):
            with st.expander(f"Search {i+1}: {config['location']} (Priority {config['priority']})"):
                st.json(config)
        
        # Manual search option
        st.subheader("🔧 Manual Search")
        
        with st.form("manual_search"):
            col1, col2 = st.columns(2)
            
            with col1:
                location = st.text_input("Location", value="Minneapolis, MN")
                max_price = st.number_input("Max Price", value=500000, step=10000)
            
            with col2:
                min_beds = st.selectbox("Min Bedrooms", [1, 2, 3, 4, 5], index=1)
                sort_by = st.selectbox("Sort By", ["priorityscore", "newest", "price_asc", "price_desc"])
            
            if st.form_submit_button("🔍 Execute Manual Search"):
                if collector.api_calls_made < collector.max_calls_per_session:
                    config = {
                        "location": location,
                        "max_price": max_price,
                        "min_beds": min_beds,
                        "sort": sort_by,
                        "expected_count": 30,
                        "priority": 1
                    }
                    
                    with st.spinner("Executing search..."):
                        houses = collector.execute_strategic_search(config)
                        
                        if houses:
                            new_count = collector.store_houses_in_database(houses)
                            st.success(f"Found {len(houses)} houses, {new_count} were new")
                            
                            # Show preview
                            preview_df = pd.DataFrame(houses[:5])
                            st.dataframe(preview_df[['address', 'price', 'bedrooms', 'sqft']])
                        else:
                            st.warning("No houses found with those criteria")
                else:
                    st.error("API call limit reached for this session")

if __name__ == "__main__":
    main()