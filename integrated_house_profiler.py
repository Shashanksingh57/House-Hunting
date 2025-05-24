# integrated_house_profiler.py
# Combines parameter selection with AI-generated ideal house profiles

import streamlit as st
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
GROQ_MODEL = "llama3-70b-8192"  # Best model for detailed analysis

# Comprehensive parameter structure
PARAMETERS = {
    "💰 Budget & Value": {
        "max_price": {"name": "Maximum Price", "type": "number", "unit": "$"},
        "min_price": {"name": "Minimum Price", "type": "number", "unit": "$"},
        "price_per_sqft": {"name": "Target $/sqft", "type": "number", "unit": "$/sqft"},
        "property_taxes": {"name": "Max Property Tax", "type": "number", "unit": "$/year"},
        "hoa_acceptable": {"name": "HOA Acceptable", "type": "boolean", "unit": ""},
    },
    "🏠 Size & Layout": {
        "min_sqft": {"name": "Minimum Square Feet", "type": "number", "unit": "sqft"},
        "max_sqft": {"name": "Maximum Square Feet", "type": "number", "unit": "sqft"},
        "bedrooms": {"name": "Number of Bedrooms", "type": "number", "unit": ""},
        "bathrooms": {"name": "Number of Bathrooms", "type": "number", "unit": ""},
        "stories": {"name": "Number of Stories", "type": "choice", "options": ["Single", "Two", "Three+", "Any"]},
        "open_floor_plan": {"name": "Open Floor Plan", "type": "boolean", "unit": ""},
        "home_office": {"name": "Dedicated Office", "type": "boolean", "unit": ""},
        "master_main_floor": {"name": "Master on Main", "type": "boolean", "unit": ""},
        "finished_basement": {"name": "Finished Basement", "type": "boolean", "unit": ""},
    },
    "📍 Location": {
        "neighborhoods": {"name": "Preferred Areas", "type": "multiselect", 
                         "options": ["Plymouth", "Minnetonka", "Eden Prairie", "Woodbury", "Maple Grove", 
                                   "Edina", "Wayzata", "Bloomington", "Burnsville", "Apple Valley"]},
        "max_commute": {"name": "Max Commute Time", "type": "number", "unit": "minutes"},
        "school_rating": {"name": "Min School Rating", "type": "number", "unit": "/10"},
        "walkability": {"name": "Walkability Important", "type": "boolean", "unit": ""},
        "quiet_street": {"name": "Quiet Street", "type": "boolean", "unit": ""},
    },
    "🏡 Property Features": {
        "lot_size": {"name": "Minimum Lot Size", "type": "number", "unit": "sqft"},
        "garage_spaces": {"name": "Garage Spaces", "type": "number", "unit": "cars"},
        "year_built_min": {"name": "Minimum Year Built", "type": "number", "unit": ""},
        "pool": {"name": "Pool Desired", "type": "boolean", "unit": ""},
        "fireplace": {"name": "Fireplace", "type": "boolean", "unit": ""},
        "hardwood_floors": {"name": "Hardwood Floors", "type": "boolean", "unit": ""},
        "updated_kitchen": {"name": "Updated Kitchen", "type": "boolean", "unit": ""},
        "move_in_ready": {"name": "Move-in Ready", "type": "boolean", "unit": ""},
    },
    "🌟 Lifestyle": {
        "entertaining_space": {"name": "Good for Entertaining", "type": "boolean", "unit": ""},
        "private_yard": {"name": "Private Backyard", "type": "boolean", "unit": ""},
        "pet_friendly": {"name": "Pet Friendly Yard", "type": "boolean", "unit": ""},
        "storage_space": {"name": "Lots of Storage", "type": "boolean", "unit": ""},
        "natural_light": {"name": "Natural Light Important", "type": "boolean", "unit": ""},
        "energy_efficient": {"name": "Energy Efficient", "type": "boolean", "unit": ""},
    }
}

class HouseProfileGenerator:
    """Generate ideal house profiles based on selected parameters"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def create_profile_prompt(self, selected_params: Dict, user_context: Dict) -> str:
        """Create a prompt for generating house profile"""
        
        prompt = f"""Based on the following home buyer preferences, create a detailed but practical house profile that can be used to search on Zillow and other real estate sites.

BUYER CONTEXT:
- Buyer Type: {user_context.get('buyer_type', 'Not specified')}
- Timeline: {user_context.get('timeline', 'Not specified')}
- Work Situation: {user_context.get('work_situation', 'Not specified')}

