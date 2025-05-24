# parameter_workshop.py
# Interactive workshop to help you choose the best scoring parameters

import streamlit as st
import pandas as pd
import plotly.express as px
import json

st.set_page_config(page_title="Parameter Workshop", page_icon="🎯", layout="wide")

st.title("🎯 House Scoring Parameter Workshop")
st.markdown("*Let's figure out what parameters actually matter for your house hunting*")

# Define all possible parameters
ALL_PARAMETERS = {
    "💰 Financial & Market": {
        "purchase_price": {
            "name": "Purchase Price",
            "description": "The listing price of the house",
            "data_availability": "✅ Available",
            "implementation": "Easy",
            "impact": "High"
        },
        "total_monthly_cost": {
            "name": "Total Monthly Cost",
            "description": "Mortgage + taxes + insurance + utilities + maintenance + HOA",
            "data_availability": "🔶 Estimated",
            "implementation": "Medium",
            "impact": "Very High"
        },
        "property_taxes": {
            "name": "Property Tax Rate",
            "description": "Annual property taxes (varies significantly by area)",
            "data_availability": "✅ Public records",
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
        "days_on_market": {
            "name": "Days on Market",
            "description": "How long the house has been listed (indicates seller motivation)",
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
        "comparable_sales": {
            "name": "Recent Comparable Sales",
            "description": "How this house compares to recent sales in area",
            "data_availability": "✅ MLS/Zillow data",
            "implementation": "Medium",
            "impact": "High"
        },
        "market_temperature": {
            "name": "Local Market Heat",
            "description": "Buyer vs seller market in this specific area",
            "data_availability": "🔶 Market analysis",
            "implementation": "Hard",
            "impact": "Medium"
        },
        "homeowners_insurance": {
            "name": "Insurance Costs",
            "description": "Annual homeowner's insurance premiums",
            "data_availability": "🔶 Insurance APIs",
            "implementation": "Medium",
            "impact": "Medium"
        },
        "hoa_fees": {
            "name": "HOA Fees & Restrictions",
            "description": "Monthly HOA costs and community restrictions",
            "data_availability": "🔶 Listing/HOA data",
            "implementation": "Medium",
            "impact": "Medium"
        },
        "rent_ratio": {
            "name": "Rent vs Buy Ratio",
            "description": "What this house would rent for vs purchase price",
            "data_availability": "🔶 Rental market data",
            "implementation": "Medium",
            "impact": "Low"
        },
        "appreciation_potential": {
            "name": "Historical Appreciation",
            "description": "How home values have grown in this area",
            "data_availability": "✅ Historical data",
            "implementation": "Medium",
            "impact": "Medium"
        }
    },
    "🏘️ Location & Neighborhood": {
        "commute_time": {
            "name": "Commute Time",
            "description": "Travel time to work during rush hour",
            "data_availability": "✅ Google Maps API",
            "implementation": "Easy",
            "impact": "High"
        },
        "multiple_commute_options": {
            "name": "Commute Flexibility",
            "description": "Driving, transit, biking options to work",
            "data_availability": "✅ Transit APIs",
            "implementation": "Medium",
            "impact": "Medium"
        },
        "school_ratings": {
            "name": "School Quality",
            "description": "Elementary, middle, and high school ratings (affects resale)",
            "data_availability": "✅ GreatSchools API",
            "implementation": "Easy",
            "impact": "High"
        },
        "school_boundaries": {
            "name": "School District Stability",
            "description": "Likelihood of school boundary changes",
            "data_availability": "🔶 District data",
            "implementation": "Hard",
            "impact": "Medium"
        },
        "crime_rate": {
            "name": "Crime Statistics",
            "description": "Violent and property crime rates in the area",
            "data_availability": "✅ FBI/Local APIs",
            "implementation": "Medium",
            "impact": "High"
        },
        "crime_trends": {
            "name": "Crime Trend Direction",
            "description": "Whether crime is increasing or decreasing",
            "data_availability": "✅ Historical crime data",
            "implementation": "Medium",
            "impact": "Medium"
        },
        "walkability": {
            "name": "Walk Score",
            "description": "Ability to walk to amenities (groceries, restaurants, etc.)",
            "data_availability": "✅ Walk Score API",
            "implementation": "Easy",
            "impact": "Medium"
        },
        "bike_score": {
            "name": "Bike Score",
            "description": "Bike-friendliness and bike lane access",
            "data_availability": "✅ Walk Score API",
            "implementation": "Easy",
            "impact": "Low"
        },
        "transit_score": {
            "name": "Transit Score",
            "description": "Public transportation accessibility",
            "data_availability": "✅ Walk Score API",
            "implementation": "Easy",
            "impact": "Medium"
        },
        "nearby_amenities": {
            "name": "Essential Amenities",
            "description": "Distance to grocery, pharmacy, gas station, bank",
            "data_availability": "✅ Google Places API",
            "implementation": "Medium",
            "impact": "Medium"
        },
        "restaurants_entertainment": {
            "name": "Dining & Entertainment",
            "description": "Restaurants, bars, theaters, cultural venues nearby",
            "data_availability": "✅ Google Places API",
            "implementation": "Medium",
            "impact": "Low"
        },
        "healthcare_access": {
            "name": "Healthcare Proximity",
            "description": "Hospitals, urgent care, specialists nearby",
            "data_availability": "✅ Google Places API",
            "implementation": "Medium",
            "impact": "Medium"
        },
        "parks_recreation": {
            "name": "Parks & Recreation",
            "description": "Parks, trails, gyms, sports facilities",
            "data_availability": "✅ Google Places API",
            "implementation": "Medium",
            "impact": "Low"
        },
        "future_development": {
            "name": "Planned Development",
            "description": "Upcoming infrastructure, shopping, transit projects",
            "data_availability": "🔶 City planning data",
            "implementation": "Hard",
            "impact": "Medium"
        },
        "zoning_restrictions": {
            "name": "Zoning & Land Use",
            "description": "Current zoning and potential for commercial development",
            "data_availability": "✅ City data",
            "implementation": "Medium",
            "impact": "Low"
        },
        "neighborhood_age": {
            "name": "Neighborhood Maturity",
            "description": "Established vs developing neighborhood",
            "data_availability": "🔶 Census/building data",
            "implementation": "Medium",
            "impact": "Low"
        },
        "population_trends": {
            "name": "Population Growth",
            "description": "Whether area is growing or declining",
            "data_availability": "✅ Census data",
            "implementation": "Easy",
            "impact": "Medium"
        },
        "demographics_fit": {
            "name": "Demographic Match",
            "description": "Age, income, lifestyle match with neighbors",
            "data_availability": "✅ Census data",
            "implementation": "Medium",
            "impact": "Low"
        }
    },
    "🏠 Property Structure & Layout": {
        "square_footage": {
            "name": "Total Square Footage",
            "description": "Total living space",
            "data_availability": "✅ Available",
            "implementation": "Easy",
            "impact": "High"
        },
        "functional_sqft": {
            "name": "Functional Square Footage",
            "description": "Usable space (excluding awkward layouts, wasted space)",
            "data_availability": "🔶 Floor plan analysis",
            "implementation": "Hard",
            "impact": "Medium"
        },
        "bedrooms_bathrooms": {
            "name": "Bedrooms & Bathrooms",
            "description": "Number and configuration of bedrooms and bathrooms",
            "data_availability": "✅ Available",
            "implementation": "Easy",
            "impact": "High"
        },
        "bedroom_sizes": {
            "name": "Bedroom Sizes",
            "description": "Whether bedrooms are adequate size vs cramped",
            "data_availability": "🔶 Floor plan data",
            "implementation": "Hard",
            "impact": "Medium"
        },
        "master_suite_quality": {
            "name": "Master Suite",
            "description": "Master bedroom size, bathroom, walk-in closet",
            "data_availability": "🔶 Listing details",
            "implementation": "Medium",
            "impact": "Medium"
        },
        "layout_efficiency": {
            "name": "Layout Quality",
            "description": "Open concept, flow, wasted space",
            "data_availability": "🔶 Floor plan analysis",
            "implementation": "Hard",
            "impact": "Medium"
        },
        "kitchen_quality": {
            "name": "Kitchen Layout & Size",
            "description": "Kitchen size, layout, counter space, storage",
            "data_availability": "🔶 Photos/listing",
            "implementation": "Hard",
            "impact": "High"
        },
        "storage_space": {
            "name": "Storage Adequacy",
            "description": "Closets, pantry, basement, attic storage",
            "data_availability": "🔶 Listing details",
            "implementation": "Medium",
            "impact": "Medium"
        },
        "ceiling_heights": {
            "name": "Ceiling Heights",
            "description": "Whether ceilings feel spacious vs cramped",
            "data_availability": "🔶 Listing/photos",
            "implementation": "Medium",
            "impact": "Low"
        },
        "natural_light": {
            "name": "Natural Light",
            "description": "Window placement, orientation, brightness",
            "data_availability": "🔶 Photos/satellite",
            "implementation": "Hard",
            "impact": "Medium"
        },
        "outdoor_living": {
            "name": "Outdoor Living Space",
            "description": "Deck, patio, porch, outdoor entertainment areas",
            "data_availability": "🔶 Listing/photos",
            "implementation": "Medium",
            "impact": "Low"
        },
        "basement_finished": {
            "name": "Basement Condition",
            "description": "Finished, unfinished, walkout, potential",
            "data_availability": "✅ Listing data",
            "implementation": "Easy",
            "impact": "Medium"
        },
        "attic_potential": {
            "name": "Attic/Expansion Potential",
            "description": "Potential to finish attic or add square footage",
            "data_availability": "🔶 Structural analysis",
            "implementation": "Hard",
            "impact": "Low"
        }
    },
    "🔧 Condition & Systems": {
        "year_built": {
            "name": "Year Built / Age",
            "description": "Age of the house (affects maintenance needs)",
            "data_availability": "✅ Available",
            "implementation": "Easy",
            "impact": "Medium"
        },
        "recent_updates": {
            "name": "Recent Renovations",
            "description": "Kitchen, bathroom, flooring updates in last 5 years",
            "data_availability": "🔶 Listing details",
            "implementation": "Medium",
            "impact": "High"
        },
        "roof_condition": {
            "name": "Roof Age & Condition",
            "description": "When roof was last replaced, current condition",
            "data_availability": "🔶 Inspection/photos",
            "implementation": "Hard",
            "impact": "High"
        },
        "hvac_age": {
            "name": "HVAC System Age",
            "description": "Heating and cooling system age and efficiency",
            "data_availability": "🔶 Inspection data",
            "implementation": "Hard",
            "impact": "High"
        },
        "electrical_plumbing": {
            "name": "Electrical & Plumbing",
            "description": "Age and condition of electrical and plumbing systems",
            "data_availability": "🔶 Inspection data",
            "implementation": "Hard",
            "impact": "High"
        },
        "windows_insulation": {
            "name": "Energy Efficiency",
            "description": "Window quality, insulation, energy costs",
            "data_availability": "🔶 Energy audit/inspection",
            "implementation": "Hard",
            "impact": "Medium"
        },
        "foundation_structure": {
            "name": "Foundation & Structure",
            "description": "Foundation condition, structural integrity",
            "data_availability": "🔶 Inspection data",
            "implementation": "Hard",
            "impact": "High"
        },
        "maintenance_backlog": {
            "name": "Deferred Maintenance",
            "description": "Estimated cost of needed repairs and updates",
            "data_availability": "🔶 Inspection estimate",
            "implementation": "Hard",
            "impact": "High"
        },
        "material_quality": {
            "name": "Build Quality",
            "description": "Quality of materials, construction, finishes",
            "data_availability": "🔶 Visual inspection",
            "implementation": "Hard",
            "impact": "Medium"
        },
        "smart_home_features": {
            "name": "Smart Home Integration",
            "description": "Smart thermostats, security, automation systems",
            "data_availability": "🔶 Listing details",
            "implementation": "Medium",
            "impact": "Low"
        }
    },
    "🌳 Lot & Outdoor Features": {
        "lot_size": {
            "name": "Lot Size",
            "description": "Total lot square footage",
            "data_availability": "✅ Available",
            "implementation": "Easy",
            "impact": "Medium"
        },
        "usable_yard": {
            "name": "Usable Yard Space",
            "description": "Flat, usable yard vs steep/unusable space",
            "data_availability": "🔶 Satellite/topo data",
            "implementation": "Medium",
            "impact": "Medium"
        },
        "yard_privacy": {
            "name": "Privacy Level",
            "description": "Fencing, trees, distance from neighbors",
            "data_availability": "🔶 Photos/satellite",
            "implementation": "Medium",
            "impact": "Medium"
        },
        "landscaping": {
            "name": "Landscaping Quality",
            "description": "Mature trees, gardens, landscape maintenance needs",
            "data_availability": "🔶 Photos",
            "implementation": "Medium",
            "impact": "Low"
        },
        "drainage_flooding": {
            "name": "Drainage & Flood Risk",
            "description": "Lot drainage, basement flooding history",
            "data_availability": "✅ FEMA flood maps",
            "implementation": "Medium",
            "impact": "Medium"
        },
        "soil_conditions": {
            "name": "Soil Quality",
            "description": "Soil stability for foundations, gardening",
            "data_availability": "🔶 Geological surveys",
            "implementation": "Hard",
            "impact": "Low"
        },
        "sun_exposure": {
            "name": "Sun/Shade Balance",
            "description": "Sunlight for gardens, natural heating/cooling",
            "data_availability": "🔶 Satellite analysis",
            "implementation": "Hard",
            "impact": "Low"
        },
        "tree_canopy": {
            "name": "Mature Trees",
            "description": "Shade, cooling, privacy from mature trees",
            "data_availability": "🔶 Satellite imagery",
            "implementation": "Medium",
            "impact": "Low"
        }
    },
    "🚗 Parking & Access": {
        "garage_parking": {
            "name": "Garage Spaces",
            "description": "Number of covered parking spaces",
            "data_availability": "✅ Available",
            "implementation": "Easy",
            "impact": "Medium"
        },
        "driveway_parking": {
            "name": "Driveway Capacity",
            "description": "Additional parking in driveway",
            "data_availability": "🔶 Photos/listing",
            "implementation": "Easy",
            "impact": "Low"
        },
        "street_parking": {
            "name": "Street Parking",
            "description": "Availability and restrictions for street parking",
            "data_availability": "🔶 Local observation",
            "implementation": "Hard",
            "impact": "Low"
        },
        "garage_size": {
            "name": "Garage Size & Storage",
            "description": "Whether garage fits large vehicles, has storage",
            "data_availability": "🔶 Listing details",
            "implementation": "Medium",
            "impact": "Low"
        },
        "workshop_space": {
            "name": "Workshop/Hobby Space",
            "description": "Space for hobbies, workshop, crafts",
            "data_availability": "🔶 Listing/photos",
            "implementation": "Medium",
            "impact": "Low"
        }
    },
    "🌍 Environmental & External Factors": {
        "noise_levels": {
            "name": "Noise Pollution",
            "description": "Traffic, airport, train, highway noise",
            "data_availability": "🔶 Noise mapping data",
            "implementation": "Medium",
            "impact": "Medium"
        },
        "air_quality": {
            "name": "Air Quality Index",
            "description": "Pollution levels, allergens, industrial proximity",
            "data_availability": "✅ EPA data",
            "implementation": "Easy",
            "impact": "Low"
        },
        "natural_disasters": {
            "name": "Natural Disaster Risk",
            "description": "Flood, earthquake, tornado, wildfire risk",
            "data_availability": "✅ FEMA/USGS data",
            "implementation": "Easy",
            "impact": "Medium"
        },
        "power_reliability": {
            "name": "Power Grid Reliability",
            "description": "Frequency of power outages in area",
            "data_availability": "🔶 Utility data",
            "implementation": "Hard",
            "impact": "Low"
        },
        "internet_infrastructure": {
            "name": "Internet Options",
            "description": "Fiber, cable, satellite internet availability",
            "data_availability": "✅ ISP coverage maps",
            "implementation": "Medium",
            "impact": "Medium"
        },
        "cell_coverage": {
            "name": "Cell Phone Coverage",
            "description": "Signal strength for major carriers",
            "data_availability": "✅ Carrier coverage maps",
            "implementation": "Easy",
            "impact": "Low"
        },
        "industrial_proximity": {
            "name": "Industrial/Commercial",
            "description": "Distance from factories, landfills, industrial areas",
            "data_availability": "✅ Mapping data",
            "implementation": "Medium",
            "impact": "Medium"
        },
        "agricultural_exposure": {
            "name": "Agricultural Area",
            "description": "Pesticide exposure, farming odors, seasonal issues",
            "data_availability": "✅ Land use data",
            "implementation": "Medium",
            "impact": "Low"
        }
    },
    "🏢 Investment & Resale": {
        "rental_potential": {
            "name": "Rental Income Potential",
            "description": "What house could rent for if needed",
            "data_availability": "🔶 Rental market data",
            "implementation": "Medium",
            "impact": "Low"
        },
        "resale_factors": {
            "name": "Resale Appeal",
            "description": "Features that appeal to future buyers",
            "data_availability": "🔶 Market analysis",
            "implementation": "Hard",
            "impact": "Medium"
        },
        "unique_features": {
            "name": "Unique Selling Points",
            "description": "Special features that differentiate the property",
            "data_availability": "🔶 Listing analysis",
            "implementation": "Medium",
            "impact": "Low"
        },
        "subdivision_reputation": {
            "name": "Subdivision Desirability",
            "description": "Reputation and desirability of specific subdivision",
            "data_availability": "🔶 Market research",
            "implementation": "Hard",
            "impact": "Medium"
        },
        "lot_premium": {
            "name": "Premium Lot Features",
            "description": "Corner lot, cul-de-sac, water view, etc.",
            "data_availability": "🔶 Lot analysis",
            "implementation": "Medium",
            "impact": "Low"
        }
    },
    "👥 Lifestyle & Community": {
        "family_friendliness": {
            "name": "Family Environment",
            "description": "Sidewalks, playgrounds, family activities",
            "data_availability": "🔶 Community observation",
            "implementation": "Hard",
            "impact": "Low"
        },
        "social_opportunities": {
            "name": "Community Engagement",
            "description": "HOA events, neighborhood groups, social activities",
            "data_availability": "🔶 Community research",
            "implementation": "Hard",
            "impact": "Low"
        },
        "pet_friendliness": {
            "name": "Pet Amenities",
            "description": "Dog parks, pet stores, veterinarians, pet policies",
            "data_availability": "🔶 Local research",
            "implementation": "Medium",
            "impact": "Low"
        },
        "senior_amenities": {
            "name": "Senior Services",
            "description": "Healthcare, senior centers, accessibility features",
            "data_availability": "🔶 Local research",
            "implementation": "Medium",
            "impact": "Low"
        },
        "cultural_diversity": {
            "name": "Cultural Diversity",
            "description": "Diversity of residents and cultural amenities",
            "data_availability": "✅ Census data",
            "implementation": "Easy",
            "impact": "Low"
        },
        "nightlife_entertainment": {
            "name": "Entertainment Options",
            "description": "Bars, clubs, theaters, nightlife for different ages",
            "data_availability": "🔶 Local research",
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
    
    # Buyer type
    st.subheader("👤 Your Situation")
    buyer_type = st.selectbox(
        "What best describes you?",
        ["First-time buyer", "Family with kids", "Empty nesters", "Investor", "Young professional", "Other"]
    )
    answers['buyer_type'] = buyer_type
    
    # Timeline
    timeline = st.selectbox(
        "How long do you plan to stay in this house?",
        ["2-5 years", "5-10 years", "10+ years", "Forever home"]
    )
    answers['timeline'] = timeline
    
    # Budget flexibility
    budget_flexibility = st.selectbox(
        "How flexible is your budget?",
        ["Very tight - every dollar matters", "Somewhat flexible", "Pretty flexible", "Money is not the primary concern"]
    )
    answers['budget_flexibility'] = budget_flexibility
    
    # Work situation
    work_situation = st.selectbox(
        "What's your work situation?",
        ["Fixed office location", "Hybrid work", "Fully remote", "Multiple office locations", "Retired"]
    )
    answers['work_situation'] = work_situation
    
    # Lifestyle priorities
    st.subheader("🎯 Lifestyle Priorities")
    
    lifestyle_factors = {
        "Low maintenance": "I want a house that doesn't need much work",
        "Good schools": "School quality is important (even if no kids yet)",
        "Walkable neighborhood": "I want to walk to things, not always drive",
        "Privacy": "I value privacy and space from neighbors", 
        "Modern amenities": "I want updated kitchens, bathrooms, etc.",
        "Investment potential": "I care about resale value and appreciation",
        "Community feel": "I want an active, friendly neighborhood",
        "Safety": "Low crime rate is very important to me"
    }
    
    selected_priorities = st.multiselect(
        "Select your top priorities (choose 3-5):",
        list(lifestyle_factors.keys()),
        help="These will help weight your scoring parameters"
    )
    answers['priorities'] = selected_priorities
    
    return answers

def recommend_parameters(answers):
    """Recommend parameters based on quiz answers"""
    
    st.header("🎯 Recommended Parameters for You")
    
    # Base recommendations
    recommendations = {
        "high_priority": [],
        "medium_priority": [],
        "low_priority": []
    }
    
    # Based on buyer type
    if answers['buyer_type'] == "First-time buyer":
        recommendations["high_priority"].extend([
            "total_monthly_cost", "purchase_price", "condition_updates"
        ])
        recommendations["medium_priority"].extend([
            "school_ratings", "commute_time", "square_footage"
        ])
    
    elif answers['buyer_type'] == "Family with kids":
        recommendations["high_priority"].extend([
            "school_ratings", "crime_rate", "square_footage", "bedrooms_bathrooms"
        ])
        recommendations["medium_priority"].extend([
            "lot_size", "nearby_amenities", "total_monthly_cost"
        ])
    
    elif answers['buyer_type'] == "Empty nesters":
        recommendations["high_priority"].extend([
            "walkability", "nearby_amenities", "total_monthly_cost", "condition_updates"
        ])
        recommendations["medium_priority"].extend([
            "square_footage", "commute_time"
        ])
        recommendations["low_priority"].extend([
            "school_ratings", "lot_size"
        ])
    
    elif answers['buyer_type'] == "Investor":
        recommendations["high_priority"].extend([
            "price_per_sqft", "days_on_market", "school_ratings", "crime_rate"
        ])
        recommendations["medium_priority"].extend([
            "future_development", "walkability"
        ])
    
    # Based on priorities
    priority_mapping = {
        "Low maintenance": ["year_built", "condition_updates", "property_taxes"],
        "Good schools": ["school_ratings"],
        "Walkable neighborhood": ["walkability", "nearby_amenities"],
        "Privacy": ["lot_size", "noise_levels"],
        "Modern amenities": ["year_built", "condition_updates"],
        "Investment potential": ["school_ratings", "price_per_sqft", "future_development"],
        "Community feel": ["crime_rate", "walkability"],
        "Safety": ["crime_rate", "natural_disasters"]
    }
    
    for priority in answers.get('priorities', []):
        if priority in priority_mapping:
            recommendations["high_priority"].extend(priority_mapping[priority])
    
    # Remove duplicates and organize
    recommendations["high_priority"] = list(set(recommendations["high_priority"]))
    recommendations["medium_priority"] = list(set(recommendations["medium_priority"]) - set(recommendations["high_priority"]))
    recommendations["low_priority"] = list(set(recommendations["low_priority"]) - set(recommendations["high_priority"]) - set(recommendations["medium_priority"]))
    
    return recommendations

def display_parameter_details(recommendations):
    """Display detailed information about recommended parameters"""
    
    priority_colors = {
        "high_priority": "🔥",
        "medium_priority": "⭐", 
        "low_priority": "💡"
    }
    
    priority_names = {
        "high_priority": "High Priority - Implement First",
        "medium_priority": "Medium Priority - Add Later",
        "low_priority": "Low Priority - Optional"
    }
    
    for priority_level, params in recommendations.items():
        if not params:
            continue
            
        st.subheader(f"{priority_colors[priority_level]} {priority_names[priority_level]}")
        
        for param_id in params:
            # Find the parameter in our data structure
            param_info = None
            category = None
            
            for cat_name, cat_params in ALL_PARAMETERS.items():
                if param_id in cat_params:
                    param_info = cat_params[param_id]
                    category = cat_name
                    break
            
            if param_info:
                with st.expander(f"{param_info['name']} ({category})"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Description:** {param_info['description']}")
                        st.write(f"**Data Source:** {param_info['data_availability']}")
                    
                    with col2:
                        st.write(f"**Implementation:** {param_info['implementation']}")
                        st.write(f"**Impact:** {param_info['impact']}")
                        
                        # Implementation difficulty color coding
                        if param_info['implementation'] == "Easy":
                            st.success("✅ Quick to implement")
                        elif param_info['implementation'] == "Medium":
                            st.warning("⚠️ Moderate effort needed")
                        else:
                            st.error("🔴 Complex implementation")

def export_recommendations(recommendations, answers):
    """Export recommendations as configuration"""
    
    st.header("📋 Your Customized Scoring System")
    
    # Create weights based on recommendations
    weights = {}
    total_params = len(recommendations["high_priority"]) + len(recommendations["medium_priority"]) + len(recommendations["low_priority"])
    
    if total_params > 0:
        # Allocate weights
        high_weight = 0.08 if recommendations["high_priority"] else 0
        med_weight = 0.05 if recommendations["medium_priority"] else 0
        low_weight = 0.02 if recommendations["low_priority"] else 0
        
        for param in recommendations["high_priority"]:
            weights[param] = high_weight
        for param in recommendations["medium_priority"]:
            weights[param] = med_weight
        for param in recommendations["low_priority"]:
            weights[param] = low_weight
        
        # Normalize weights to sum to 1
        total_weight = sum(weights.values())
        if total_weight > 0:
            weights = {k: v/total_weight for k, v in weights.items()}
    
    # Display as configuration
    config = {
        "buyer_profile": answers,
        "recommended_parameters": recommendations,
        "parameter_weights": weights
    }
    
    st.json(config)
    
    # Implementation plan
    st.subheader("🚀 Implementation Plan")
    
    phase1 = [p for p in recommendations["high_priority"] if ALL_PARAMETERS.get("💰 Financial", {}).get(p, {}).get("implementation") == "Easy"]
    phase2 = [p for p in recommendations["high_priority"] if ALL_PARAMETERS.get("💰 Financial", {}).get(p, {}).get("implementation") == "Medium"]
    
    if phase1:
        st.write("**Phase 1 (This Week):** Implement easy parameters")
        for param in phase1:
            st.write(f"  - {param}")
    
    if phase2:
        st.write("**Phase 2 (Next Month):** Add medium complexity parameters")
        for param in phase2:
            st.write(f"  - {param}")

def main():
    """Main workshop function"""
    
    tab1, tab2, tab3 = st.tabs(["🤔 Parameter Quiz", "📊 All Parameters", "🎯 Recommendations"])
    
    with tab1:
        st.markdown("Let's figure out which parameters matter most for YOUR situation:")
        answers = parameter_selection_quiz()
        
        if st.button("🎯 Get My Recommendations", type="primary"):
            st.session_state.answers = answers
            st.session_state.recommendations = recommend_parameters(answers)
            st.success("✅ Recommendations generated! Check the 'Recommendations' tab.")
    
    with tab2:
        st.markdown("Here are ALL possible parameters we could use for scoring:")
        
        for category, params in ALL_PARAMETERS.items():
            st.subheader(category)
            
            for param_id, param_info in params.items():
                with st.expander(f"{param_info['name']} - {param_info['impact']} Impact"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Description:** {param_info['description']}")
                        st.write(f"**Data:** {param_info['data_availability']}")
                    
                    with col2:
                        st.write(f"**Implementation:** {param_info['implementation']}")
                        st.write(f"**Impact:** {param_info['impact']}")
    
    with tab3:
        if hasattr(st.session_state, 'recommendations') and hasattr(st.session_state, 'answers'):
            display_parameter_details(st.session_state.recommendations)
            export_recommendations(st.session_state.recommendations, st.session_state.answers)
        else:
            st.info("👆 Take the quiz in the first tab to get personalized recommendations!")

if __name__ == "__main__":
    main()