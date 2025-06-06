# seamless_integrated_profiler_fixed.py
# Complete workflow: Quiz → Parameter Analysis → AI Profile Generation
# Fixed version that doesn't require external parameter_definitions.py

import streamlit as st

# MUST BE FIRST STREAMLIT COMMAND
st.set_page_config(
    page_title="AI House Profile Generator",
    page_icon="🏡",
    layout="wide"
)

import pandas as pd
import json
import requests
import os
from typing import Dict, List
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Groq API configuration
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama3-70b-8192"

# Embedded parameter definitions (no external imports needed)
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

# Default parameter values
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

class ParameterAnalyzer:
    """Analyzes quiz responses and generates weighted parameters"""
    
    def __init__(self):
        self.parameters = PARAMETERS
        self.default_values = DEFAULT_PARAMETER_VALUES
    
    def recommend_parameters_from_answers(self, answers: Dict) -> Dict:
        """Generate parameter recommendations based on quiz answers"""
        
        recommendations = {
            "high_priority": [],
            "medium_priority": [],
            "low_priority": []
        }
        
        # Core parameters everyone needs
        core_params = ["purchase_price", "square_footage", "bedrooms", "bathrooms"]
        recommendations["high_priority"].extend(core_params)
        
        # Based on buyer type
        buyer_type_mapping = {
            "First-time buyer": {
                "high": ["price_per_sqft", "total_monthly_cost", "property_taxes"],
                "medium": ["year_built", "neighborhood_quality"],
                "low": ["walkability"]
            },
            "Family with kids": {
                "high": ["school_ratings", "crime_rate", "lot_size", "garage_spaces"],
                "medium": ["neighborhood_quality", "privacy_level"],
                "low": ["walkability"]
            },
            "Empty nesters": {
                "high": ["walkability", "neighborhood_quality", "crime_rate"],
                "medium": ["commute_time"],
                "low": ["school_ratings", "lot_size"]
            },
            "Young professional": {
                "high": ["commute_time", "walkability", "neighborhood_quality"],
                "medium": ["price_per_sqft"],
                "low": ["school_ratings", "lot_size"]
            },
            "Remote worker": {
                "high": ["home_office", "square_footage", "privacy_level"],
                "medium": ["neighborhood_quality"],
                "low": ["commute_time"]
            },
            "Investor": {
                "high": ["price_per_sqft", "neighborhood_quality", "school_ratings"],
                "medium": ["crime_rate", "property_taxes"],
                "low": ["home_office"]
            }
        }
        
        buyer_type = answers.get('buyer_type', 'Family with kids')
        buyer_recommendations = buyer_type_mapping.get(buyer_type, buyer_type_mapping['Family with kids'])
        
        for priority_level, params in buyer_recommendations.items():
            target_list = f"{priority_level}_priority"
            for param in params:
                if param in [p for cat in PARAMETERS.values() for p in cat.keys()]:
                    if param not in recommendations[target_list]:
                        recommendations[target_list].append(param)
        
        # Based on work situation
        work_situation = answers.get('work_situation', 'Hybrid work')
        if work_situation in ["Fixed office location", "Hybrid work"]:
            if "commute_time" not in recommendations["high_priority"]:
                recommendations["high_priority"].append("commute_time")
        elif work_situation == "Fully remote":
            if "home_office" not in recommendations["high_priority"]:
                recommendations["high_priority"].append("home_office")
            if "commute_time" in recommendations["high_priority"]:
                recommendations["high_priority"].remove("commute_time")
                if "commute_time" not in recommendations["low_priority"]:
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
            "Storage space": ["square_footage"],
            "Investment potential": ["school_ratings", "neighborhood_quality"],
            "Energy efficiency": ["year_built"]
        }
        
        for priority in answers.get('priorities', []):
            if priority in priority_mapping:
                for param in priority_mapping[priority]:
                    if param in [p for cat in PARAMETERS.values() for p in cat.keys()]:
                        if param not in recommendations["high_priority"]:
                            recommendations["high_priority"].append(param)
        
        # Budget flexibility adjustments
        budget_flexibility = answers.get('budget_flexibility', 'Moderate')
        if budget_flexibility == "Very tight":
            for param in ["total_monthly_cost", "property_taxes"]:
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
    
    def analyze_quiz_responses(self, answers: Dict) -> tuple:
        """Convert quiz answers into weighted parameters and selected values"""
        
        selected_params = {}
        param_weights = {}
        
        # Get base recommendations
        recommendations = self.recommend_parameters_from_answers(answers)
        
        # Assign weights based on priority levels
        high_weight = 0.6 / max(len(recommendations["high_priority"]), 1)
        medium_weight = 0.3 / max(len(recommendations["medium_priority"]), 1)
        low_weight = 0.1 / max(len(recommendations["low_priority"]), 1)
        
        # Process high priority parameters
        for param in recommendations["high_priority"]:
            param_weights[param] = high_weight
            selected_params[param] = self._get_parameter_value_from_answers(param, answers, "high")
        
        # Process medium priority parameters  
        for param in recommendations["medium_priority"]:
            param_weights[param] = medium_weight
            selected_params[param] = self._get_parameter_value_from_answers(param, answers, "medium")
        
        # Process low priority parameters
        for param in recommendations["low_priority"]:
            param_weights[param] = low_weight
            selected_params[param] = self._get_parameter_value_from_answers(param, answers, "low")
        
        return selected_params, param_weights, recommendations
    
    def _get_parameter_value_from_answers(self, param: str, answers: Dict, priority: str) -> any:
        """Convert quiz answers into specific parameter values"""
        
        # Get parameter info
        param_info = None
        for category, params in PARAMETERS.items():
            if param in params:
                param_info = params[param]
                break
        
        if not param_info:
            return self.default_values.get(param, "Unknown")
        
        # Budget-related parameters
        if param == "purchase_price":
            budget_flexibility = answers.get('budget_flexibility', 'Moderate')
            if budget_flexibility == "Very tight":
                return 300000
            elif budget_flexibility == "Very flexible":
                return 500000
            else:
                return 400000
        
        # Work-related parameters
        if param == "commute_time":
            work_situation = answers.get('work_situation', 'Hybrid work')
            if work_situation == "Fully remote":
                return 60  # Not important for remote workers
            elif work_situation == "Fixed office location":
                return 25  # Very important
            else:
                return 30  # Moderate importance
        
        if param == "home_office":
            work_situation = answers.get('work_situation', 'Hybrid work')
            return work_situation in ["Fully remote", "Hybrid work"]
        
        # Family-related parameters  
        if param == "school_ratings":
            buyer_type = answers.get('buyer_type', 'Family with kids')
            priorities = answers.get('priorities', [])
            if buyer_type == "Family with kids" or "Good schools" in priorities:
                return 8.5
            elif buyer_type == "Empty nesters":
                return 6.0  # Less important but still affects resale
            else:
                return 7.0
        
        if param == "bedrooms":
            buyer_type = answers.get('buyer_type', 'Family with kids')
            if buyer_type == "Family with kids":
                return 4
            elif buyer_type == "Empty nesters":
                return 2
            else:
                return 3
        
        # Lifestyle-related parameters
        if param == "lot_size":
            priorities = answers.get('priorities', [])
            if "Large yard" in priorities:
                return 10000
            elif "Privacy" in priorities:
                return 8000
            else:
                return 7000
        
        if param == "walkability":
            priorities = answers.get('priorities', [])
            if "Walkable area" in priorities:
                return 80
            else:
                return 60
        
        # Default to standard values
        return self.default_values.get(param, "Standard")