SPECIFIC REQUIREMENTS:
"""
        
        # Organize parameters by category
        for category, params in selected_params.items():
            if params:
                prompt += f"\n{category}:\n"
                for param_key, param_value in params.items():
                    if param_value is not None and param_value != "":
                        param_info = self._find_param_info(param_key)
                        if param_info:
                            if param_info['type'] == 'boolean' and param_value:
                                prompt += f"- Must have: {param_info['name']}\n"
                            else:
                                prompt += f"- {param_info['name']}: {param_value} {param_info.get('unit', '')}\n"
        
        prompt += """
Please provide:

1. SEARCH KEYWORDS (5-10 specific terms to use on Zillow)
   - Focus on features that are searchable/filterable
   - Include specific neighborhood names, features, styles

2. IDEAL HOUSE DESCRIPTION (2-3 paragraphs)
   - Write as if describing an actual listing
   - Include specific features, layout, and characteristics
   - Be specific about what to look for

3. MUST-HAVE FEATURES (Bullet list)
   - List the non-negotiable features
   - Be specific (e.g., "3-car garage" not just "garage")

4. NICE-TO-HAVE FEATURES (Bullet list)
   - Features that would be bonuses
   - Things to prioritize if choosing between similar houses

5. RED FLAGS TO AVOID
   - Specific things that would make a house unsuitable
   - Common issues to watch for

6. EXAMPLE ZILLOW SEARCH FILTERS
   - Specific filter settings to use
   - Price range, square footage, year built, etc.

7. TARGET NEIGHBORHOODS & WHY
   - Specific areas that match the criteria
   - Brief explanation of why each fits

