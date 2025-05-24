# parameter_workshop_fixed.py
# Fixed version of the parameter workshop with expanded parameters

import streamlit as st
import pandas as pd
import json

st.set_page_config(page_title="Parameter Workshop", page_icon="🎯", layout="wide")

st.title("🎯 House Scoring Parameter Workshop")
st.markdown("*Let's figure out what parameters actually matter for your house hunting*")

# Expanded parameter structure with many more options
PARAMETERS = {
    "💰 Financial & Market": {
        "purchase_price": {
            "name": "Purchase Price",
            "description": "The listing price of the house",
            "data_availability": "✅ Available",
            "implementation": "Easy",
            "impact": "High"
        },
        "price_per_sqft": {
            "name": "Price per Square Foot",
            "description": "Value metric compared to area average",
            "data_availability": "✅ Calculated",
            "implementation": "Easy",
            "impact": "High"
        },
        "total_monthly_cost": {
            "name": "Total Monthly Cost",
            "description": "Mortgage + taxes + insurance + utilities estimate",
            "data_availability": "🔶 Estimated",
            "implementation": "Medium",
            "impact": "Very High"
        },
        "property_taxes": {
            "name": "Property Tax Amount",
            "description": "Annual property taxes for the home",
            "data_availability": "✅ Public records",
            "implementation": "Medium",
            "impact": "High"
        },
        "days_on_market": {
            "name": "Days on Market",
            "description": "How long the house has been listed",
            "data_availability": "✅ Zillow data",
            "implementation": "Easy",
            "impact": "Medium"
        },
        "price_history": {
            "name": "Price Change History",
            "description": "Recent price drops or increases",
            "data_availability": "✅ Zillow data",
            "implementation": "Easy",
            "impact": "Medium"
        },
        "hoa_fees": {
            "name": "HOA Fees",
            "description": "Monthly homeowners association costs",
            "data_availability": "🔶 Listing data",
            "implementation": "Medium",
            "impact": "Medium"
        },
        "zestimate_accuracy": {
            "name": "Zestimate vs List Price",
            "description": "How the price compares to Zillow's estimate",
            "data_availability": "✅ Zillow data",
            "implementation": "Easy",
            "impact": "Low"
        },
        "appreciation_history": {
            "name": "Area Appreciation Rate",
            "description": "Historical home value growth in the area",
            "data_availability": "🔶 Market data",
            "implementation": "Hard",
            "impact": "Medium"
        },
        "market_temperature": {
            "name": "Market Heat Index",
            "description": "How hot/cold the local market is",
            "data_availability": "🔶 Calculated",
            "implementation": "Medium",
            "impact": "Medium"
        }
    },
    "🏘️ Location & Neighborhood": {
        "commute_time": {
            "name": "Commute Time",
            "description": "Travel time to work/downtown",
            "data_availability": "✅ Calculated",
            "implementation": "Easy",
            "impact": "High"
        },
        "commute_options": {
            "name": "Transportation Options",
            "description": "Driving, transit, biking accessibility",
            "data_availability": "🔶 Transit APIs",
            "implementation": "Medium",
            "impact": "Medium"
        },
        "school_ratings": {
            "name": "School Quality",
            "description": "Elementary, middle, and high school ratings",
            "data_availability": "🔶 GreatSchools API",
            "implementation": "Medium",
            "impact": "High"
        },
        "school_distance": {
            "name": "Distance to Schools",
            "description": "How far to assigned schools",
            "data_availability": "🔶 Calculated",
            "implementation": "Medium",
            "impact": "Medium"
        },
        "walkability": {
            "name": "Walk Score",
            "description": "Ability to walk to amenities",
            "data_availability": "✅ Walk Score API",
            "implementation": "Medium",
            "impact": "Medium"
        },
        "bike_score": {
            "name": "Bike Score",
            "description": "Bike-friendliness of the area",
            "data_availability": "✅ Walk Score API",
            "implementation": "Medium",
            "impact": "Low"
        },
        "transit_score": {
            "name": "Transit Score",
            "description": "Public transportation access",
            "data_availability": "✅ Walk Score API",
            "implementation": "Medium",
            "impact": "Medium"
        },
        "crime_rate": {
            "name": "Crime Statistics",
            "description": "Area crime rates and safety",
            "data_availability": "✅ Crime APIs",
            "implementation": "Medium",
            "impact": "High"
        },
        "neighborhood_quality": {
            "name": "Neighborhood Desirability",
            "description": "Overall neighborhood appeal and reputation",
            "data_availability": "✅ Available",
            "implementation": "Easy",
            "impact": "High"
        },
        "grocery_distance": {
            "name": "Distance to Grocery",
            "description": "Distance to nearest quality grocery store",
            "data_availability": "✅ Google Places",
            "implementation": "Medium",
            "impact": "Medium"
        },
        "healthcare_access": {
            "name": "Healthcare Proximity",
            "description": "Distance to hospitals and medical facilities",
            "data_availability": "✅ Google Places",
            "implementation": "Medium",
            "impact": "Medium"
        },
        "entertainment_options": {
            "name": "Entertainment & Dining",
            "description": "Restaurants, bars, theaters nearby",
            "data_availability": "✅ Google Places",
            "implementation": "Medium",
            "impact": "Low"
        },
        "parks_recreation": {
            "name": "Parks & Recreation",
            "description": "Access to parks, trails, and recreation",
            "data_availability": "✅ Google Places",
            "implementation": "Medium",
            "impact": "Medium"
        },
        "noise_level": {
            "name": "Noise Pollution",
            "description": "Traffic, airport, train noise levels",
            "data_availability": "🔶 Noise maps",
            "implementation": "Hard",
            "impact": "Medium"
        },
        "future_development": {
            "name": "Planned Development",
            "description": "Upcoming area improvements or concerns",
            "data_availability": "🔴 City planning",
            "implementation": "Hard",
            "impact": "Medium"
        }
    },
    "🏠 Property Features": {
        "square_footage": {
            "name": "Total Square Footage",
            "description": "Total living space",
            "data_availability": "✅ Available",
            "implementation": "Easy",
            "impact": "High"
        },
        "bedrooms": {
            "name": "Number of Bedrooms",
            "description": "Total bedroom count",
            "data_availability": "✅ Available",
            "implementation": "Easy",
            "impact": "High"
        },
        "bathrooms": {
            "name": "Number of Bathrooms",
            "description": "Full and half bathrooms",
            "data_availability": "✅ Available",
            "implementation": "Easy",
            "impact": "High"
        },
        "master_suite": {
            "name": "Master Suite Quality",
            "description": "Master bedroom with ensuite bath",
            "data_availability": "🔶 Listing details",
            "implementation": "Medium",
            "impact": "Medium"
        },
        "kitchen_quality": {
            "name": "Kitchen Updates",
            "description": "Modern kitchen with good appliances",
            "data_availability": "🔶 Photos/listing",
            "implementation": "Hard",
            "impact": "High"
        },
        "open_floor_plan": {
            "name": "Layout Openness",
            "description": "Open concept vs traditional layout",
            "data_availability": "🔶 Photos/listing",
            "implementation": "Hard",
            "impact": "Medium"
        },
        "finished_basement": {
            "name": "Basement Status",
            "description": "Finished, unfinished, or no basement",
            "data_availability": "🔶 Listing details",
            "implementation": "Medium",
            "impact": "Medium"
        },
        "storage_space": {
            "name": "Storage Options",
            "description": "Closets, attic, basement storage",
            "data_availability": "🔶 Listing details",
            "implementation": "Medium",
            "impact": "Low"
        },
        "home_office": {
            "name": "Office Space",
            "description": "Dedicated room for home office",
            "data_availability": "🔶 Listing details",
            "implementation": "Medium",
            "impact": "Medium"
        },
        "outdoor_living": {
            "name": "Outdoor Spaces",
            "description": "Deck, patio, porch areas",
            "data_availability": "🔶 Listing details",
            "implementation": "Medium",
            "impact": "Medium"
        }
    },
    "🔧 Condition & Systems": {
        "year_built": {
            "name": "Year Built / Age",
            "description": "Age of the house",
            "data_availability": "✅ Available",
            "implementation": "Easy",
            "impact": "Medium"
        },
        "recent_updates": {
            "name": "Recent Renovations",
            "description": "Updates in last 5 years",
            "data_availability": "🔶 Listing details",
            "implementation": "Medium",
            "impact": "High"
        },
        "roof_age": {
            "name": "Roof Condition",
            "description": "Age and condition of roof",
            "data_availability": "🔴 Inspection",
            "implementation": "Hard",
            "impact": "High"
        },
        "hvac_age": {
            "name": "HVAC System Age",
            "description": "Heating/cooling system condition",
            "data_availability": "🔴 Inspection",
            "implementation": "Hard",
            "impact": "High"
        },
        "windows_quality": {
            "name": "Window Quality",
            "description": "Energy efficient windows",
            "data_availability": "🔶 Listing/photos",
            "implementation": "Hard",
            "impact": "Medium"
        },
        "insulation_quality": {
            "name": "Energy Efficiency",
            "description": "Insulation and energy costs",
            "data_availability": "🔴 Energy audit",
            "implementation": "Hard",
            "impact": "Medium"
        },
        "foundation_condition": {
            "name": "Foundation Status",
            "description": "Foundation integrity",
            "data_availability": "🔴 Inspection",
            "implementation": "Hard",
            "impact": "High"
        }
    },
    "🌳 Lot & Outdoor": {
        "lot_size": {
            "name": "Lot Size",
            "description": "Total lot square footage",
            "data_availability": "✅ Available",
            "implementation": "Easy",
            "impact": "Medium"
        },
        "usable_yard": {
            "name": "Usable Yard Space",
            "description": "Flat, usable outdoor space",
            "data_availability": "🔶 Photos/satellite",
            "implementation": "Medium",
            "impact": "Medium"
        },
        "privacy_level": {
            "name": "Privacy",
            "description": "Distance from neighbors, fencing",
            "data_availability": "🔶 Photos/satellite",
            "implementation": "Medium",
            "impact": "Medium"
        },
        "mature_trees": {
            "name": "Tree Coverage",
            "description": "Mature trees for shade and beauty",
            "data_availability": "🔶 Photos/satellite",
            "implementation": "Medium",
            "impact": "Low"
        },
        "landscaping": {
            "name": "Landscaping Quality",
            "description": "Garden and yard maintenance",
            "data_availability": "🔶 Photos",
            "implementation": "Medium",
            "impact": "Low"
        },
        "drainage": {
            "name": "Lot Drainage",
            "description": "Water drainage and flood risk",
            "data_availability": "🔶 Topography data",
            "implementation": "Hard",
            "impact": "Medium"
        },
        "corner_lot": {
            "name": "Lot Position",
            "description": "Corner lot, cul-de-sac, etc.",
            "data_availability": "✅ Available",
            "implementation": "Easy",
            "impact": "Low"
        }
    },
    "🚗 Parking & Storage": {
        "garage_spaces": {
            "name": "Garage Spaces",
            "description": "Number of covered parking spots",
            "data_availability": "✅ Available",
            "implementation": "Easy",
            "impact": "Medium"
        },
        "garage_type": {
            "name": "Garage Type",
            "description": "Attached, detached, heated",
            "data_availability": "🔶 Listing details",
            "implementation": "Medium",
            "impact": "Low"
        },
        "driveway_size": {
            "name": "Driveway Capacity",
            "description": "Additional parking space",
            "data_availability": "🔶 Photos",
            "implementation": "Medium",
            "impact": "Low"
        },
        "workshop_space": {
            "name": "Workshop/Storage",
            "description": "Extra space for hobbies",
            "data_availability": "🔶 Listing details",
            "implementation": "Medium",
            "impact": "Low"
        },
        "rv_parking": {
            "name": "RV/Boat Parking",
            "description": "Space for recreational vehicles",
            "data_availability": "🔶 Listing details",
            "implementation": "Medium",
            "impact": "Low"
        }
    },
    "🏆 Lifestyle & Special": {
        "pool_spa": {
            "name": "Pool/Spa",
            "description": "Swimming pool or hot tub",
            "data_availability": "🔶 Listing details",
            "implementation": "Medium",
            "impact": "Low"
        },
        "view_quality": {
            "name": "View",
            "description": "Water, mountain, or city views",
            "data_availability": "🔶 Photos/listing",
            "implementation": "Medium",
            "impact": "Medium"
        },
        "waterfront": {
            "name": "Water Access",
            "description": "Lake, river, or ocean access",
            "data_availability": "✅ Available",
            "implementation": "Easy",
            "impact": "High"
        },
        "pet_friendly": {
            "name": "Pet Features",
            "description": "Fenced yard, pet doors",
            "data_availability": "🔶 Listing details",
            "implementation": "Medium",
            "impact": "Low"
        },
        "smart_home": {
            "name": "Smart Home Features",
            "description": "Automation and smart devices",
            "data_availability": "🔶 Listing details",
            "implementation": "Medium",
            "impact": "Low"
        },
        "solar_panels": {
            "name": "Solar Energy",
            "description": "Solar panels installed",
            "data_availability": "🔶 Listing details",
            "implementation": "Medium",
            "impact": "Medium"
        },
        "accessibility": {
            "name": "Accessibility Features",
            "description": "Single level, wide doors, ramps",
            "data_availability": "🔶 Listing details",
            "implementation": "Medium",
            "impact": "Low"
        }
    }
}