class HouseProfileGenerator:
    """Generate AI house profiles using Groq"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def generate_profile(self, selected_params: Dict, param_weights: Dict, user_context: Dict) -> Dict:
        """Generate comprehensive house profile using AI"""
        
        prompt = self._create_detailed_prompt(selected_params, param_weights, user_context)
        
        data = {
            "model": GROQ_MODEL,
            "messages": [
                {
                    "role": "system", 
                    "content": "You are an expert real estate advisor who creates detailed, scientific house hunting strategies. Provide specific, actionable advice based on data-driven parameter analysis."
                },
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 3500
        }
        
        try:
            response = requests.post(
                GROQ_API_URL,
                headers=self.headers,
                json=data,
                timeout=45
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                return {"success": True, "profile": content}
            else:
                return {"success": False, "error": f"API error: {response.status_code}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _create_detailed_prompt(self, selected_params: Dict, param_weights: Dict, user_context: Dict) -> str:
        """Create comprehensive prompt for AI profile generation"""
        
        # Sort parameters by weight for prioritization
        sorted_params = sorted(param_weights.items(), key=lambda x: x[1], reverse=True)
        
        prompt = f"""Create a comprehensive house hunting profile based on this scientific parameter analysis:

BUYER PROFILE:
- Type: {user_context.get('buyer_type', 'Not specified')}
- Timeline: {user_context.get('timeline', 'Not specified')}
- Work: {user_context.get('work_situation', 'Not specified')}
- Budget Flexibility: {user_context.get('budget_flexibility', 'Not specified')}
- Priorities: {', '.join(user_context.get('priorities', []))}

