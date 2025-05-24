# integrated_house_profiler.py
# Updated to use parameters from parameter_workshop_fixed.py

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

# Import the parameter structure from parameter definitions (no Streamlit)
from parameter_definitions import PARAMETERS, parameter_selection_quiz, recommend_parameters, DEFAULT_PARAMETER_VALUES

# Load environment variables
load_dotenv()

# Groq API configuration
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama3-70b-8192"

class HouseProfileGenerator:
    """Generate ideal house profiles based on selected parameters from parameter workshop"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def create_profile_prompt(self, selected_params: Dict, user_context: Dict, param_weights: Dict) -> str:
        """Create a prompt for generating house profile using workshop parameters"""
        
        prompt = f"""Based on the following home buyer preferences and scientific parameter analysis, create a detailed house profile for real estate searching.

BUYER CONTEXT:
- Buyer Type: {user_context.get('buyer_type', 'Not specified')}
- Timeline: {user_context.get('timeline', 'Not specified')}
- Work Situation: {user_context.get('work_situation', 'Not specified')}
- Budget Flexibility: {user_context.get('budget_flexibility', 'Not specified')}

PRIORITIZED PARAMETERS (by importance weight):
"""
        
        # Sort parameters by weight (highest first)
        sorted_params = sorted(param_weights.items(), key=lambda x: x[1], reverse=True)
        
        for param_key, weight in sorted_params[:15]:  # Top 15 parameters
            param_info = self._find_param_info(param_key)
            if param_info and param_key in selected_params:
                param_value = selected_params[param_key]
                prompt += f"- {param_info['name']} (Weight: {weight:.1%}): {param_value}\n"
        
        prompt += f"""
SELECTED REQUIREMENTS BY CATEGORY:
"""
        
        # Organize by category for clarity
        for category, params in PARAMETERS.items():
            category_params = {k: v for k, v in selected_params.items() if k in params}
            if category_params:
                prompt += f"\n{category}:\n"
                for param_key, param_value in category_params.items():
                    param_info = params[param_key]
                    weight = param_weights.get(param_key, 0)
                    if weight > 0:
                        prompt += f"  - {param_info['name']}: {param_value} (Priority: {weight:.1%})\n"
        
        prompt += """

Please provide a comprehensive house hunting profile with:

1. ZILLOW SEARCH STRATEGY
   - Specific search terms and filters to use
   - Price range, size, year built, and feature filters
   - Geographic areas to focus on

2. IDEAL HOUSE DESCRIPTION (2-3 paragraphs)
   - Specific features and characteristics to look for
   - Layout preferences and must-have elements
   - Neighborhood and location requirements

3. MUST-HAVE FEATURES (Ranked by Priority)
   - Non-negotiable requirements based on highest-weighted parameters
   - Specific measurable criteria (e.g., "3+ car garage" not just "garage")

4. HIGHLY PREFERRED FEATURES
   - Features that would significantly increase desirability
   - Secondary requirements that add value

5. NICE-TO-HAVE FEATURES  
   - Bonus features that would be appreciated
   - Features that could break ties between similar properties

6. RED FLAGS TO AVOID
   - Specific dealbreakers based on your parameters
   - Common issues to watch for that conflict with your priorities

7. SCORING WEIGHTS FOR HOUSE EVALUATION
   - How to weight different factors when comparing houses
   - Suggested point system for ranking properties

8. NEGOTIATION STRATEGY
   - What to emphasize based on your priorities
   - Market conditions to leverage
   - Inspection focus areas

9. RECOMMENDED SEARCH AREAS
   - Specific neighborhoods that match your criteria
   - Areas to avoid and why
   - Up-and-coming areas to consider

10. LONG-TERM CONSIDERATIONS
    - How this house fits your timeline and goals
    - Resale factors based on your priorities
    - Future needs to anticipate