Format the response in a clear, practical way that someone can immediately use to search for houses."""
        
        return prompt
    
    def _find_param_info(self, param_key: str) -> Dict:
        """Find parameter info from the structure"""
        for category, params in PARAMETERS.items():
            if param_key in params:
                return params[param_key]
        return None
    
    def generate_profile(self, selected_params: Dict, user_context: Dict) -> Dict:
        """Generate house profile using Groq"""
        
        prompt = self.create_profile_prompt(selected_params, user_context)
        
        data = {
            "model": GROQ_MODEL,
            "messages": [
                {
                    "role": "system", 
                    "content": "You are an expert real estate advisor who helps people find their perfect home. You provide practical, specific advice that can be immediately used on house hunting websites."
                },
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 2000
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
    
    def generate_search_query(self, selected_params: Dict) -> str:
        """Generate a Zillow-ready search query"""
        
        queries = []
        
        # Price range
        if 'min_price' in selected_params.get('💰 Budget & Value', {}):
            min_p = selected_params['💰 Budget & Value']['min_price']
            max_p = selected_params['💰 Budget & Value'].get('max_price', min_p + 100000)
            queries.append(f"${min_p:,}-${max_p:,}")
        
        # Bedrooms
        if 'bedrooms' in selected_params.get('🏠 Size & Layout', {}):
            beds = selected_params['🏠 Size & Layout']['bedrooms']
            queries.append(f"{int(beds)}+ beds")
        
        # Square footage
        if 'min_sqft' in selected_params.get('🏠 Size & Layout', {}):
            sqft = selected_params['🏠 Size & Layout']['min_sqft']
            queries.append(f"{int(sqft)}+ sqft")
        
        # Neighborhoods
        if 'neighborhoods' in selected_params.get('📍 Location', {}):
            areas = selected_params['📍 Location']['neighborhoods']
            if areas:
                queries.append(f"{', '.join(areas[:2])} area")
        
        return " ".join(queries)

def create_parameter_form():
    """Create the parameter selection form"""
    
    st.header("🎯 Define Your Dream Home")
    
    # User context
    with st.expander("👤 Tell us about yourself", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            buyer_type = st.selectbox(
                "I am a...",
                ["First-time buyer", "Growing family", "Downsizing", "Investor", 
                 "Remote worker", "Retiree", "Other"]
            )
        
        with col2:
            timeline = st.selectbox(
                "Planning to buy...",
                ["ASAP", "1-3 months", "3-6 months", "6-12 months", "Just browsing"]
            )
        
        with col3:
            work_situation = st.selectbox(
                "Work situation",
                ["Office downtown", "Hybrid", "Fully remote", "Multiple locations", "Retired"]
            )
    
    user_context = {
        "buyer_type": buyer_type,
        "timeline": timeline,
        "work_situation": work_situation
    }
    
    # Parameter selection
    selected_params = {}
    
    for category, params in PARAMETERS.items():
        with st.expander(f"{category}", expanded=(category == "💰 Budget & Value")):
            selected_params[category] = {}
            
            # Create appropriate input for each parameter type
            cols = st.columns(2)
            for i, (param_key, param_info) in enumerate(params.items()):
                col = cols[i % 2]
                
                with col:
                    if param_info['type'] == 'number':
                        if param_key == 'max_price':
                            value = st.number_input(
                                param_info['name'],
                                min_value=100000,
                                max_value=2000000,
                                value=500000,
                                step=25000,
                                help=f"Amount in {param_info['unit']}"
                            )
                        elif param_key == 'min_price':
                            value = st.number_input(
                                param_info['name'],
                                min_value=100000,
                                max_value=2000000,
                                value=300000,
                                step=25000,
                                help=f"Amount in {param_info['unit']}"
                            )
                        elif param_key == 'min_sqft':
                            value = st.number_input(
                                param_info['name'],
                                min_value=500,
                                max_value=10000,
                                value=1500,
                                step=100,
                                help=f"Size in {param_info['unit']}"
                            )
                        elif param_key == 'bedrooms':
                            value = st.number_input(
                                param_info['name'],
                                min_value=1,
                                max_value=8,
                                value=3
                            )
                        elif param_key == 'bathrooms':
                            value = st.number_input(
                                param_info['name'],
                                min_value=1.0,
                                max_value=6.0,
                                value=2.0,
                                step=0.5
                            )
                        elif param_key == 'year_built_min':
                            value = st.number_input(
                                param_info['name'],
                                min_value=1900,
                                max_value=2025,
                                value=2000,
                                step=5
                            )
                        elif param_key == 'garage_spaces':
                            value = st.number_input(
                                param_info['name'],
                                min_value=0,
                                max_value=5,
                                value=2,
                                help=f"Number of {param_info['unit']}"
                            )
                        elif param_key == 'lot_size':
                            value = st.number_input(
                                param_info['name'],
                                min_value=0,
                                max_value=50000,
                                value=7500,
                                step=500,
                                help=f"Size in {param_info['unit']}"
                            )
                        elif param_key == 'max_commute':
                            value = st.number_input(
                                param_info['name'],
                                min_value=5,
                                max_value=90,
                                value=30,
                                step=5,
                                help=f"Time in {param_info['unit']}"
                            )
                        elif param_key == 'school_rating':
                            value = st.number_input(
                                param_info['name'],
                                min_value=1,
                                max_value=10,
                                value=7,
                                help="Rating out of 10"
                            )
                        elif param_key == 'property_taxes':
                            value = st.number_input(
                                param_info['name'],
                                min_value=0,
                                max_value=50000,
                                value=5000,
                                step=500,
                                help=f"Amount in {param_info['unit']}"
                            )
                        elif param_key == 'price_per_sqft':
                            value = st.number_input(
                                param_info['name'],
                                min_value=50,
                                max_value=500,
                                value=200,
                                step=10,
                                help=f"Price in {param_info['unit']}"
                            )
                        elif param_key == 'max_sqft':
                            value = st.number_input(
                                param_info['name'],
                                min_value=500,
                                max_value=10000,
                                value=3000,
                                step=100,
                                help=f"Size in {param_info['unit']}"
                            )
                        else:
                            value = st.number_input(
                                param_info['name'], 
                                min_value=0,
                                help=f"Value in {param_info.get('unit', 'units')}" if param_info.get('unit') else None
                            )
                        
                        if value > 0:
                            selected_params[category][param_key] = value
                    
                    elif param_info['type'] == 'boolean':
                        value = st.checkbox(param_info['name'])
                        if value:
                            selected_params[category][param_key] = value
                    
                    elif param_info['type'] == 'choice':
                        value = st.selectbox(param_info['name'], param_info['options'])
                        if value != "Any":
                            selected_params[category][param_key] = value
                    
                    elif param_info['type'] == 'multiselect':
                        value = st.multiselect(param_info['name'], param_info['options'])
                        if value:
                            selected_params[category][param_key] = value
    
    # Quick presets
    st.markdown("### ⚡ Quick Presets")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("👨‍👩‍👧‍👦 Family Home"):
            selected_params['🏠 Size & Layout']['bedrooms'] = 4
            selected_params['🏠 Size & Layout']['bathrooms'] = 2.5
            selected_params['🏠 Size & Layout']['min_sqft'] = 2000
            selected_params['📍 Location']['school_rating'] = 8
            st.rerun()
    
    with col2:
        if st.button("💼 Young Professional"):
            selected_params['💰 Budget & Value']['max_price'] = 350000
            selected_params['🏠 Size & Layout']['bedrooms'] = 2
            selected_params['📍 Location']['walkability'] = True
            selected_params['📍 Location']['max_commute'] = 30
            st.rerun()
    
    with col3:
        if st.button("🏡 Empty Nester"):
            selected_params['🏠 Size & Layout']['stories'] = "Single"
            selected_params['🏠 Size & Layout']['master_main_floor'] = True
            selected_params['🏠 Size & Layout']['bedrooms'] = 2
            st.rerun()
    
    with col4:
        if st.button("💻 Remote Worker"):
            selected_params['🏠 Size & Layout']['home_office'] = True
            selected_params['📍 Location']['quiet_street'] = True
            selected_params['🌟 Lifestyle']['natural_light'] = True
            st.rerun()
    
    return selected_params, user_context

def display_house_profile(profile_text: str, selected_params: Dict):
    """Display the generated house profile"""
    
    st.header("🏡 Your Ideal House Profile")
    
    # Quick search query
    generator = HouseProfileGenerator("")  # Don't need API key for this
    search_query = generator.generate_search_query(selected_params)
    
    if search_query:
        st.info(f"**Quick Zillow Search:** {search_query}")
        
        # Direct Zillow search link
        zillow_url = f"https://www.zillow.com/homes/{search_query.replace(' ', '-').replace(',', '')}_rb/"
        st.markdown(f"[🔍 Search on Zillow]({zillow_url})")
    
    # Display the full profile
    st.markdown(profile_text)
    
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
        param_json = json.dumps(selected_params, indent=2)
        st.download_button(
            "⚙️ Save Parameters",
            param_json,
            file_name=f"house_params_{timestamp}.json",
            mime="application/json"
        )

def main():
    """Main application"""
    
    st.set_page_config(
        page_title="AI House Profile Generator",
        page_icon="🏡",
        layout="wide"
    )
    
    st.title("🏡 AI-Powered House Profile Generator")
    st.markdown("*Define your preferences and get a detailed profile of your ideal home*")
    
    # Load API key from environment
    from dotenv import load_dotenv
    load_dotenv()
    
    # Try to get API key from environment first
    api_key = os.getenv('GROQ_API_KEY') or os.getenv('RAPIDAPI_KEY')
    
    # If not in environment, allow manual input
    if not api_key:
        api_key = st.sidebar.text_input(
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
            
            Or add it to your .env file as:
            GROQ_API_KEY=your_api_key_here
            """)
    else:
        st.sidebar.success("✅ API key loaded from .env file")
        st.sidebar.caption(f"Key: {api_key[:8]}...")
    
    # Parameter selection
    selected_params, user_context = create_parameter_form()
    
    # Show selected parameters summary
    with st.sidebar:
        st.markdown("### 📊 Selected Parameters")
        
        param_count = sum(len(params) for params in selected_params.values())
        st.metric("Total Parameters", param_count)
        
        # Show key selections
        if selected_params.get('💰 Budget & Value', {}).get('max_price'):
            st.write(f"**Budget:** ${selected_params['💰 Budget & Value']['max_price']:,}")
        
        if selected_params.get('🏠 Size & Layout', {}).get('bedrooms'):
            beds = selected_params['🏠 Size & Layout']['bedrooms']
            baths = selected_params['🏠 Size & Layout'].get('bathrooms', 0)
            st.write(f"**Size:** {int(beds)} bed, {baths} bath")
        
        if selected_params.get('📍 Location', {}).get('neighborhoods'):
            areas = selected_params['📍 Location']['neighborhoods']
            st.write(f"**Areas:** {', '.join(areas[:3])}")
    
    # Generate profile button
    if st.button("🎨 Generate My House Profile", type="primary", disabled=not api_key):
        if param_count < 5:
            st.error("Please select at least 5 parameters to generate a meaningful profile")
        else:
            with st.spinner("Creating your personalized house profile..."):
                generator = HouseProfileGenerator(api_key)
                result = generator.generate_profile(selected_params, user_context)
                
                if result['success']:
                    st.session_state.generated_profile = result['profile']
                    st.session_state.selected_params = selected_params
                else:
                    st.error(f"Error generating profile: {result['error']}")
    
    # Display generated profile
    if 'generated_profile' in st.session_state:
        display_house_profile(
            st.session_state.generated_profile,
            st.session_state.selected_params
        )
    
    # Examples section
    with st.expander("📚 Example Use Cases"):
        st.markdown("""
        ### How to use your generated profile:
        
        1. **On Zillow:**
           - Copy the search keywords into Zillow's search bar
           - Use the filter settings provided
           - Save searches with these criteria for alerts
        
        2. **With Real Estate Agents:**
           - Share your profile with agents
           - They'll understand exactly what you're looking for
           - No more seeing irrelevant houses
        
        3. **For Comparison:**
           - Use the must-have list as a checklist
           - Score houses based on how many criteria they meet
           - Identify deal-breakers quickly
        """)

if __name__ == "__main__":
    main()