TOP WEIGHTED PARAMETERS:
"""
        
        # Show top 10 parameters with weights and values
        for param_key, weight in sorted_params[:10]:
            param_value = selected_params.get(param_key, 'Not specified')
            param_info = self._find_param_info(param_key)
            param_name = param_info['name'] if param_info else param_key
            prompt += f"- {param_name}: {param_value} (Weight: {weight:.1%})\n"
        
        prompt += f"""
ALL SELECTED PARAMETERS:
{json.dumps(selected_params, indent=2)}

Create a detailed house hunting profile with these sections:

1. EXECUTIVE SUMMARY (2-3 sentences)
   - Your ideal house in a nutshell based on highest-weighted parameters

2. ZILLOW SEARCH STRATEGY
   - Exact search filters (price range, beds, baths, sqft, year built)
   - Geographic areas to focus on
   - Keywords to use in search
   - Specific MLS filters to apply

3. IDEAL HOUSE DESCRIPTION (2 paragraphs)
   - Specific architectural style and features
   - Layout and room requirements
   - Lot and neighborhood characteristics
   - Why this matches your weighted parameters

4. MUST-HAVE FEATURES (Top 8, ranked by parameter weights)
   - Non-negotiable requirements with specific criteria
   - Include measurable thresholds (e.g., "school rating 8.5+/10")

5. HIGHLY PREFERRED FEATURES (Next 6 most important)
   - Strong preferences that significantly increase appeal
   - Features you'd prioritize in competitive situations

6. NICE-TO-HAVE FEATURES (Bonus items)
   - Features that would break ties between similar houses
   - Luxury or convenience items

7. RED FLAGS & DEALBREAKERS
   - Specific things to avoid based on your parameters
   - Warning signs during house tours
   - Market conditions that conflict with your goals

8. SCORING FRAMEWORK
   - Point system for evaluating houses (100-point scale)
   - Weight each category based on your parameter priorities
   - Decision matrix for comparing multiple houses

9. NEGOTIATION STRATEGY
   - What to emphasize based on your priorities
   - Market leverage points
   - Inspection focus areas

10. RECOMMENDED SEARCH AREAS & TIMING
    - Specific Minneapolis neighborhoods that match criteria
    - Best times to search based on market conditions
    - Areas to monitor for future opportunities

