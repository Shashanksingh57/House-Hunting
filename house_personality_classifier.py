# house_personality_classifier.py
# Classify house "personalities" using free LLMs

import streamlit as st
import pandas as pd
import json
from typing import Dict, List
import requests
import os

# Free LLM Options
LLM_OPTIONS = {
    "Groq (Recommended)": {
        "description": "Fast inference with Llama 3, Mixtral",
        "models": ["llama3-70b-8192", "llama3-8b-8192", "mixtral-8x7b-32768"],
        "api_url": "https://api.groq.com/openai/v1/chat/completions",
        "free_tier": "30K tokens/minute",
        "setup": "Sign up at groq.com for free API key"
    },
    "Together AI": {
        "description": "Many open models, generous free tier",
        "models": ["meta-llama/Llama-3-70b-chat-hf", "mistralai/Mixtral-8x7B-Instruct-v0.1"],
        "api_url": "https://api.together.xyz/v1/chat/completions",
        "free_tier": "$25 free credit",
        "setup": "Sign up at together.ai"
    },
    "Hugging Face": {
        "description": "Free inference API",
        "models": ["mistralai/Mixtral-8x7B-Instruct-v0.1", "meta-llama/Llama-2-70b-chat-hf"],
        "api_url": "https://api-inference.huggingface.co/models/",
        "free_tier": "Limited rate",
        "setup": "Get token from huggingface.co"
    },
    "Ollama (Local)": {
        "description": "Run models locally - completely free",
        "models": ["llama3", "mixtral", "mistral", "phi"],
        "api_url": "http://localhost:11434/api/generate",
        "free_tier": "Unlimited (local)",
        "setup": "Install Ollama, run 'ollama pull llama3'"
    }
}

# House personality archetypes
HOUSE_ARCHETYPES = {
    "The Suburban Dream": {
        "key_params": ["good_schools", "large_yard", "quiet_street", "garage", "safe_neighborhood"],
        "description": "Perfect for families seeking the classic American dream"
    },
    "The Urban Oasis": {
        "key_params": ["walkability", "transit_score", "entertainment_nearby", "modern_updates"],
        "description": "City living with all conveniences at your doorstep"
    },
    "The Executive Estate": {
        "key_params": ["large_sqft", "premium_finishes", "master_suite", "high_price", "prestigious_area"],
        "description": "Luxury living for those who've made it"
    },
    "The Starter Home": {
        "key_params": ["affordable_price", "good_value", "needs_work", "small_size"],
        "description": "Perfect first step on the property ladder"
    },
    "The Remote Worker's Haven": {
        "key_params": ["home_office", "quiet_area", "fast_internet", "outdoor_space"],
        "description": "Designed for the work-from-home lifestyle"
    },
    "The Entertainer's Paradise": {
        "key_params": ["open_floor_plan", "large_kitchen", "outdoor_living", "entertainment_space"],
        "description": "Built for hosting and creating memories"
    },
    "The Green Sanctuary": {
        "key_params": ["energy_efficient", "solar_panels", "mature_trees", "sustainable_features"],
        "description": "Eco-friendly living in harmony with nature"
    },
    "The Fixer-Upper": {
        "key_params": ["needs_updates", "good_bones", "below_market", "older_home"],
        "description": "Diamond in the rough waiting for your vision"
    },
    "The Empty Nester's Retreat": {
        "key_params": ["single_level", "master_on_main", "low_maintenance", "smaller_size"],
        "description": "Right-sized comfort for the next chapter"
    },
    "The Investment Opportunity": {
        "key_params": ["below_market", "good_rental_area", "appreciation_potential", "multiple_units"],
        "description": "Smart money move with income potential"
    }
}

