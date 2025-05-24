# streamlit_app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from quick_start_scorer import QuickHouseScorer, analyze_houses

st.set_page_config(page_title="AI House Hunter", page_icon="🏠", layout="wide")

def main():
    st.title("🏠 AI-Powered House Hunter")
    st.markdown("*Data-driven home search with personalized scoring*")
    
    # Sidebar for preferences
    with st.sidebar:
        st.header("🎯 Your Preferences")
        
        max_budget = st.number_input("Max Budget ($)", value=400000, step=10000)
        max_commute = st.slider("Max Commute (minutes)", 15, 45, 30)
        min_bedrooms = st.selectbox("Min Bedrooms", [2, 3, 4, 5], index=1)
        min_sqft = st.number_input("Min Square Feet", value=1200, step=100)
        min_year = st.number_input("Min Year Built", value=2000, step=5)
        
        st.subheader("Scoring Weights")
        price_weight = st.slider("Price Importance", 0.0, 0.5, 0.25, 0.05)
        commute_weight = st.slider("Commute Importance", 0.0, 0.5, 0.20, 0.05)
        size_weight = st.slider("Size Importance", 0.0, 0.3, 0.15, 0.05)
        
        update_prefs = st.button("Update Analysis")
    
    # Main content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("📊 House Analysis")
        
        # Load and analyze data
        try:
            # Create scorer with custom preferences
            scorer = QuickHouseScorer()
            scorer.max_budget = max_budget
            scorer.max_commute_minutes = max_commute
            scorer.min_bedrooms = min_bedrooms
            scorer.min_sqft = min_sqft
            scorer.min_year_built = min_year
            
            # Update weights
            scorer.weights['price'] = price_weight
            scorer.weights['commute'] = commute_weight
            scorer.weights['size'] = size_weight
            
            # Analyze houses
            results_df = analyze_houses()
            
            if len(results_df) > 0:
                # Filter viable houses
                viable_houses = results_df[results_df['is_viable']]
                
                st.metric("Total Houses Analyzed", len(results_df))
                col_a, col_b, col_c = st.columns(3)
                
                with col_a:
                    st.metric("Meet Criteria", len(viable_houses))
                with col_b:
                    if len(viable_houses) > 0:
                        avg_score = viable_houses['overall_score'].mean()
                        st.metric("Avg Score", f"{avg_score:.1%}")
                with col_c:
                    if len(viable_houses) > 0:
                        avg_price = viable_houses['price'].mean()
                        st.metric("Avg Price", f"${avg_price:,.0f}")
                
                # Top houses table
                st.subheader("🏆 Top Houses")
                
                # Create display dataframe
                display_df = viable_houses.head(10).copy()
                display_df['Score'] = display_df['overall_score'].apply(lambda x: f"{x:.1%}")
                display_df['Price'] = display_df['price'].apply(lambda x: f"${x:,}")
                display_df['Commute'] = display_df.get('estimated_commute_minutes', 0).apply(lambda x: f"{x:.0f} min")
                
                st.dataframe(
                    display_df[['address', 'Score', 'Price', 'sqft', 'bedrooms', 'Commute']],
                    column_config={
                        "address": "Address",
                        "Score": st.column_config.TextColumn("AI Score"),
                        "Price": "Price", 
                        "sqft": "Sq Ft",
                        "bedrooms": "Beds",
                        "Commute": "Commute"
                    },
                    hide_index=True
                )
                
                # Detailed house cards
                st.subheader("📋 Detailed Analysis")
                
                for idx, house in viable_houses.head(5).iterrows():
                    with st.expander(f"{house['address']} - Score: {house['overall_score']:.1%}"):
                        col_x, col_y = st.columns(2)
                        
                        with col_x:
                            st.write("**Property Details**")
                            st.write(f"Price: ${house['price']:,}")
                            st.write(f"Size: {house['sqft']} sqft")
                            st.write(f"Bedrooms: {house['bedrooms']}")
                            st.write(f"Year Built: {house['year_built']}")
                            st.write(f"Commute: ~{house.get('estimated_commute_minutes', 'N/A')} minutes")
                        
                        with col_y:
                            st.write("**Score Breakdown**")
                            
                            # Create score visualization
                            score_data = {
                                'Category': ['Price', 'Commute', 'Size', 'Age', 'Value', 'Requirements'],
                                'Score': [
                                    house['price_score'],
                                    house['commute_score'], 
                                    house['size_score'],
                                    house['age_score'],
                                    house['value_score'],
                                    house['requirements_score']
                                ]
                            }
                            
                            fig = px.bar(
                                score_data, 
                                x='Category', 
                                y='Score',
                                title=f"Score Breakdown",
                                color='Score',
                                color_continuous_scale='RdYlGn'
                            )
                            fig.update_layout(height=300, showlegend=False)
                            st.plotly_chart(fig, use_container_width=True)
            
            else:
                st.warning("No house data found. Please run manual_data_collection.py first.")
        
        except FileNotFoundError:
            st.error("❌ No house data found!")
            st.info("👉 Please run `python manual_data_collection.py` first to create sample data")
    
    with col2:
        st.header("📈 Market Overview")
        
        try:
            results_df = analyze_houses()
            
            if len(results_df) > 0:
                # Price distribution
                fig_price = px.histogram(
                    results_df, 
                    x='price', 
                    title="Price Distribution",
                    nbins=10
                )
                fig_price.update_layout(height=300)
                st.plotly_chart(fig_price, use_container_width=True)
                
                # Score vs Price scatter
                fig_scatter = px.scatter(
                    results_df,
                    x='price',
                    y='overall_score',
                    size='sqft',
                    color='overall_score',
                    title="Score vs Price",
                    color_continuous_scale='RdYlGn'
                )
                fig_scatter.update_layout(height=300)
                st.plotly_chart(fig_scatter, use_container_width=True)
                
                # Key insights
                st.subheader("🔍 Key Insights")
                
                viable = results_df[results_df['is_viable']]
                if len(viable) > 0:
                    best_value = viable.loc[viable['value_score'].idxmax()]
                    shortest_commute = viable.loc[viable['commute_score'].idxmax()]
                    
                    st.write(f"**Best Value**: {best_value['address'][:30]}...")
                    st.write(f"**Shortest Commute**: {shortest_commute['address'][:30]}...")
                    
                    # Market stats
                    avg_price_per_sqft = (viable['price'] / viable['sqft']).mean()
                    st.write(f"**Avg $/sqft**: ${avg_price_per_sqft:.0f}")
        
        except:
            st.info("Add house data to see market insights")

if __name__ == "__main__":
    main()