def parameter_selection_quiz():
    """Help users identify what matters to them"""
    
    st.header("🤔 What Matters Most to You?")
    st.markdown("Answer these questions to help identify your key parameters:")
    
    answers = {}
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Buyer type
        st.subheader("👤 Your Situation")
        buyer_type = st.selectbox(
            "What best describes you?",
            ["First-time buyer", "Family with kids", "Empty nesters", 
             "Investor", "Young professional", "Remote worker", "Retiree", "Other"]
        )
        answers['buyer_type'] = buyer_type
        
        # Timeline
        timeline = st.selectbox(
            "How long do you plan to stay?",
            ["2-5 years", "5-10 years", "10+ years", "Forever home"]
        )
        answers['timeline'] = timeline
        
        # Work situation
        work_situation = st.selectbox(
            "Work situation?",
            ["Fixed office location", "Hybrid work", "Fully remote", 
             "Multiple locations", "Retired", "Self-employed"]
        )
        answers['work_situation'] = work_situation
    
    with col2:
        # Budget flexibility
        st.subheader("💰 Financial")
        budget_flexibility = st.selectbox(
            "Budget flexibility?",
            ["Very tight", "Somewhat flexible", "Pretty flexible", "Very flexible"]
        )
        answers['budget_flexibility'] = budget_flexibility
        
        # Down payment
        down_payment = st.selectbox(
            "Down payment readiness?",
            ["<10%", "10-20%", "20%+", "Cash buyer"]
        )
        answers['down_payment'] = down_payment
        
        # Monthly budget
        monthly_comfort = st.selectbox(
            "Monthly payment comfort?",
            ["Very conservative", "Conservative", "Moderate", "Aggressive"]
        )
        answers['monthly_comfort'] = monthly_comfort
    
    # Lifestyle priorities
    st.subheader("🎯 Lifestyle Priorities")
    st.markdown("Select your top priorities (choose 5-8):")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Living Priorities**")
        p1 = st.checkbox("Low maintenance")
        p2 = st.checkbox("Good schools")
        p3 = st.checkbox("Walkable area")
        p4 = st.checkbox("Privacy")
        p5 = st.checkbox("Modern updates")
    
    with col2:
        st.markdown("**Space Priorities**")
        p6 = st.checkbox("Large yard")
        p7 = st.checkbox("Home office")
        p8 = st.checkbox("Storage space")
        p9 = st.checkbox("Entertainment space")
        p10 = st.checkbox("Workshop/hobby space")
    
    with col3:
        st.markdown("**Value Priorities**")
        p11 = st.checkbox("Investment potential")
        p12 = st.checkbox("Energy efficiency")
        p13 = st.checkbox("Move-in ready")
        p14 = st.checkbox("Future expansion")
        p15 = st.checkbox("Unique features")
    
    selected_priorities = []
    priority_names = [
        "Low maintenance", "Good schools", "Walkable area", "Privacy", "Modern updates",
        "Large yard", "Home office", "Storage space", "Entertainment space", "Workshop/hobby space",
        "Investment potential", "Energy efficiency", "Move-in ready", "Future expansion", "Unique features"
    ]
    
    for i, (p, name) in enumerate(zip([p1,p2,p3,p4,p5,p6,p7,p8,p9,p10,p11,p12,p13,p14,p15], priority_names)):
        if p:
            selected_priorities.append(name)
    
    answers['priorities'] = selected_priorities
    
    # Deal breakers
    st.subheader("🚫 Deal Breakers")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Must NOT have:**")
        db1 = st.checkbox("HOA restrictions")
        db2 = st.checkbox("Busy street")
        db3 = st.checkbox("Bad schools")
        db4 = st.checkbox("Long commute (>45min)")
        db5 = st.checkbox("Major repairs needed")
    
    with col2:
        st.markdown("**Must have:**")
        db6 = st.checkbox("Garage required")
        db7 = st.checkbox("Yard required")
        db8 = st.checkbox("2+ bathrooms")
        db9 = st.checkbox("Basement required")
        db10 = st.checkbox("Single level required")
    
    deal_breakers = []
    if db1: deal_breakers.append("HOA restrictions")
    if db2: deal_breakers.append("Busy street")
    if db3: deal_breakers.append("Bad schools")
    if db4: deal_breakers.append("Long commute")
    if db5: deal_breakers.append("Major repairs")
    if db6: deal_breakers.append("No garage")
    if db7: deal_breakers.append("No yard")
    if db8: deal_breakers.append("Less than 2 bathrooms")
    if db9: deal_breakers.append("No basement")
    if db10: deal_breakers.append("Multi-level")
    
    answers['deal_breakers'] = deal_breakers
    
    return answers