Format as a professional, actionable house hunting guide."""
        
        return prompt
    
    def _find_param_info(self, param_key: str) -> Dict:
        """Find parameter info from the PARAMETERS structure"""
        for category, params in PARAMETERS.items():
            if param_key in params:
                return params[param_key]
        return None
    
    def generate_profile(self, selected_params: Dict, user_context: Dict, param_weights: Dict) -> Dict:
        """Generate house profile using Groq"""
        
        prompt = self.create_profile_prompt(selected_params, user_context, param_weights)
        
        data = {
            "model": GROQ_MODEL,
            "messages": [
                {
                    "role": "system", 
                    "content": "You are an expert real estate advisor who creates detailed, scientific house hunting strategies. Your recommendations are based on data-driven parameter analysis and real market knowledge."
                },
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 3000
        }
        
        try:
            response = requests.post(
                GROQ_API_URL,
                headers=self.headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                return {"success": True, "profile": content}
            else:
                return {"success": False, "error": f"API error: {response.status_code}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def generate_zillow_filters(self, selected_params: Dict, param_weights: Dict) -> Dict:
        """Generate specific Zillow search filters from parameters"""
        
        filters = {}
        
        # Budget filters
        if 'min_price' in selected_params:
            filters['min_price'] = selected_params['min_price']
        if 'max_price' in selected_params:
            filters['max_price'] = selected_params['max_price']
        
        # Size filters
        if 'bedrooms' in selected_params:
            filters['min_beds'] = selected_params['bedrooms']
        if 'bathrooms' in selected_params:
            filters['min_baths'] = selected_params['bathrooms']
        if 'min_sqft' in selected_params:
            filters['min_sqft'] = selected_params['min_sqft']
        if 'max_sqft' in selected_params:
            filters['max_sqft'] = selected_params['max_sqft']
        
        # Age filters
        if 'year_built_min' in selected_params:
            filters['min_year'] = selected_params['year_built_min']
        
        # Location filters
        if 'neighborhoods' in selected_params:
            filters['neighborhoods'] = selected_params['neighborhoods']
        
        # Feature filters
        feature_filters = []
        if selected_params.get('garage_spaces', 0) > 0:
            feature_filters.append(f"{selected_params['garage_spaces']}+ car garage")
        if selected_params.get('pool'):
            feature_filters.append("pool")
        if selected_params.get('fireplace'):
            feature_filters.append("fireplace")
        if selected_params.get('hardwood_floors'):
            feature_filters.append("hardwood floors")
        
        if feature_filters:
            filters['keywords'] = " ".join(feature_filters)
        
        return filters

def create_integrated_parameter_form():
    """Create parameter form using the workshop structure"""
    
    st.header("🎯 Define Your Dream Home Profile")
    
    # Use the parameter workshop quiz
    answers = parameter_selection_quiz()
    
    # Get recommendations based on answers
    if st.button("🧠 Analyze My Preferences", type="primary"):
        if len(answers.get('priorities', [])) < 3:
            st.error("Please select at least 3 lifestyle priorities!")
            return None, None, None
        else:
            recommendations = recommend_parameters(answers)
            
            # Convert recommendations to selected parameters format
            selected_params = {}
            param_weights = {}
            
            # Assign weights based on priority level
            high_weight = 0.6 / max(len(recommendations["high_priority"]), 1)
            medium_weight = 0.3 / max(len(recommendations["medium_priority"]), 1)
            low_weight = 0.1 / max(len(recommendations["low_priority"]), 1)
            
            # Add high priority parameters
            for param in recommendations["high_priority"]:
                param_info = None
                for category, params in PARAMETERS.items():
                    if param in params:
                        param_info = params[param]
                        break
                
                if param_info:
                    # Set default values based on parameter type
                    if param_info['type'] == 'number':
                        if 'price' in param:
                            selected_params[param] = 400000 if 'max' in param else 300000
                        elif 'sqft' in param:
                            selected_params[param] = 1500
                        elif 'bedrooms' in param:
                            selected_params[param] = 3
                        elif 'year' in param:
                            selected_params[param] = 2000
                        else:
                            selected_params[param] = 1
                    elif param_info['type'] == 'boolean':
                        selected_params[param] = True
                    else:
                        selected_params[param] = "preferred"
                    
                    param_weights[param] = high_weight
            
            # Add medium and low priority parameters with lower weights
            for param in recommendations["medium_priority"]:
                if param not in param_weights:  # Avoid duplicates
                    param_weights[param] = medium_weight
                    selected_params[param] = "moderate_preference"
            
            for param in recommendations["low_priority"]:
                if param not in param_weights:  # Avoid duplicates
                    param_weights[param] = low_weight
                    selected_params[param] = "nice_to_have"
            
            st.session_state.selected_params = selected_params
            st.session_state.param_weights = param_weights
            st.session_state.user_context = answers
            st.success("✅ Analysis complete! Your personalized profile is ready.")
            
            return selected_params, param_weights, answers
    
    return None, None, None

def display_house_profile(profile_text: str, selected_params: Dict, param_weights: Dict):
    """Display the generated house profile with enhanced features"""
    
    st.header("🏡 Your Personalized House Hunting Profile")
    
    # Quick summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Parameters Analyzed", len(param_weights))
    with col2:
        high_priority_count = len([w for w in param_weights.values() if w > 0.05])
        st.metric("High Priority Items", high_priority_count)
    with col3:
        if 'max_price' in selected_params:
            st.metric("Max Budget", f"${selected_params['max_price']:,}")
        else:
            st.metric("Budget", "Custom")
    with col4:
        if 'neighborhoods' in selected_params:
            st.metric("Target Areas", len(selected_params['neighborhoods']))
        else:
            st.metric("Areas", "All")
    
    # Display the profile
    st.markdown("### 📋 Your Complete House Hunting Guide")
    st.markdown(profile_text)
    
    # Generate Zillow filters
    generator = HouseProfileGenerator("")  # Don't need API key for this
    zillow_filters = generator.generate_zillow_filters(selected_params, param_weights)
    
    if zillow_filters:
        st.markdown("### 🔍 Ready-to-Use Zillow Search Filters")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.json(zillow_filters)
        
        with col2:
            # Create direct Zillow search URL
            url_parts = []
            if 'min_price' in zillow_filters:
                url_parts.append(f"price_min={zillow_filters['min_price']}")
            if 'max_price' in zillow_filters:
                url_parts.append(f"price_max={zillow_filters['max_price']}")
            if 'min_beds' in zillow_filters:
                url_parts.append(f"beds_min={zillow_filters['min_beds']}")
            if 'min_baths' in zillow_filters:
                url_parts.append(f"baths_min={zillow_filters['min_baths']}")
            
            if url_parts:
                zillow_url = f"https://www.zillow.com/minneapolis-mn/?" + "&".join(url_parts)
                st.markdown(f"[🏠 Search Zillow Now]({zillow_url})")
    
    # Action buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📋 Copy Profile"):
            st.code(profile_text, language=None)
    
    with col2:
        # Save profile
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"house_profile_{timestamp}.txt"
        st.download_button(
            "💾 Download Profile",
            profile_text,
            file_name=filename,
            mime="text/plain"
        )
    
    with col3:
        # Save parameters
        config = {
            "selected_params": selected_params,
            "param_weights": param_weights,
            "user_context": st.session_state.get('user_context', {}),
            "generated_date": timestamp
        }
        param_json = json.dumps(config, indent=2)
        st.download_button(
            "⚙️ Save Configuration",
            param_json,
            file_name=f"house_config_{timestamp}.json",
            mime="application/json"
        )

def main():
    """Main application"""
    
    st.title("🏡 AI-Powered House Profile Generator")
    st.markdown("*Scientific parameter analysis meets personalized house hunting*")
    
    # Load API key
    api_key = os.getenv('GROQ_API_KEY') or os.getenv('RAPIDAPI_KEY')
    
    if not api_key:
        with st.sidebar:
            api_key = st.text_input(
                "Groq API Key",
                type="password",
                help="Get your free API key at console.groq.com"
            )
        
        if not api_key:
            st.warning("👈 Please enter your Groq API key in the sidebar to generate profiles")
            st.info("""
            **How to get a free Groq API key:**
            1. Go to [console.groq.com](https://console.groq.com)
            2. Sign up for a free account
            3. Create an API key
            4. Paste it in the sidebar
            """)
    else:
        st.sidebar.success("✅ API key loaded")
    
    # Main interface
    tab1, tab2, tab3 = st.tabs(["🎯 Create Profile", "📊 Parameter Analysis", "💾 Saved Profiles"])
    
    with tab1:
        # Parameter selection using workshop
        selected_params, param_weights, user_context = create_integrated_parameter_form()
        
        # Generate profile if we have parameters
        if (hasattr(st.session_state, 'selected_params') and 
            hasattr(st.session_state, 'param_weights') and
            api_key):
            
            if st.button("🎨 Generate My House Profile", type="primary"):
                with st.spinner("Creating your personalized house profile..."):
                    generator = HouseProfileGenerator(api_key)
                    result = generator.generate_profile(
                        st.session_state.selected_params,
                        st.session_state.user_context,
                        st.session_state.param_weights
                    )
                    
                    if result['success']:
                        st.session_state.generated_profile = result['profile']
                        st.success("✅ Profile generated successfully!")
                    else:
                        st.error(f"Error generating profile: {result['error']}")
    
    with tab2:
        if hasattr(st.session_state, 'param_weights'):
            st.header("📊 Your Parameter Analysis")
            
            # Create visualization of parameter weights
            weight_df = pd.DataFrame([
                {"Parameter": param, "Weight": weight, "Category": "High" if weight > 0.05 else "Medium" if weight > 0.02 else "Low"}
                for param, weight in st.session_state.param_weights.items()
            ]).sort_values('Weight', ascending=False)
            
            # Show top parameters
            st.subheader("🎯 Your Top Priorities")
            for _, row in weight_df.head(10).iterrows():
                col1, col2 = st.columns([3, 1])
                with col1:
                    param_info = None
                    for category, params in PARAMETERS.items():
                        if row['Parameter'] in params:
                            param_info = params[row['Parameter']]
                            break
                    
                    param_name = param_info['name'] if param_info else row['Parameter']
                    st.write(f"**{param_name}**")
                    if param_info:
                        st.caption(param_info['description'])
                
                with col2:
                    st.metric("Weight", f"{row['Weight']:.1%}")
            
        else:
            st.info("Complete the profile creation to see your parameter analysis")
    
    with tab3:
        st.header("💾 Saved Profiles")
        st.info("Upload a previously saved configuration to recreate a profile")
        
        uploaded_file = st.file_uploader("Upload Configuration", type=['json'])
        if uploaded_file:
            try:
                config = json.load(uploaded_file)
                st.session_state.selected_params = config['selected_params']
                st.session_state.param_weights = config['param_weights']
                st.session_state.user_context = config['user_context']
                st.success("✅ Configuration loaded! Go to 'Create Profile' tab to generate.")
            except Exception as e:
                st.error(f"Error loading configuration: {e}")
    
    # Display generated profile
    if hasattr(st.session_state, 'generated_profile'):
        display_house_profile(
            st.session_state.generated_profile,
            st.session_state.selected_params,
            st.session_state.param_weights
        )

if __name__ == "__main__":
    main()