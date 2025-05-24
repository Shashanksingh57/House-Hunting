# parameter_definitions.py
# Pure data structures and logic - NO STREAMLIT IMPORTS
# This can be imported safely without triggering Streamlit commands

# Comprehensive parameter structure with many more options
PARAMETERS = {
    "💰 Financial & Market": {
        "purchase_price": {
            "name": "Purchase Price",
            "description": "The listing price of the house",
            "data_availability": "✅ Available",
            "implementation": "Easy",
            "impact": "High",
            "type": "number",
            "unit": "$"
        },
        "price_per_sqft": {
            "name": "Price per Square Foot",
            "description": "Value metric compared to area average",
            "data_availability": "✅ Calculated",
            "implementation": "Easy",
            "impact": "High",
            "type": "number",
            "unit": "$/sqft"
        },
        "total_monthly_cost": {
            "name": "Total Monthly Cost",
            "description": "Mortgage + taxes + insurance + utilities estimate",
            "data_availability": "🔶 Estimated",
            "implementation": "Medium",
            "impact": "Very High",
            "type": "number",
            "unit": "$/month"
        },
        "property_taxes": {
            "name": "Property Tax Amount",
            "description": "Annual property taxes for the home",
            "data_availability": "✅ Public records",
            "implementation": "Medium",
            "impact": "High",
            "type": "number",
            "unit": "$/year"
        },
        "days_on_market": {
            "name": "Days on Market",
            "description": "How long the house has been listed",
            "data_availability": "✅ Zillow data",
            "implementation": "Easy",
            "impact": "Medium",
            "type": "number",
            "unit": "days"
        },
        "price_history": {
            "name": "Price Change History",
            "description": "Recent price drops or increases",
            "data_availability": "✅ Zillow data",
            "implementation": "Easy",
            "impact": "Medium",
            "type": "number",
            "unit": "$"
        },
        "hoa_fees": {
            "name": "HOA Fees",
            "description": "Monthly homeowners association costs",
            "data_availability": "🔶 Listing data",
            "implementation": "Medium",
            "impact": "Medium",
            "type": "number",
            "unit": "$/month"
        }
    },
    "🏘️ Location & Neighborhood": {
        "commute_time": {
            "name": "Commute Time",
            "description": "Travel time to work/downtown",
            "data_availability": "✅ Calculated",
            "implementation": "Easy",
            "impact": "High",
            "type": "number",
            "unit": "minutes"
        },
        "school_ratings": {
            "name": "School Quality",
            "description": "Elementary, middle, and high school ratings",
            "data_availability": "🔶 GreatSchools API",
            "implementation": "Medium",
            "impact": "High",
            "type": "number",
            "unit": "/10"
        },
        "walkability": {
            "name": "Walk Score",
            "description": "Ability to walk to amenities",
            "data_availability": "✅ Walk Score API",
            "implementation": "Medium",
            "impact": "Medium",
            "type": "number",
            "unit": "/100"
        },
        "crime_rate": {
            "name": "Crime Statistics",
            "description": "Area crime rates and safety",
            "data_availability": "✅ Crime APIs",
            "implementation": "Medium",
            "impact": "High",
            "type": "number",
            "unit": "incidents/1000"
        },
        "neighborhood_quality": {
            "name": "Neighborhood Desirability",
            "description": "Overall neighborhood appeal and reputation",
            "data_availability": "✅ Available",
            "implementation": "Easy",
            "impact": "High",
            "type": "choice",
            "options": ["Excellent", "Very Good", "Good", "Fair", "Poor"]
        },
        "neighborhoods": {
            "name": "Preferred Areas",
            "description": "Specific neighborhoods you prefer",
            "data_availability": "✅ Available",
            "implementation": "Easy",
            "impact": "High",
            "type": "multiselect",
            "options": ["Plymouth", "Minnetonka", "Eden Prairie", "Woodbury", "Maple Grove", 
                       "Edina", "Wayzata", "Bloomington", "Burnsville", "Apple Valley"]
        }
    },
    "🏠 Property Features": {
        "square_footage": {
            "name": "Total Square Footage",
            "description": "Total living space",
            "data_availability": "✅ Available",
            "implementation": "Easy",
            "impact": "High",
            "type": "number",
            "unit": "sqft"
        },
        "bedrooms": {
            "name": "Number of Bedrooms",
            "description": "Total bedroom count",
            "data_availability": "✅ Available",
            "implementation": "Easy",
            "impact": "High",
            "type": "number",
            "unit": ""
        },
        "bathrooms": {
            "name": "Number of Bathrooms",
            "description": "Full and half bathrooms",
            "data_availability": "✅ Available",
            "implementation": "Easy",
            "impact": "High",
            "type": "number",
            "unit": ""
        },
        "garage_spaces": {
            "name": "Garage Spaces",
            "description": "Number of covered parking spots",
            "data_availability": "✅ Available",
            "implementation": "Easy",
            "impact": "Medium",
            "type": "number",
            "unit": "cars"
        },
        "year_built": {
            "name": "Year Built / Age",
            "description": "Age of the house",
            "data_availability": "✅ Available",
            "implementation": "Easy",
            "impact": "Medium",
            "type": "number",
            "unit": ""
        },
        "home_office": {
            "name": "Office Space",
            "description": "Dedicated room for home office",
            "data_availability": "🔶 Listing details",
            "implementation": "Medium",
            "impact": "Medium",
            "type": "boolean",
            "unit": ""
        }
    },
    "🌳 Lot & Outdoor": {
        "lot_size": {
            "name": "Lot Size",
            "description": "Total lot square footage",
            "data_availability": "✅ Available",
            "implementation": "Easy",
            "impact": "Medium",
            "type": "number",
            "unit": "sqft"
        },
        "privacy_level": {
            "name": "Privacy",
            "description": "Distance from neighbors, fencing",
            "data_availability": "🔶 Photos/satellite",
            "implementation": "Medium",
            "impact": "Medium",
            "type": "choice",
            "options": ["Very Private", "Private", "Moderate", "Open"]
        }
    }
}