def recommend_parameters(answers):
    """Recommend parameters based on quiz answers"""
    
    recommendations = {
        "high_priority": [],
        "medium_priority": [],
        "low_priority": []
    }
    
    # Core parameters everyone needs
    core_params = ["purchase_price", "square_footage", "bedrooms", "bathrooms"]
    recommendations["high_priority"].extend(core_params)
    
    # Based on buyer type
    buyer_type_params = {
        "First-time buyer": {
            "high": ["price_per_sqft", "total_monthly_cost", "property_taxes"],
            "medium": ["year_built", "recent_updates", "days_on_market"],
            "low": ["pool_spa", "view_quality"]
        },
        "Family with kids": {
            "high": ["school_ratings", "school_distance", "crime_rate", "usable_yard"],
            "medium": ["parks_recreation", "finished_basement", "storage_space"],
            "low": ["smart_home", "workshop_space"]
        },
        "Empty nesters": {
            "high": ["master_suite", "accessibility", "healthcare_access"],
            "medium": ["walkability", "maintenance_level", "single_level"],
            "low": ["school_ratings", "school_distance"]
        },
        "Investor": {
            "high": ["price_per_sqft", "appreciation_history", "rental_potential"],
            "medium": ["market_temperature", "neighborhood_quality", "crime_rate"],
            "low": ["personal_preferences", "unique_features"]
        },
        "Young professional": {
            "high": ["commute_time", "commute_options", "entertainment_options"],
            "medium": ["walkability", "modern_updates", "smart_home"],
            "low": ["school_ratings", "large_yard", "storage_space"]
        },
        "Remote worker": {
            "high": ["home_office", "internet_quality", "square_footage"],
            "medium": ["quiet_area", "outdoor_living", "walkability"],
            "low": ["commute_time", "commute_options"]
        }
    }
    
    # Add buyer-specific parameters
    buyer_params = buyer_type_params.get(answers['buyer_type'], {})
    for priority in ["high", "medium", "low"]:
        params = buyer_params.get(priority, [])
        target_list = f"{priority}_priority"
        for param in params:
            if param in [p for cat in PARAMETERS.values() for p in cat.keys()]:
                recommendations[target_list].append(param)
    
    # Based on work situation
    if answers['work_situation'] in ["Fixed office location", "Hybrid work"]:
        recommendations["high_priority"].extend(["commute_time", "commute_options"])
    elif answers['work_situation'] == "Fully remote":
        recommendations["high_priority"].append("home_office")
        recommendations["low_priority"].append("commute_time")
    
    # Based on priorities
    priority_mapping = {
        "Low maintenance": ["year_built", "recent_updates", "roof_age", "hvac_age"],
        "Good schools": ["school_ratings", "school_distance"],
        "Walkable area": ["walkability", "transit_score", "grocery_distance"],
        "Privacy": ["lot_size", "privacy_level", "corner_lot"],
        "Modern updates": ["kitchen_quality", "recent_updates", "smart_home"],
        "Large yard": ["lot_size", "usable_yard", "landscaping"],
        "Home office": ["home_office", "square_footage", "quiet_area"],
        "Storage space": ["storage_space", "garage_spaces", "finished_basement"],
        "Investment potential": ["appreciation_history", "school_ratings", "neighborhood_quality"],
        "Energy efficiency": ["insulation_quality", "windows_quality", "solar_panels"]
    }
    
    for priority in answers.get('priorities', []):
        if priority in priority_mapping:
            for param in priority_mapping[priority]:
                if param in [p for cat in PARAMETERS.values() for p in cat.keys()]:
                    if param not in recommendations["high_priority"]:
                        recommendations["high_priority"].append(param)
    
    # Based on budget constraints
    if answers['budget_flexibility'] == "Very tight":
        recommendations["high_priority"].extend(["total_monthly_cost", "property_taxes", "hoa_fees"])
    
    # Remove duplicates and limit counts
    all_params = set()
    for priority_level in ["high_priority", "medium_priority", "low_priority"]:
        # Remove items that are already in higher priority levels
        recommendations[priority_level] = [
            p for p in recommendations[priority_level] 
            if p not in all_params and p in [param for cat in PARAMETERS.values() for param in cat.keys()]
        ]
        all_params.update(recommendations[priority_level])
    
    # Limit to reasonable numbers
    recommendations["high_priority"] = recommendations["high_priority"][:12]
    recommendations["medium_priority"] = recommendations["medium_priority"][:10]
    recommendations["low_priority"] = recommendations["low_priority"][:8]
    
    return recommendations