Make every recommendation specific and actionable. Reference the parameter weights to justify priorities."""
        
        return prompt
    
    def _find_param_info(self, param_key: str) -> Dict:
        """Find parameter info from PARAMETERS structure"""
        for category, params in PARAMETERS.items():
            if param_key in params:
                return params[param_key]
        return {"name": param_key}

def create_comprehensive_quiz():
    """Create the complete assessment quiz with immediate processing"""
    
    st.header("🎯 Personal House Hunting Assessment")
    st.markdown("*Answer these questions to get your scientifically-generated house hunting profile*")
    
    # Initialize or get existing answers
    if 'quiz_answers' not in st.session_state:
        st.session_state.quiz_answers = {}
    
    answers = st.session_state.quiz_answers
    
    # Section 1: Basic Profile
    with st.expander("👤 Your Profile", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            buyer_type = st.selectbox(
                "I am a...",
                ["First-time buyer", "Family with kids", "Empty nesters", 
                 "Young professional", "Remote worker", "Investor", "Other"],
                index=0,
                key="buyer_type"
            )
            
            timeline = st.selectbox(
                "Planning to buy within...",
                ["ASAP", "1-3 months", "3-6 months", "6-12 months", "Just exploring"],
                index=1,
                key="timeline"
            )
        
        with col2:
            work_situation = st.selectbox(
                "Work situation",
                ["Fixed office location", "Hybrid work", "Fully remote", 
                 "Multiple locations", "Retired", "Self-employed"],
                index=1,
                key="work_situation"
            )
            
            budget_flexibility = st.selectbox(
                "Budget flexibility",
                ["Very tight", "Somewhat flexible", "Pretty flexible", "Very flexible"],
                index=1,
                key="budget_flexibility"
            )
    
    # Section 2: Lifestyle Priorities
    with st.expander("🎯 Lifestyle Priorities", expanded=True):
        st.markdown("**Select your top 5-8 priorities:**")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**Living Style**")
            p1 = st.checkbox("Low maintenance", key="p1")
            p2 = st.checkbox("Good schools", key="p2")
            p3 = st.checkbox("Walkable area", key="p3")
            p4 = st.checkbox("Privacy", key="p4")
            p5 = st.checkbox("Modern updates", key="p5")
        
        with col2:
            st.markdown("**Space Needs**")
            p6 = st.checkbox("Large yard", key="p6")
            p7 = st.checkbox("Home office", key="p7")
            p8 = st.checkbox("Storage space", key="p8")
            p9 = st.checkbox("Entertainment space", key="p9")
            p10 = st.checkbox("Workshop/hobby space", key="p10")
        
        with col3:
            st.markdown("**Investment & Value**")
            p11 = st.checkbox("Investment potential", key="p11")
            p12 = st.checkbox("Energy efficiency", key="p12")
            p13 = st.checkbox("Move-in ready", key="p13")
            p14 = st.checkbox("Future expansion potential", key="p14")
            p15 = st.checkbox("Unique features", key="p15")
        
        # Collect selected priorities
        priority_map = {
            "p1": "Low maintenance", "p2": "Good schools", "p3": "Walkable area", 
            "p4": "Privacy", "p5": "Modern updates", "p6": "Large yard",
            "p7": "Home office", "p8": "Storage space", "p9": "Entertainment space",
            "p10": "Workshop/hobby space", "p11": "Investment potential", 
            "p12": "Energy efficiency", "p13": "Move-in ready", 
            "p14": "Future expansion potential", "p15": "Unique features"
        }
        
        selected_priorities = [priority_map[key] for key, priority in priority_map.items() 
                             if st.session_state.get(key, False)]
    
    # Section 3: Deal Breakers
    with st.expander("🚫 Deal Breakers", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Must NOT have:**")
            db1 = st.checkbox("HOA restrictions", key="db1")
            db2 = st.checkbox("Busy street", key="db2")
            db3 = st.checkbox("Bad schools", key="db3")
            db4 = st.checkbox("Long commute (>45min)", key="db4")
            db5 = st.checkbox("Major repairs needed", key="db5")
        
        with col2:
            st.markdown("**Must have:**")
            db6 = st.checkbox("Garage required", key="db6")
            db7 = st.checkbox("Yard required", key="db7")
            db8 = st.checkbox("2+ bathrooms", key="db8")
            db9 = st.checkbox("Updated kitchen", key="db9")
            db10 = st.checkbox("Single level only", key="db10")
        
        deal_breaker_map = {
            "db1": "HOA restrictions", "db2": "Busy street", "db3": "Bad schools",
            "db4": "Long commute", "db5": "Major repairs", "db6": "No garage",
            "db7": "No yard", "db8": "Less than 2 bathrooms", 
            "db9": "Outdated kitchen", "db10": "Multi-level"
        }
        
        deal_breakers = [deal_breaker_map[key] for key, breaker in deal_breaker_map.items() 
                        if st.session_state.get(key, False)]
    
    # Compile all answers
    answers.update({
        'buyer_type': buyer_type,
        'timeline': timeline,
        'work_situation': work_situation,
        'budget_flexibility': budget_flexibility,
        'priorities': selected_priorities,
        'deal_breakers': deal_breakers
    })
    
    # Update session state
    st.session_state.quiz_answers = answers
    
    # Show summary of selections
    st.markdown("### 📋 Your Assessment Summary")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Buyer Type", buyer_type)
        st.metric("Timeline", timeline)
    
    with col2:
        st.metric("Work Style", work_situation)
        st.metric("Budget Style", budget_flexibility)
    
    with col3:
        st.metric("Priorities Selected", len(selected_priorities))
        st.metric("Deal Breakers", len(deal_breakers))
    
    # Validation and next step
    if len(selected_priorities) < 3:
        st.warning("⚠️ Please select at least 3 priorities to get meaningful results")
        return None
    
    if len(selected_priorities) > 10:
        st.warning("⚠️ Please limit yourself to 8-10 priorities for focused results")
        return None
    
    st.success(f"✅ Assessment complete! You selected {len(selected_priorities)} priorities and {len(deal_breakers)} deal breakers.")
    
    return answers

def display_parameter_analysis(selected_params: Dict, param_weights: Dict, recommendations: Dict):
    """Display the parameter analysis results"""
    
    st.header("📊 Your Scientific Parameter Analysis")
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Parameters", len(param_weights))
    with col2:
        high_priority_count = len(recommendations["high_priority"])
        st.metric("High Priority", high_priority_count)
    with col3:
        medium_priority_count = len(recommendations["medium_priority"])
        st.metric("Medium Priority", medium_priority_count)
    with col4:
        low_priority_count = len(recommendations["low_priority"])
        st.metric("Low Priority", low_priority_count)
    
    # Top parameters breakdown
    st.subheader("🎯 Your Top Priorities (Highest Weighted)")
    
    # Sort by weight
    sorted_params = sorted(param_weights.items(), key=lambda x: x[1], reverse=True)
    
    for i, (param_key, weight) in enumerate(sorted_params[:10]):
        param_value = selected_params.get(param_key, 'Not specified')
        
        # Find parameter info
        param_info = None
        category_name = "Other"
        for category, params in PARAMETERS.items():
            if param_key in params:
                param_info = params[param_key]
                category_name = category
                break
        
        param_name = param_info['name'] if param_info else param_key
        param_desc = param_info['description'] if param_info else "No description"
        
        with st.expander(f"#{i+1} - {param_name} ({category_name}) - Weight: {weight:.1%}"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write(f"**Description:** {param_desc}")
                st.write(f"**Your Value:** {param_value}")
                st.write(f"**Category:** {category_name}")
            
            with col2:
                st.metric("Priority Weight", f"{weight:.1%}")
                
                # Visual weight bar
                weight_percent = int(weight * 1000)  # Scale for visibility
                st.progress(min(weight_percent, 100))

def main():
    """Main application with seamless workflow"""
    
    st.title("🏡 AI-Powered House Profile Generator")
    st.markdown("*Complete workflow: Assessment → Analysis → AI Profile*")
    
    # Check for API key
    api_key = os.getenv('GROQ_API_KEY') or os.getenv('RAPIDAPI_KEY')
    
    if not api_key:
        with st.sidebar:
            api_key = st.text_input(
                "Groq API Key",
                type="password",
                help="Get your free API key at console.groq.com"
            )
        
        if not api_key:
            st.warning("👈 Please enter your Groq API key in the sidebar")
            st.info("""
            **How to get a free Groq API key:**
            1. Go to [console.groq.com](https://console.groq.com)
            2. Sign up for a free account
            3. Create an API key
            4. Paste it in the sidebar
            """)
    else:
        st.sidebar.success("✅ API key loaded")
    
    # Step 1: Assessment Quiz
    st.markdown("## Step 1: Personal Assessment")
    answers = create_comprehensive_quiz()
    
    if not answers:
        st.info("👆 Complete the assessment above to continue")
        return
    
    # Step 2: Generate Analysis Button
    st.markdown("## Step 2: Scientific Analysis")
    
    if st.button("🧠 Generate Parameter Analysis", type="primary", help="Analyze your responses scientifically"):
        with st.spinner("Analyzing your responses and generating parameter weights..."):
            
            # Initialize analyzer and process quiz
            analyzer = ParameterAnalyzer()
            selected_params, param_weights, recommendations = analyzer.analyze_quiz_responses(answers)
            
            # Store in session state
            st.session_state.selected_params = selected_params
            st.session_state.param_weights = param_weights
            st.session_state.recommendations = recommendations
            st.session_state.analysis_complete = True
            
        st.success("✅ Parameter analysis complete!")
        st.rerun()  # Refresh to show results
    
    # Step 3: Show Analysis Results
    if st.session_state.get('analysis_complete', False):
        display_parameter_analysis(
            st.session_state.selected_params,
            st.session_state.param_weights,
            st.session_state.recommendations
        )
        
        # Step 4: Generate AI Profile
        st.markdown("## Step 3: AI Profile Generation")
        
        if st.button("🎨 Generate My House Hunting Profile", type="primary"):
            if not api_key:
                st.error("❌ Please enter your Groq API key in the sidebar first!")
                return
                
            with st.spinner("Creating your personalized house hunting profile with AI..."):
                
                generator = HouseProfileGenerator(api_key)
                result = generator.generate_profile(
                    st.session_state.selected_params,
                    st.session_state.param_weights,
                    answers
                )
                
                if result['success']:
                    st.session_state.generated_profile = result['profile']
                    st.success("✅ Profile generated successfully!")
                else:
                    st.error(f"Error generating profile: {result['error']}")
        
        # Step 5: Display Generated Profile
        if st.session_state.get('generated_profile'):
            st.markdown("## 🎯 Your Personalized House Hunting Profile")
            
            # Display the profile
            st.markdown(st.session_state.generated_profile)
            
            # Download options
            st.markdown("### 💾 Save Your Profile")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"house_profile_{timestamp}.txt"
                st.download_button(
                    "📄 Download Profile",
                    st.session_state.generated_profile,
                    file_name=filename,
                    mime="text/plain"
                )
            
            with col2:
                config = {
                    "quiz_answers": answers,
                    "selected_params": st.session_state.selected_params,
                    "param_weights": st.session_state.param_weights,
                    "generated_date": timestamp
                }
                config_json = json.dumps(config, indent=2)
                st.download_button(
                    "⚙️ Save Configuration",
                    config_json,
                    file_name=f"house_config_{timestamp}.json",
                    mime="application/json"
                )
            
            with col3:
                # Create Zillow search URL
                max_price = st.session_state.selected_params.get('purchase_price', 400000)
                min_beds = st.session_state.selected_params.get('bedrooms', 3)
                min_sqft = st.session_state.selected_params.get('square_footage', 1500)
                
                # Create simple Zillow search URL
                zillow_params = []
                if max_price:
                    zillow_params.append(f"price_max={int(max_price)}")
                if min_beds:
                    zillow_params.append(f"beds_min={int(min_beds)}")
                if min_sqft:
                    zillow_params.append(f"sqft_min={int(min_sqft)}")
                
                zillow_url = f"https://www.zillow.com/minneapolis-mn/?" + "&".join(zillow_params)
                
                st.link_button(
                    "🏠 Search Zillow Now",
                    zillow_url,
                    help="Open Zillow with your personalized filters"
                )
    
    # Sidebar with workflow status
    with st.sidebar:
        st.header("🔄 Workflow Status")
        
        # Step indicators
        if answers:
            st.success("✅ Step 1: Assessment Complete")
        else:
            st.info("📝 Step 1: Complete Assessment")
        
        if st.session_state.get('analysis_complete', False):
            st.success("✅ Step 2: Analysis Complete")
        else:
            st.info("🧠 Step 2: Generate Analysis")
        
        if st.session_state.get('generated_profile'):
            st.success("✅ Step 3: Profile Complete")
        else:
            st.info("🎨 Step 3: Generate Profile")
        
        # Quick stats if analysis is done
        if st.session_state.get('param_weights'):
            st.markdown("### 📊 Quick Stats")
            total_params = len(st.session_state.param_weights)
            high_priority = len(st.session_state.recommendations["high_priority"])
            
            st.metric("Parameters", total_params)
            st.metric("High Priority", high_priority)
            
            # Top 3 parameters
            sorted_params = sorted(st.session_state.param_weights.items(), 
                                 key=lambda x: x[1], reverse=True)
            
            st.markdown("**Top 3 Priorities:**")
            for i, (param_key, weight) in enumerate(sorted_params[:3]):
                param_info = None
                for category, params in PARAMETERS.items():
                    if param_key in params:
                        param_info = params[param_key]
                        break
                param_name = param_info['name'] if param_info else param_key
                st.caption(f"{i+1}. {param_name} ({weight:.1%})")

if __name__ == "__main__":
    main()