def parameter_selection_quiz():
    """Basic parameter selection without Streamlit - returns default preferences"""
    
    # This is a simplified version that returns default answers
    # The full Streamlit version is in parameter_workshop.py
    answers = {
        'buyer_type': 'Family with kids',
        'timeline': '5-10 years',
        'work_situation': 'Hybrid work',
        'budget_flexibility': 'Somewhat flexible',
        'down_payment': '20%+',
        'monthly_comfort': 'Moderate',
        'priorities': ['Good schools', 'Low maintenance', 'Privacy', 'Modern updates', 'Large yard'],
        'deal_breakers': []
    }
    
    return answers

def recommend_parameters(answers):
    """Recommend parameters based on quiz answers without Streamlit"""
    
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
            "medium": ["year_built", "days_on_market"],
            "low": []
        },
        "Family with kids": {
            "high": ["school_ratings", "crime_rate", "lot_size"],
            "medium": ["neighborhood_quality", "home_office"],
            "low": ["walkability"]
        },
        "Empty nesters": {
            "high": ["walkability", "neighborhood_quality"],
            "medium": ["crime_rate"],
            "low": ["school_ratings", "lot_size"]
        },
        "Young professional": {
            "high": ["commute_time", "walkability"],
            "medium": ["neighborhood_quality"],
            "low": ["school_ratings", "lot_size"]
        },
        "Remote worker": {
            "high": ["home_office", "square_footage"],
            "medium": ["neighborhood_quality", "privacy_level"],
            "low": ["commute_time"]
        }
    }
    
    # Add buyer-specific parameters
    buyer_params = buyer_type_params.get(answers['buyer_type'], buyer_type_params["Family with kids"])
    for priority in ["high", "medium", "low"]:
        params = buyer_params.get(priority, [])
        target_list = f"{priority}_priority"
        for param in params:
            if param in [p for cat in PARAMETERS.values() for p in cat.keys()]:
                recommendations[target_list].append(param)
    
    # Based on work situation
    if answers['work_situation'] in ["Fixed office location", "Hybrid work"]:
        if "commute_time" not in recommendations["high_priority"]:
            recommendations["high_priority"].append("commute_time")
    elif answers['work_situation'] == "Fully remote":
        if "home_office" not in recommendations["high_priority"]:
            recommendations["high_priority"].append("home_office")
        if "commute_time" in recommendations["high_priority"]:
            recommendations["high_priority"].remove("commute_time")
            recommendations["low_priority"].append("commute_time")
    
    # Based on priorities
    priority_mapping = {
        "Low maintenance": ["year_built"],
        "Good schools": ["school_ratings"],
        "Walkable area": ["walkability"],
        "Privacy": ["lot_size", "privacy_level"],
        "Modern updates": ["year_built"],
        "Large yard": ["lot_size"],
        "Home office": ["home_office", "square_footage"],
        "Investment potential": ["school_ratings", "neighborhood_quality"]
    }
    
    for priority in answers.get('priorities', []):
        if priority in priority_mapping:
            for param in priority_mapping[priority]:
                if param in [p for cat in PARAMETERS.values() for p in cat.keys()]:
                    if param not in recommendations["high_priority"]:
                        recommendations["high_priority"].append(param)
    
    # Remove duplicates and limit counts
    all_params = set()
    for priority_level in ["high_priority", "medium_priority", "low_priority"]:
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

# Default parameter values for common scenarios
DEFAULT_PARAMETER_VALUES = {
    "purchase_price": 350000,
    "price_per_sqft": 200,
    "total_monthly_cost": 2500,
    "property_taxes": 5000,
    "commute_time": 25,
    "school_ratings": 8.0,
    "walkability": 70,
    "crime_rate": 2.0,
    "square_footage": 1800,
    "bedrooms": 3,
    "bathrooms": 2.5,
    "garage_spaces": 2,
    "year_built": 2010,
    "lot_size": 8000,
    "home_office": True,
    "neighborhood_quality": "Very Good",
    "privacy_level": "Private"
}