def display_recommendations(recommendations, answers):
    """Display parameter recommendations"""
    
    st.header("🎯 Your Personalized Parameters")
    
    # Count total parameters
    total_params = (len(recommendations["high_priority"]) + 
                   len(recommendations["medium_priority"]) + 
                   len(recommendations["low_priority"]))
    
    st.info(f"Based on your answers, we recommend focusing on {total_params} key parameters.")
    
    # Create scoring weights
    weights = {}
    
    # Weight allocation strategy
    high_weight = 0.6 / max(len(recommendations["high_priority"]), 1)
    medium_weight = 0.3 / max(len(recommendations["medium_priority"]), 1)
    low_weight = 0.1 / max(len(recommendations["low_priority"]), 1)
    
    for param in recommendations["high_priority"]:
        weights[param] = high_weight
    
    for param in recommendations["medium_priority"]:
        weights[param] = medium_weight
    
    for param in recommendations["low_priority"]:
        weights[param] = low_weight
    
    # Display in tabs
    tab1, tab2, tab3 = st.tabs(["🔥 High Priority", "⭐ Medium Priority", "💡 Low Priority"])
    
    with tab1:
        st.markdown("**Focus most of your attention on these:**")
        for param_id in recommendations["high_priority"]:
            # Find the parameter info
            param_info = None
            category_name = None
            for category, params in PARAMETERS.items():
                if param_id in params:
                    param_info = params[param_id]
                    category_name = category
                    break
            
            if param_info:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**{param_info['name']}** ({category_name})")
                    st.caption(f"{param_info['description']}")
                with col2:
                    st.metric("Weight", f"{weights.get(param_id, 0):.1%}")
                
                # Show implementation details
                cols = st.columns(3)
                with cols[0]:
                    st.caption(f"Data: {param_info['data_availability']}")
                with cols[1]:
                    st.caption(f"Setup: {param_info['implementation']}")
                with cols[2]:
                    st.caption(f"Impact: {param_info['impact']}")
                
                st.divider()
    
    with tab2:
        st.markdown("**Important but secondary factors:**")
        for param_id in recommendations["medium_priority"]:
            param_info = None
            category_name = None
            for category, params in PARAMETERS.items():
                if param_id in params:
                    param_info = params[param_id]
                    category_name = category
                    break
            
            if param_info:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**{param_info['name']}** ({category_name})")
                    st.caption(f"{param_info['description']}")
                with col2:
                    st.metric("Weight", f"{weights.get(param_id, 0):.1%}")
                st.divider()
    
    with tab3:
        st.markdown("**Nice to have but not critical:**")
        for param_id in recommendations["low_priority"]:
            param_info = None
            category_name = None
            for category, params in PARAMETERS.items():
                if param_id in params:
                    param_info = params[param_id]
                    category_name = category
                    break
            
            if param_info:
                st.write(f"**{param_info['name']}**")
                st.caption(f"{param_info['description']} (Weight: {weights.get(param_id, 0):.1%})")
    
    # Export configuration
    st.header("📋 Your Custom Configuration")
    
    # Implementation readiness check
    easy_params = []
    medium_params = []
    hard_params = []
    
    all_params = (recommendations["high_priority"] + 
                  recommendations["medium_priority"] + 
                  recommendations["low_priority"])
    
    for param_id in all_params:
        for category, params in PARAMETERS.items():
            if param_id in params:
                impl = params[param_id].get("implementation", "Unknown")
                if impl == "Easy":
                    easy_params.append(param_id)
                elif impl == "Medium":
                    medium_params.append(param_id)
                elif impl == "Hard":
                    hard_params.append(param_id)
                break
    
    # Create configuration
    config = {
        "buyer_profile": answers,
        "parameters": {
            "high_priority": recommendations["high_priority"],
            "medium_priority": recommendations["medium_priority"],
            "low_priority": recommendations["low_priority"]
        },
        "weights": weights,
        "implementation_status": {
            "ready_now": easy_params,
            "needs_setup": medium_params,
            "requires_work": hard_params
        },
        "total_parameters": total_params,
        "generated_date": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Display configuration
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.json(config)
    
    with col2:
        # Download button
        json_str = json.dumps(config, indent=2)
        st.download_button(
            label="💾 Download Configuration",
            data=json_str,
            file_name=f"house_scoring_config_{answers['buyer_type'].lower().replace(' ', '_')}.json",
            mime="application/json"
        )
    
    # Implementation guide
    st.header("🚀 Implementation Guide")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("✅ Ready to Use")
        st.markdown("These parameters can be implemented immediately:")
        for param in easy_params[:5]:  # Show first 5
            param_name = next((p['name'] for cat in PARAMETERS.values() for k, p in cat.items() if k == param), param)
            st.write(f"• {param_name}")
        if len(easy_params) > 5:
            st.caption(f"...and {len(easy_params)-5} more")
    
    with col2:
        st.subheader("⏳ Need Setup")
        st.markdown("These require API keys or data sources:")
        for param in medium_params[:5]:
            param_name = next((p['name'] for cat in PARAMETERS.values() for k, p in cat.items() if k == param), param)
            st.write(f"• {param_name}")
        if len(medium_params) > 5:
            st.caption(f"...and {len(medium_params)-5} more")
    
    with col3:
        st.subheader("🔧 Advanced")
        st.markdown("These need significant work:")
        for param in hard_params[:5]:
            param_name = next((p['name'] for cat in PARAMETERS.values() for k, p in cat.items() if k == param), param)
            st.write(f"• {param_name}")
        if len(hard_params) > 5:
            st.caption(f"...and {len(hard_params)-5} more")
    
    # Quick start code
    st.header("💻 Quick Start Code")
    
    code = f"""# Import your configuration
import json

with open('house_scoring_config_{answers['buyer_type'].lower().replace(' ', '_')}.json', 'r') as f:
    config = json.load(f)

# Extract weights
weights = config['weights']

# Score a house based on your priorities
def score_house(house_data):
    total_score = 0
    
    # Example scoring for ready-to-use parameters
    if 'purchase_price' in weights:
        price_score = calculate_price_score(house_data['price'])
        total_score += price_score * weights['purchase_price']
    
    if 'square_footage' in weights:
        size_score = calculate_size_score(house_data['sqft'])
        total_score += size_score * weights['square_footage']
    
    # Add more parameters as you implement them
    
    return total_score
"""
    
    st.code(code, language='python')

def display_all_parameters():
    """Display all available parameters in an organized way"""
    
    st.header("📊 Complete Parameter Reference")
    
    # Summary statistics
    total_params = sum(len(params) for params in PARAMETERS.values())
    easy_count = sum(1 for cat in PARAMETERS.values() for p in cat.values() if p['implementation'] == 'Easy')
    available_count = sum(1 for cat in PARAMETERS.values() for p in cat.values() if '✅' in p['data_availability'])
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Parameters", total_params)
    with col2:
        st.metric("Easy to Implement", easy_count)
    with col3:
        st.metric("Data Available", available_count)
    
    # Filter options
    st.subheader("🔍 Filter Parameters")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        filter_category = st.selectbox(
            "Category",
            ["All"] + list(PARAMETERS.keys())
        )
    
    with col2:
        filter_implementation = st.selectbox(
            "Implementation Difficulty",
            ["All", "Easy", "Medium", "Hard"]
        )
    
    with col3:
        filter_impact = st.selectbox(
            "Impact Level",
            ["All", "High", "Medium", "Low", "Very High"]
        )
    
    # Display filtered parameters
    for category, params in PARAMETERS.items():
        if filter_category != "All" and category != filter_category:
            continue
        
        # Filter params
        filtered_params = {}
        for param_id, param_info in params.items():
            if filter_implementation != "All" and param_info['implementation'] != filter_implementation:
                continue
            if filter_impact != "All" and param_info['impact'] != filter_impact:
                continue
            filtered_params[param_id] = param_info
        
        if filtered_params:
            st.subheader(category)
            
            # Create expandable sections for each parameter
            for param_id, info in filtered_params.items():
                with st.expander(f"{info['name']} - {info['impact']} Impact"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Description:** {info['description']}")
                        st.write(f"**Parameter ID:** `{param_id}`")
                        
                        # Data availability with color coding
                        if "✅" in info['data_availability']:
                            st.success(f"**Data:** {info['data_availability']}")
                        elif "🔶" in info['data_availability']:
                            st.warning(f"**Data:** {info['data_availability']}")
                        else:
                            st.error(f"**Data:** {info['data_availability']}")
                    
                    with col2:
                        # Implementation difficulty with color coding
                        if info['implementation'] == "Easy":
                            st.success(f"**Implementation:** {info['implementation']}")
                        elif info['implementation'] == "Medium":
                            st.warning(f"**Implementation:** {info['implementation']}")
                        else:
                            st.error(f"**Implementation:** {info['implementation']}")
                        
                        st.write(f"**Impact:** {info['impact']}")
                        
                        # Suggested data sources
                        if param_id == "school_ratings":
                            st.caption("💡 Data source: GreatSchools.org API")
                        elif param_id in ["walkability", "bike_score", "transit_score"]:
                            st.caption("💡 Data source: WalkScore.com API")
                        elif param_id == "crime_rate":
                            st.caption("💡 Data source: Local police data APIs")
                        elif param_id in ["grocery_distance", "healthcare_access", "parks_recreation"]:
                            st.caption("💡 Data source: Google Places API")

def main():
    """Main workshop function"""
    
    tab1, tab2, tab3, tab4 = st.tabs(["🤔 Parameter Quiz", "📊 All Parameters", "🎯 Your Results", "📚 Help"])
    
    with tab1:
        answers = parameter_selection_quiz()
        
        if st.button("🎯 Get My Recommendations", type="primary", key="get_recommendations"):
            if len(answers.get('priorities', [])) < 3:
                st.error("Please select at least 3 lifestyle priorities!")
            else:
                st.session_state.answers = answers
                st.session_state.recommendations = recommend_parameters(answers)
                st.success("✅ Recommendations generated! Check the 'Your Results' tab.")
    
    with tab2:
        display_all_parameters()
    
    with tab3:
        if hasattr(st.session_state, 'recommendations') and hasattr(st.session_state, 'answers'):
            display_recommendations(st.session_state.recommendations, st.session_state.answers)
        else:
            st.info("👆 Take the quiz in the first tab to get personalized recommendations!")
            
            # Show example configuration
            st.subheader("📋 Example Configuration")
            example_config = {
                "buyer_profile": {
                    "buyer_type": "Family with kids",
                    "work_situation": "Hybrid work",
                    "priorities": ["Good schools", "Large yard", "Low maintenance"]
                },
                "weights": {
                    "school_ratings": 0.15,
                    "school_distance": 0.10,
                    "usable_yard": 0.10,
                    "crime_rate": 0.10,
                    "commute_time": 0.10,
                    "purchase_price": 0.10,
                    "square_footage": 0.08,
                    "year_built": 0.08,
                    "recent_updates": 0.07,
                    "bedrooms": 0.07,
                    "neighborhood_quality": 0.05
                }
            }
            st.json(example_config)
    
    with tab4:
        st.header("📚 How to Use This Tool")
        
        st.markdown("""
        ### 🎯 Purpose
        This tool helps you identify which factors matter most for YOUR house search, 
        then creates a custom scoring system tailored to your needs.
        
        ### 📝 Steps
        1. **Take the Quiz** - Answer questions about your situation and priorities
        2. **Get Recommendations** - See which parameters matter most for you
        3. **Download Config** - Get a JSON file with your custom weights
        4. **Implement Scoring** - Use the config in your house hunting system
        
        ### 🏆 Parameter Categories
        
        **💰 Financial & Market**
        - Focus on affordability, value, and investment potential
        - Includes price, taxes, HOA fees, market trends
        
        **🏘️ Location & Neighborhood**  
        - Everything about where the house is located
        - Commute, schools, walkability, safety, amenities
        
        **🏠 Property Features**
        - Physical characteristics of the house
        - Rooms, layout, updates, special features
        
        **🔧 Condition & Systems**
        - Age and condition of major systems
        - Roof, HVAC, foundation, energy efficiency
        
        **🌳 Lot & Outdoor**
        - Outdoor space and landscaping
        - Yard size, privacy, drainage, trees
        
        **🚗 Parking & Storage**
        - Garage, driveway, storage options
        - Workshop space, RV parking
        
        **🏆 Lifestyle & Special**
        - Unique features and lifestyle amenities
        - Pool, views, smart home, accessibility
        
        ### 📊 Understanding Weights
        - **High Priority (10-15% each)** - Critical factors for your decision
        - **Medium Priority (5-10% each)** - Important but not deal-breakers
        - **Low Priority (2-5% each)** - Nice to have but not essential
        
        ### 🚀 Next Steps
        After getting your configuration:
        1. Start with "Easy" implementation parameters
        2. Add data sources for "Medium" parameters
        3. Consider which "Hard" parameters are worth the effort
        4. Use weights in your scoring algorithm
        5. Adjust weights based on real-world results
        """)
        
        st.info("""
        💡 **Pro Tip**: Start simple! Focus on 5-10 key parameters that are easy to implement. 
        You can always add more sophisticated parameters later as your system evolves.
        """)

if __name__ == "__main__":
    main()