class HousePersonalityAnalyzer:
    """Analyze house personality using LLMs"""
    
    def __init__(self, llm_provider="Groq", api_key=None):
        self.provider = llm_provider
        self.api_key = api_key or os.getenv(f"{llm_provider.upper()}_API_KEY")
        self.provider_config = LLM_OPTIONS.get(llm_provider, LLM_OPTIONS["Groq"])
    
    def create_house_prompt(self, house_data: Dict, parameters: Dict) -> str:
        """Create a detailed prompt for the LLM"""
        
        prompt = f"""Analyze this house and give it a creative, memorable personality description.

HOUSE DATA:
- Address: {house_data.get('address', 'Unknown')}
- Price: ${house_data.get('price', 0):,}
- Size: {house_data.get('sqft', 0)} sqft
- Bedrooms: {house_data.get('bedrooms', 0)}
- Bathrooms: {house_data.get('bathrooms', 0)}
- Year Built: {house_data.get('year_built', 'Unknown')}
- Lot Size: {house_data.get('lot_size', 0)} sqft
- Days on Market: {house_data.get('days_on_market', 'Unknown')}
- Neighborhood: {house_data.get('neighborhood', 'Unknown')}

KEY FEATURES THAT MATTER TO BUYER:
"""
        
        # Add weighted parameters
        if parameters:
            sorted_params = sorted(parameters.items(), key=lambda x: x[1], reverse=True)[:10]
            for param, weight in sorted_params:
                param_value = house_data.get(param, 'Unknown')
                prompt += f"- {param}: {param_value} (importance: {weight:.0%})\n"
        
        prompt += """
Based on this information, provide:

1. A creative nickname for this house (e.g., "The Cozy Corner Cottage", "The Modern Marvel")
2. Its personality type from these options (or create your own):
   - The Suburban Dream (family-focused, safe, good schools)
   - The Urban Oasis (walkable, trendy, convenient)
   - The Executive Estate (luxury, spacious, prestigious)
   - The Starter Home (affordable, potential, first-time buyer)
   - The Remote Worker's Haven (quiet, home office, good internet)
   - The Entertainer's Paradise (open layout, great for hosting)
   - The Green Sanctuary (eco-friendly, efficient, natural)
   - The Fixer-Upper (needs work but has potential)
   - The Empty Nester's Retreat (downsizing, easy maintenance)
   - The Investment Opportunity (rental potential, appreciation)

3. A vivid 2-3 sentence description of the house's character and what kind of life someone would live there

4. Three unexpected benefits or hidden gems about this property

5. The ideal buyer profile (who would love this house most)

6. A lifestyle score (1-10) for these aspects:
   - Family Life
   - Work from Home
   - Entertainment
   - Relaxation
   - Investment Potential

Format your response as JSON."""
        
        return prompt
    
    def call_groq(self, prompt: str) -> Dict:
        """Call Groq API (recommended free option)"""
        
        if not self.api_key:
            return {"error": "No API key provided. Get one free at groq.com"}
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "llama3-8b-8192",  # Using smaller model for faster response
            "messages": [
                {"role": "system", "content": "You are a creative real estate personality analyst. Always respond with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        try:
            response = requests.post(
                self.provider_config["api_url"],
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                # Try to extract JSON from the response
                try:
                    # Sometimes the LLM includes markdown formatting
                    if "```json" in content:
                        content = content.split("```json")[1].split("```")[0].strip()
                    elif "```" in content:
                        content = content.split("```")[1].split("```")[0].strip()
                    return json.loads(content)
                except:
                    # If JSON parsing fails, return a structured error
                    return {
                        "nickname": "House",
                        "personality_type": "Unknown",
                        "description": content,
                        "error": "JSON parsing failed"
                    }
            else:
                return {"error": f"API error: {response.status_code} - {response.text}"}
                
        except Exception as e:
            return {"error": str(e)}
    
    def call_ollama(self, prompt: str) -> Dict:
        """Call local Ollama (completely free)"""
        
        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "llama3",
                    "prompt": prompt + "\n\nRespond only with valid JSON.",
                    "stream": False,
                    "format": "json"
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return json.loads(result['response'])
            else:
                return {"error": "Ollama not running. Install and run: ollama pull llama3"}
                
        except Exception as e:
            return {"error": f"Ollama error: {e}. Make sure Ollama is running locally."}
    
    def analyze_house(self, house_data: Dict, parameters: Dict) -> Dict:
        """Analyze a house and return its personality"""
        
        prompt = self.create_house_prompt(house_data, parameters)
        
        if self.provider == "Ollama (Local)":
            return self.call_ollama(prompt)
        elif self.provider == "Groq":
            return self.call_groq(prompt)
        else:
            # Add other providers as needed
            return {"error": f"Provider {self.provider} not implemented yet"}
    
    def get_batch_personalities(self, houses_df: pd.DataFrame, parameters: Dict, top_n: int = 10) -> List[Dict]:
        """Analyze multiple houses"""
        
        results = []
        
        # Take top N houses by score
        top_houses = houses_df.nlargest(top_n, 'overall_score') if 'overall_score' in houses_df.columns else houses_df.head(top_n)
        
        for idx, house in top_houses.iterrows():
            house_dict = house.to_dict()
            personality = self.analyze_house(house_dict, parameters)
            
            if "error" not in personality:
                personality["house_data"] = house_dict
                results.append(personality)
        
        return results

def create_personality_report(personality_data: Dict) -> str:
    """Create a nice formatted report from personality data"""
    
    report = f"""
# {personality_data.get('nickname', 'Unnamed House')}

**Personality Type:** {personality_data.get('personality_type', 'Unknown')}

## Character Description
{personality_data.get('description', 'No description available')}

## Hidden Gems
"""
    
    hidden_gems = personality_data.get('hidden_gems', [])
    if isinstance(hidden_gems, list):
        for gem in hidden_gems:
            report += f"- {gem}\n"
    
    report += f"""
## Ideal For
{personality_data.get('ideal_buyer', 'Anyone looking for a home')}

## Lifestyle Scores
"""
    
    scores = personality_data.get('lifestyle_scores', {})
    if isinstance(scores, dict):
        for aspect, score in scores.items():
            report += f"- {aspect}: {'⭐' * int(score)}/10\n"
    
    return report

# Streamlit UI - Main Application
def main():
    """Main Streamlit application"""
    
    st.title("🏠 House Personality Analyzer")
    st.markdown("*Discover the character and soul of each house using AI*")
    
    # LLM Setup
    with st.sidebar:
        st.header("🤖 AI Setup")
        
        provider = st.selectbox(
            "Choose LLM Provider",
            ["Groq", "Ollama (Local)", "Together AI", "Hugging Face"],
            help="Groq is recommended for best free performance"
        )
        
        provider_info = LLM_OPTIONS.get(provider, LLM_OPTIONS["Groq"])
        st.info(f"**{provider_info['description']}**\n\nFree tier: {provider_info['free_tier']}")
        
        if provider != "Ollama (Local)":
            api_key = st.text_input(
                "API Key",
                type="password",
                help=provider_info['setup']
            )
        else:
            api_key = None
            st.info("Make sure Ollama is running locally")
        
        st.markdown(f"**Setup:** {provider_info['setup']}")
    
    # Main interface
    tab1, tab2, tab3 = st.tabs(["🎯 Analyze Houses", "📊 Batch Analysis", "🎨 Custom Analysis"])
    
    with tab1:
        st.header("Analyze Your Top Houses")
        
        # File upload option
        uploaded_file = st.file_uploader("Upload your house data CSV", type=['csv'])
        
        if uploaded_file is not None:
            df = pd.read_csv(uploaded_file)
            st.success(f"Loaded {len(df)} houses from uploaded file")
            st.session_state.houses_df = df
        else:
            # Try to load from default location
            if st.button("Load House Data from Default Location"):
                try:
                    df = pd.read_csv('real_scored_houses.csv')
                    st.success(f"Loaded {len(df)} houses")
                    st.session_state.houses_df = df
                except:
                    st.error("No house data found. Upload a CSV or run your scoring system first!")
        
        if 'houses_df' in st.session_state and (api_key or provider == "Ollama (Local)"):
            analyzer = HousePersonalityAnalyzer(provider, api_key)
            
            # Load parameters (you'd get these from your parameter workshop)
            parameters = {
                "school_ratings": 0.20,
                "commute_time": 0.15,
                "price": 0.15,
                "square_footage": 0.10,
                "neighborhood_quality": 0.10
            }
            
            # Number of houses to analyze
            num_houses = st.slider("Number of houses to analyze", 1, 10, 5)
            
            if st.button("🎨 Analyze Top Houses", type="primary"):
                with st.spinner("Analyzing house personalities..."):
                    results = []
                    progress_bar = st.progress(0)
                    
                    # Analyze houses one by one with progress
                    top_houses = st.session_state.houses_df.head(num_houses)
                    
                    for i, (idx, house) in enumerate(top_houses.iterrows()):
                        progress_bar.progress((i + 1) / len(top_houses))
                        
                        house_dict = house.to_dict()
                        personality = analyzer.analyze_house(house_dict, parameters)
                        
                        if "error" not in personality:
                            personality["house_data"] = house_dict
                            results.append(personality)
                        else:
                            st.warning(f"Error analyzing house {i+1}: {personality.get('error', 'Unknown error')}")
                    
                    progress_bar.empty()
                    st.session_state.personality_results = results
            
            if 'personality_results' in st.session_state:
                st.success(f"Analyzed {len(st.session_state.personality_results)} houses successfully!")
                
                for i, result in enumerate(st.session_state.personality_results):
                    with st.expander(f"House {i+1}: {result.get('nickname', 'Unknown')}"):
                        house_data = result.get('house_data', {})
                        
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            st.markdown(create_personality_report(result))
                        
                        with col2:
                            st.metric("Price", f"${house_data.get('price', 0):,}")
                            st.metric("Size", f"{house_data.get('sqft', 0)} sqft")
                            st.metric("Bedrooms", house_data.get('bedrooms', 'N/A'))
                            if 'overall_score' in house_data:
                                st.metric("AI Score", f"{house_data['overall_score']:.1%}")
    
    with tab2:
        st.header("Batch Personality Analysis")
        
        if 'personality_results' in st.session_state and st.session_state.personality_results:
            # Show personality type distribution
            personality_types = [r.get('personality_type', 'Unknown') for r in st.session_state.personality_results]
            type_counts = pd.Series(personality_types).value_counts()
            
            st.subheader("Personality Type Distribution")
            st.bar_chart(type_counts)
            
            # Average lifestyle scores
            st.subheader("Average Lifestyle Scores")
            
            lifestyle_aspects = ['Family Life', 'Work from Home', 'Entertainment', 'Relaxation', 'Investment Potential']
            avg_scores = {}
            
            for aspect in lifestyle_aspects:
                scores = []
                for result in st.session_state.personality_results:
                    if 'lifestyle_scores' in result and isinstance(result['lifestyle_scores'], dict):
                        score = result['lifestyle_scores'].get(aspect, 0)
                        scores.append(score)
                
                if scores:
                    avg_scores[aspect] = sum(scores) / len(scores)
            
            if avg_scores:
                scores_df = pd.DataFrame(list(avg_scores.items()), columns=['Aspect', 'Average Score'])
                st.bar_chart(scores_df.set_index('Aspect'))
        else:
            st.info("Analyze some houses first to see batch analysis")
    
    with tab3:
        st.header("Custom House Analysis")
        st.markdown("Enter house details manually for personality analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            address = st.text_input("Address")
            price = st.number_input("Price", min_value=0, value=350000)
            sqft = st.number_input("Square Feet", min_value=0, value=1500)
            bedrooms = st.number_input("Bedrooms", min_value=0, value=3)
        
        with col2:
            bathrooms = st.number_input("Bathrooms", min_value=0.0, value=2.0, step=0.5)
            year_built = st.number_input("Year Built", min_value=1900, value=2010)
            lot_size = st.number_input("Lot Size (sqft)", min_value=0, value=7500)
            neighborhood = st.text_input("Neighborhood", value="Minneapolis")
        
        if st.button("Analyze This House") and (api_key or provider == "Ollama (Local)"):
            custom_house = {
                "address": address,
                "price": price,
                "sqft": sqft,
                "bedrooms": bedrooms,
                "bathrooms": bathrooms,
                "year_built": year_built,
                "lot_size": lot_size,
                "neighborhood": neighborhood
            }
            
            analyzer = HousePersonalityAnalyzer(provider, api_key)
            
            with st.spinner("Analyzing house personality..."):
                result = analyzer.analyze_house(custom_house, {})
            
            if "error" not in result:
                st.markdown(create_personality_report(result))
            else:
                st.error(f"Error: {result['error']}")

if __name__ == "__main__":
    main()