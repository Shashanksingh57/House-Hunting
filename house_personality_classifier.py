# integrate_personality_with_parameters.py
# Connect your parameter workshop to personality analysis

import json
import pandas as pd
from house_personality_classifier import HousePersonalityAnalyzer

def load_parameter_config(config_file):
    """Load parameters from your workshop"""
    with open(config_file, 'r') as f:
        config = json.load(f)
    return config['weights']

def enhance_house_data_with_personality(houses_df, parameter_weights, llm_provider="Groq", api_key=None):
    """Add personality analysis to your scored houses"""
    
    analyzer = HousePersonalityAnalyzer(llm_provider, api_key)
    
    # Add personality column
    personalities = []
    
    for idx, house in houses_df.iterrows():
        try:
            # Get personality analysis
            personality = analyzer.analyze_house(
                house.to_dict(),
                parameter_weights
            )
            
            if "error" not in personality:
                # Add key personality traits to the dataframe
                house_personality = {
                    'personality_nickname': personality.get('nickname', 'Unknown'),
                    'personality_type': personality.get('personality_type', 'Unknown'),
                    'personality_description': personality.get('description', ''),
                    'ideal_buyer': personality.get('ideal_buyer', ''),
                    'lifestyle_family': personality.get('lifestyle_scores', {}).get('Family Life', 0),
                    'lifestyle_wfh': personality.get('lifestyle_scores', {}).get('Work from Home', 0),
                    'lifestyle_entertainment': personality.get('lifestyle_scores', {}).get('Entertainment', 0),
                    'lifestyle_investment': personality.get('lifestyle_scores', {}).get('Investment Potential', 0)
                }
                personalities.append(house_personality)
            else:
                personalities.append({})
                
        except Exception as e:
            print(f"Error analyzing house {idx}: {e}")
            personalities.append({})
    
    # Add personality data to dataframe
    personality_df = pd.DataFrame(personalities)
    enhanced_df = pd.concat([houses_df, personality_df], axis=1)
    
    return enhanced_df

def match_buyer_to_houses(buyer_profile, houses_with_personality):
    """Match buyer profile to house personalities"""
    
    # Map buyer types to house personality types
    buyer_to_house_mapping = {
        "First-time buyer": ["The Starter Home", "The Fixer-Upper"],
        "Family with kids": ["The Suburban Dream", "The Entertainer's Paradise"],
        "Empty nesters": ["The Empty Nester's Retreat", "The Urban Oasis"],
        "Remote worker": ["The Remote Worker's Haven", "The Green Sanctuary"],
        "Young professional": ["The Urban Oasis", "The Executive Estate"],
        "Investor": ["The Investment Opportunity", "The Fixer-Upper"]
    }
    
    # Get matching personality types
    buyer_type = buyer_profile.get('buyer_type', 'Other')
    matching_personalities = buyer_to_house_mapping.get(buyer_type, [])
    
    # Filter houses by personality match
    if matching_personalities:
        personality_matches = houses_with_personality[
            houses_with_personality['personality_type'].isin(matching_personalities)
        ]
    else:
        personality_matches = houses_with_personality
    
    # Sort by overall score within personality matches
    return personality_matches.sort_values('overall_score', ascending=False)

# Example usage
if __name__ == "__main__":
    # Load your parameter configuration
    parameter_weights = load_parameter_config('house_scoring_config_family_with_kids.json')
    
    # Load your scored houses
    houses_df = pd.read_csv('real_scored_houses.csv')
    
    # Enhance with personality
    enhanced_houses = enhance_house_data_with_personality(
        houses_df.head(10),  # Top 10 houses
        parameter_weights,
        llm_provider="Groq",
        api_key="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"
    )
    
    # Save enhanced data
    enhanced_houses.to_csv('houses_with_personality.csv', index=False)
    
    # Show personality distribution
    print("\nHouse Personality Distribution:")
    print(enhanced_houses['personality_type'].value_counts())
    
    # Find best matches for buyer
    buyer_profile = {'buyer_type': 'Family with kids'}
    matches = match_buyer_to_houses(buyer_profile, enhanced_houses)
    
    print(f"\nBest matches for {buyer_profile['buyer_type']}:")
    for idx, house in matches.head(3).iterrows():
        print(f"\n{house['personality_nickname']}")
        print(f"Type: {house['personality_type']}")
        print(f"Price: ${house['price']:,}")
        print(f"Score: {house['overall_score']:.1%}")