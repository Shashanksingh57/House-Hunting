# house_hunting_command_center.py
# Central hub for all house hunting tools and applications

import streamlit as st
import subprocess
import sys
import os
import pandas as pd
import json
import glob
from datetime import datetime
import requests
from pathlib import Path

st.set_page_config(
    page_title="🏠 House Hunting Command Center",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for the command center
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .tool-card {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #28a745;
        margin: 1rem 0;
        transition: transform 0.2s;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .tool-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
    }
    
    .status-good { border-left-color: #28a745; }
    .status-warning { border-left-color: #ffc107; }
    .status-error { border-left-color: #dc3545; }
    
    .metric-container {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        margin: 0.5rem 0;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }
    
    .launch-button {
        background: linear-gradient(45deg, #667eea, #764ba2);
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        font-weight: bold;
        cursor: pointer;
        transition: all 0.3s;
    }
    
    .launch-button:hover {
        transform: scale(1.05);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
</style>
""", unsafe_allow_html=True)

class HouseHuntingHub:
    """Central hub for managing all house hunting tools"""
    
    def __init__(self):
        self.tools = self.discover_tools()
        self.system_status = self.check_system_status()
        self.data_status = self.check_data_status()
    
    def discover_tools(self):
        """Automatically discover available tools in the project directory"""
        
        # Scan directory for Python files
        python_files = [f for f in os.listdir('.') if f.endswith('.py') and f != 'house_hunting_command_center.py']
        
        # Define tool categories and patterns
        tool_definitions = {
            # Data Collection Tools
            "zillow_collection_interface.py": {
                "category": "🏠 Data Collection",
                "name": "Zillow Data Collector",
                "description": "Collect fresh house data from Zillow API",
                "purpose": "Get new listings and update your database",
                "when_to_use": "When you need fresh market data",
                "port": 8501
            },
            "comprehensive_data_collector.py": {
                "category": "🏠 Data Collection",
                "name": "Comprehensive Collector",
                "description": "Bulk data collection with multiple searches",
                "purpose": "Gather large amounts of house data at once",
                "when_to_use": "For initial data gathering or major updates",
                "port": None
            },
            "fixed_zillow_collector.py": {
                "category": "🏠 Data Collection",
                "name": "Fixed Zillow Collector",
                "description": "Standalone Zillow data collector with error handling",
                "purpose": "Collect data with robust error handling",
                "when_to_use": "When other collectors have issues",
                "port": None
            },
            
            # Analytics Tools
            "zillow_data_analytics_dashboard.py": {
                "category": "📊 Analytics & Insights",
                "name": "Data Analytics Dashboard",
                "description": "Analyze your collected house data with maps and metrics",
                "purpose": "Understand what data you've collected",
                "when_to_use": "To analyze trends and see geographic distribution",
                "port": 8502
            },
            "live_dashboard.py": {
                "category": "📊 Analytics & Insights",
                "name": "Live Scoring Dashboard",
                "description": "Real-time house scoring and recommendations",
                "purpose": "View scored houses with AI recommendations",
                "when_to_use": "To see your top house recommendations",
                "port": 8503
            },
            "dynamic_dashboard.py": {
                "category": "📊 Analytics & Insights",
                "name": "Dynamic Preferences Dashboard",
                "description": "Adjust preferences and see results update in real-time",
                "purpose": "Experiment with different criteria",
                "when_to_use": "To fine-tune your search parameters",
                "port": 8506
            },
            "streamlit_app.py": {
                "category": "📊 Analytics & Insights",
                "name": "Main Streamlit App",
                "description": "Primary house hunting dashboard",
                "purpose": "Main interface for house analysis",
                "when_to_use": "General house hunting interface",
                "port": 8507
            },
            
            # Configuration Tools
            "parameter_workshop.py": {
                "category": "🎯 Configuration & Setup",
                "name": "Parameter Workshop",
                "description": "Configure your house hunting preferences",
                "purpose": "Set up scoring weights and priorities",
                "when_to_use": "To customize what's important to you",
                "port": 8504
            },
            "parameter_workshop_fixed.py": {
                "category": "🎯 Configuration & Setup",
                "name": "Parameter Workshop (Fixed)",
                "description": "Enhanced parameter configuration tool",
                "purpose": "Advanced preference configuration",
                "when_to_use": "For detailed preference setup",
                "port": 8504
            },
            "integrated_house_profiler.py": {
                "category": "🎯 Configuration & Setup",
                "name": "AI House Profiler",
                "description": "Generate ideal house profiles using AI",
                "purpose": "Create detailed profiles of your dream home",
                "when_to_use": "To clarify what you're looking for",
                "port": 8505
            },
            "house_personality_classifier.py": {
                "category": "🎯 Configuration & Setup",
                "name": "House Personality Classifier",
                "description": "Classify houses by personality types using AI",
                "purpose": "Understand house character and style",
                "when_to_use": "To find houses that match your personality",
                "port": 8508
            },
            
            # Utilities
            "all_in_one_house_hunter.py": {
                "category": "🔧 Utilities & Management",
                "name": "All-in-One House Hunter",
                "description": "Complete house hunting system with scoring",
                "purpose": "Comprehensive house analysis tool",
                "when_to_use": "For complete analysis workflow",
                "port": None
            },
            "quick_start_scorer.py": {
                "category": "🔧 Utilities & Management",
                "name": "Quick Start Scorer",
                "description": "Simple house scoring system",
                "purpose": "Basic house evaluation",
                "when_to_use": "For quick house scoring",
                "port": None
            },
            "manual_data_collection.py": {
                "category": "🔧 Utilities & Management",
                "name": "Manual Data Collection",
                "description": "Manually input house data",
                "purpose": "Add houses manually to your database",
                "when_to_use": "When you find houses outside API sources",
                "port": None
            },
            "simple_house_collector.py": {
                "category": "🔧 Utilities & Management",
                "name": "Simple House Collector",
                "description": "Basic house data collection tool",
                "purpose": "Simple data gathering",
                "when_to_use": "For basic data collection needs",
                "port": None
            }
        }
        
        # Organize tools by category
        organized_tools = {}
        
        for file in python_files:
            if file in tool_definitions:
                tool_info = tool_definitions[file].copy()
                category = tool_info.pop("category")
                tool_info["available"] = True
                
                if category not in organized_tools:
                    organized_tools[category] = {}
                organized_tools[category][file] = tool_info
        
        # Add missing tools as unavailable
        for file, tool_info in tool_definitions.items():
            if file not in python_files:
                category = tool_info["category"]
                tool_copy = tool_info.copy()
                tool_copy.pop("category")
                tool_copy["available"] = False
                
                if category not in organized_tools:
                    organized_tools[category] = {}
                organized_tools[category][file] = tool_copy
        
        return organized_tools
        
        # Check which files actually exist
        available_tools = {}
        for category, category_tools in tools.items():
            available_category = {}
            for filename, tool_info in category_tools.items():
                if os.path.exists(filename):
                    tool_info["available"] = True
                    available_category[filename] = tool_info
                else:
                    tool_info["available"] = False
                    available_category[filename] = tool_info
            available_tools[category] = available_category
        
        return available_tools
    
    def check_system_status(self):
        """Check system requirements and setup"""
        
        status = {
            "python_version": sys.version,
            "required_packages": {},
            "api_keys": {},
            "data_directory": True
        }
        
        # Check required packages
        required_packages = [
            "streamlit", "pandas", "plotly", "requests", 
            "geopy", "folium", "streamlit-folium", "python-dotenv"
        ]
        
        for package in required_packages:
            try:
                __import__(package.replace("-", "_"))
                status["required_packages"][package] = "✅ Installed"
            except ImportError:
                status["required_packages"][package] = "❌ Missing"
        
        # Check API keys
        from dotenv import load_dotenv
        load_dotenv()
        
        api_keys = ["RAPIDAPI_KEY", "GROQ_API_KEY"]
        for key in api_keys:
            value = os.getenv(key)
            if value:
                status["api_keys"][key] = f"✅ Set ({value[:8]}...)"
            else:
                status["api_keys"][key] = "❌ Missing"
        
        return status
    
    def check_data_status(self):
        """Check available data files and their status"""
        
        data_patterns = [
            "real_scored_houses.csv",
            "real_zillow_data.csv", 
            "zillow_houses_*.csv",
            "comprehensive_houses_*.csv",
            "ai_house_analysis.csv"
        ]
        
        found_files = []
        total_houses = 0
        
        for pattern in data_patterns:
            if "*" in pattern:
                files = glob.glob(pattern)
                found_files.extend(files)
            else:
                if os.path.exists(pattern):
                    found_files.append(pattern)
        
        # Get file info
        file_info = []
        for file in found_files:
            try:
                df = pd.read_csv(file)
                size_kb = os.path.getsize(file) / 1024
                modified = datetime.fromtimestamp(os.path.getmtime(file))
                
                file_info.append({
                    "filename": file,
                    "houses": len(df),
                    "size_kb": size_kb,
                    "modified": modified
                })
                total_houses += len(df)
                
            except Exception as e:
                file_info.append({
                    "filename": file,
                    "houses": 0,
                    "size_kb": 0,
                    "modified": None,
                    "error": str(e)
                })
        
        return {
            "files": file_info,
            "total_files": len(found_files),
            "total_houses": total_houses,
            "last_updated": max([f["modified"] for f in file_info if f["modified"]], default=None)
        }
    
    def launch_tool(self, filename, port=None):
        """Launch a tool in a new browser tab"""
        
        if not os.path.exists(filename):
            return False, f"File {filename} not found"
        
        try:
            if port:
                # Launch Streamlit app on specific port
                cmd = f"streamlit run {filename} --server.port {port} --server.headless true"
                subprocess.Popen(cmd, shell=True)
                return True, f"Launching on http://localhost:{port}"
            else:
                # Run Python script
                subprocess.Popen([sys.executable, filename])
                return True, f"Running {filename}"
        except Exception as e:
            return False, f"Error launching {filename}: {str(e)}"

def display_header():
    """Display the main header"""
    
    st.markdown("""
    <div class="main-header">
        <h1>🏠 House Hunting Command Center</h1>
        <p>Your central hub for AI-powered house hunting tools</p>
        <p><em>Launch any tool, check system status, and manage your house hunting workflow</em></p>
    </div>
    """, unsafe_allow_html=True)

def display_system_status(hub):
    """Display system status overview"""
    
    st.header("🔧 System Status")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-container">
            <h3>🐍 Python</h3>
            <p>Version {}</p>
        </div>
        """.format(sys.version.split()[0]), unsafe_allow_html=True)
    
    with col2:
        missing_packages = [k for k, v in hub.system_status["required_packages"].items() if "❌" in v]
        status_color = "🔴" if missing_packages else "🟢"
        st.markdown("""
        <div class="metric-container">
            <h3>{} Packages</h3>
            <p>{} / {} Ready</p>
        </div>
        """.format(status_color, 
                  len(hub.system_status["required_packages"]) - len(missing_packages),
                  len(hub.system_status["required_packages"])), unsafe_allow_html=True)
    
    with col3:
        missing_keys = [k for k, v in hub.system_status["api_keys"].items() if "❌" in v]
        key_color = "🔴" if missing_keys else "🟢"
        st.markdown("""
        <div class="metric-container">
            <h3>{} API Keys</h3>
            <p>{} / {} Set</p>
        </div>
        """.format(key_color,
                  len(hub.system_status["api_keys"]) - len(missing_keys),
                  len(hub.system_status["api_keys"])), unsafe_allow_html=True)
    
    with col4:
        data_color = "🟢" if hub.data_status["total_houses"] > 0 else "🔴"
        st.markdown("""
        <div class="metric-container">
            <h3>{} Data</h3>
            <p>{} Houses</p>
        </div>
        """.format(data_color, hub.data_status["total_houses"]), unsafe_allow_html=True)
    
    # Show missing requirements
    missing_packages = [k for k, v in hub.system_status["required_packages"].items() if "❌" in v]
    missing_keys = [k for k, v in hub.system_status["api_keys"].items() if "❌" in v]
    
    if missing_packages or missing_keys:
        st.warning("⚠️ **Setup Required**")
        
        if missing_packages:
            st.write("**Missing Packages:**")
            st.code(f"pip install {' '.join(missing_packages)}")
        
        if missing_keys:
            st.write("**Missing API Keys:**")
            for key in missing_keys:
                st.write(f"• Add `{key}=your_key_here` to your .env file")

def display_data_overview(hub):
    """Display data overview"""
    
    st.header("📊 Data Overview")
    
    if hub.data_status["total_houses"] == 0:
        st.warning("❌ **No house data found**")
        st.info("🚀 **Get Started:** Use the Data Collection tools to gather house data")
        return
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📁 Data Files")
        
        for file_info in hub.data_status["files"]:
            if file_info.get("error"):
                st.error(f"❌ {file_info['filename']}: {file_info['error']}")
            else:
                days_old = (datetime.now() - file_info["modified"]).days if file_info["modified"] else "Unknown"
                
                st.markdown(f"""
                <div class="tool-card status-good">
                    <h4>📄 {file_info['filename']}</h4>
                    <p>🏠 <strong>{file_info['houses']}</strong> houses | 
                       💾 <strong>{file_info['size_kb']:.1f}KB</strong> | 
                       📅 <strong>{days_old} days old</strong></p>
                </div>
                """, unsafe_allow_html=True)
    
    with col2:
        st.subheader("📈 Quick Stats")
        
        st.metric("Total Houses", hub.data_status["total_houses"])
        st.metric("Data Files", hub.data_status["total_files"])
        
        if hub.data_status["last_updated"]:
            days_since_update = (datetime.now() - hub.data_status["last_updated"]).days
            st.metric("Days Since Update", days_since_update)
            
            if days_since_update > 7:
                st.warning("⚠️ Data is getting old")
            elif days_since_update > 3:
                st.info("💡 Consider updating soon")
            else:
                st.success("✅ Data is fresh")

def display_tools(hub):
    """Display tools in logical workflow order"""
    
    st.header("🛠️ House Hunting Workflow")
    st.markdown("*Follow this logical sequence for optimal house hunting*")
    
    # Step 1: Profile & Preferences
    st.subheader("1️⃣ Define Your Ideal Home")
    st.markdown("*Start here to clarify what you're looking for*")
    
    # Enhanced file detection for Seamless Integrated Profiler
    profiler_files = [
        "seamless_integrated_profiler.py",
        "integrated_house_profiler.py",
        "house_profiler.py",
        "seamless_profiler.py"
    ]
    
    profiler_file = None
    profiler_exists = False
    
    # Try to find any profiler file
    for filename in profiler_files:
        if os.path.exists(filename):
            profiler_file = filename
            profiler_exists = True
            break
    
    # If no profiler found, default to the expected name
    if not profiler_file:
        profiler_file = "seamless_integrated_profiler.py"
    
    # Define tool info
    profiler_tool = {
        "name": "Seamless Integrated Profiler",
        "description": "Complete preference setup and ideal home profiling with AI",
        "purpose": "Define your dream home criteria and preferences using AI assistance",
        "when_to_use": "Start here - before any data collection or house hunting",
        "available": profiler_exists,
        "port": 8501,
        "actual_file": profiler_file
    }
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        status_class = "status-good" if profiler_exists else "status-error"
        status_icon = "✅" if profiler_exists else "❌"
        
        st.markdown(f"""
        <div class="tool-card {status_class}">
            <h4>{status_icon} {profiler_tool['name']}</h4>
            <p><strong>Purpose:</strong> {profiler_tool['purpose']}</p>
            <p><strong>When to use:</strong> {profiler_tool['when_to_use']}</p>
            <p><em>{profiler_tool['description']}</em></p>
            {"<p><small>📁 Found: " + profiler_file + "</small></p>" if profiler_exists else ""}
        </div>
        """, unsafe_allow_html=True)
        
        # Debug information
        if not profiler_exists:
            st.error("🔍 **Debugging Info:**")
            current_dir_files = [f for f in os.listdir('.') if f.endswith('.py')]
            
            # Show all Python files
            st.write("**Python files in current directory:**")
            for f in sorted(current_dir_files):
                st.write(f"  • {f}")
            
            # Check for similar files
            similar_files = [f for f in current_dir_files if 'profiler' in f.lower() or 'integrated' in f.lower()]
            if similar_files:
                st.write("**Similar files found:**")
                for f in similar_files:
                    st.write(f"  🔍 {f}")
            
            st.write(f"**Current working directory:** `{os.getcwd()}`")
    
    with col2:
        if profiler_exists:
            if st.button(f"🚀 Launch Profiler", key="profiler_launch"):
                success, message = hub.launch_tool(profiler_file, profiler_tool.get("port"))
                if success:
                    st.success(f"✅ {message}")
                    st.info(f"🌐 Open: http://localhost:{profiler_tool['port']}")
                else:
                    st.error(f"❌ {message}")
        else:
            st.error(f"❌ File not found")
            st.caption("Looking for:")
            for filename in profiler_files:
                st.caption(f"  • {filename}")
            
            # Quick create button
            if st.button("📝 Create File", key="create_profiler"):
                st.info(f"Would create {profiler_file}")
                st.code(f"touch {profiler_file}", language="bash")
    
    st.markdown("---")
    
    # Step 2: House Ranking Dashboard
    st.subheader("2️⃣ House Ranking Dashboard")
    st.markdown("*Score and rank houses based on your criteria*")
    
    # Dynamic Dashboard - renamed to House Ranking Dashboard
    ranking_file = "dynamic_dashboard.py"
    ranking_exists = os.path.exists(ranking_file)
    
    ranking_tool = {
        "name": "House Ranking Dashboard",
        "description": "AI-powered house scoring and ranking with real-time adjustments",
        "purpose": "Score, rank, and compare houses using your personalized criteria",
        "when_to_use": "After profiling, to see scored houses and adjust ranking criteria",
        "available": ranking_exists,
        "port": 8502
    }
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        status_class = "status-good" if ranking_exists else "status-error"
        status_icon = "✅" if ranking_exists else "❌"
        
        st.markdown(f"""
        <div class="tool-card {status_class}">
            <h4>{status_icon} {ranking_tool['name']}</h4>
            <p><strong>Purpose:</strong> {ranking_tool['purpose']}</p>
            <p><strong>When to use:</strong> {ranking_tool['when_to_use']}</p>
            <p><em>{ranking_tool['description']}</em></p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        if ranking_exists:
            if st.button(f"🚀 Launch Ranking Dashboard", key="ranking_launch"):
                success, message = hub.launch_tool(ranking_file, ranking_tool.get("port"))
                if success:
                    st.success(f"✅ {message}")
                    st.info(f"🌐 Open: http://localhost:{ranking_tool['port']}")
                else:
                    st.error(f"❌ {message}")
        else:
            st.error(f"❌ {ranking_file} not found")
            st.caption("House scoring and ranking interface")
    
    st.markdown("---")
    
    # Step 3: Data Collection Section
    st.subheader("3️⃣ Zillow Data Collection")
    st.markdown("*Gather house data and monitor your collection*")
    
    # Analytics Dashboard First
    analytics_file = "zillow_data_analytics_dashboard.py"
    analytics_tool = None
    
    for category_tools in hub.tools.values():
        if analytics_file in category_tools:
            analytics_tool = category_tools[analytics_file]
            break
    
    if not analytics_tool:
        analytics_tool = {
            "name": "Zillow Data Analytics Dashboard",
            "description": "Monitor your data collection with maps, metrics, and insights",
            "purpose": "See what data you've collected and analyze market trends",
            "when_to_use": "Check this regularly to monitor your data collection progress",
            "available": os.path.exists(analytics_file),
            "port": 8503
        }
    
    # Comprehensive Collector
    collector_file = "comprehensive_data_collector.py"
    collector_tool = None
    
    for category_tools in hub.tools.values():
        if collector_file in category_tools:
            collector_tool = category_tools[collector_file]
            break
    
    if not collector_tool:
        collector_tool = {
            "name": "Comprehensive Data Collector",
            "description": "Bulk collection of house data from multiple searches",
            "purpose": "Gather large amounts of house data efficiently",
            "when_to_use": "When you need fresh data or want to expand your database",
            "available": os.path.exists(collector_file),
            "port": None
        }
    
    # Analytics Dashboard
    st.markdown("##### 📊 Data Monitoring")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        status_class = "status-good" if analytics_tool["available"] else "status-error"
        status_icon = "✅" if analytics_tool["available"] else "❌"
        
        st.markdown(f"""
        <div class="tool-card {status_class}">
            <h4>{status_icon} {analytics_tool['name']}</h4>
            <p><strong>Purpose:</strong> {analytics_tool['purpose']}</p>
            <p><strong>When to use:</strong> {analytics_tool['when_to_use']}</p>
            <p><em>{analytics_tool['description']}</em></p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        if analytics_tool["available"]:
            if st.button(f"📊 View Analytics", key="analytics_launch"):
                success, message = hub.launch_tool(analytics_file, analytics_tool.get("port"))
                if success:
                    st.success(f"✅ {message}")
                    st.info(f"🌐 Open: http://localhost:{analytics_tool['port']}")
                else:
                    st.error(f"❌ {message}")
        else:
            st.error(f"❌ {analytics_file} not found")
    
    # Data Collection Actions
    st.markdown("##### 🔄 Data Collection Actions")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        status_class = "status-good" if collector_tool["available"] else "status-error"
        status_icon = "✅" if collector_tool["available"] else "❌"
        
        st.markdown(f"""
        <div class="tool-card {status_class}">
            <h4>{status_icon} {collector_tool['name']}</h4>
            <p><strong>Purpose:</strong> {collector_tool['purpose']}</p>
            <p><strong>When to use:</strong> {collector_tool['when_to_use']}</p>
            <p><em>{collector_tool['description']}</em></p>
        </div>
        """, unsafe_allow_html=True)
        
        # Show current data status
        if hub.data_status["total_houses"] > 0:
            days_since_update = 0
            if hub.data_status["last_updated"]:
                days_since_update = (datetime.now() - hub.data_status["last_updated"]).days
            
            if days_since_update > 7:
                st.warning(f"⚠️ Data is {days_since_update} days old - consider updating")
            elif days_since_update > 3:
                st.info(f"💡 Data is {days_since_update} days old - may want to refresh soon")
            else:
                st.success(f"✅ Data is fresh ({days_since_update} days old)")
        else:
            st.info("📭 No data collected yet - start with comprehensive collection")
    
    with col2:
        if collector_tool["available"]:
            # Check API key status
            api_key = os.getenv('RAPIDAPI_KEY')
            
            if api_key:
                if st.button(f"🚀 Run Collector", key="collector_launch", type="primary"):
                    success, message = hub.launch_tool(collector_file, None)
                    if success:
                        st.success(f"✅ {message}")
                        st.info("⏳ Collection running in background...")
                    else:
                        st.error(f"❌ {message}")
                
                st.caption(f"API Key: {api_key[:8]}...")
            else:
                st.error("❌ No RAPIDAPI_KEY")
                st.caption("Add to .env file first")
        else:
            st.error(f"❌ {collector_file} not found")
    
    # Workflow guidance
    st.markdown("---")
    st.markdown("### 🎯 Recommended Workflow")
    
    workflow_col1, workflow_col2 = st.columns(2)
    
    with workflow_col1:
        st.markdown("""
        **🆕 First Time Setup:**
        1. Start with **Seamless Integrated Profiler**
        2. Use **House Ranking Dashboard** to score houses
        3. Run **Comprehensive Collector** to get initial data
        4. Monitor progress with **Analytics Dashboard**
        """)
    
    with workflow_col2:
        st.markdown("""
        **🔄 Regular Usage:**
        1. Check **Analytics Dashboard** for insights
        2. Adjust scoring in **House Ranking Dashboard**
        3. Run **Collector** weekly for fresh data
        4. Review newly ranked opportunities
        """)
    
    # Quick status overview
    st.markdown("### 📊 Quick Status")
    
    status_col1, status_col2, status_col3, status_col4 = st.columns(4)
    
    with status_col1:
        profiler_status = "🟢" if profiler_exists else "🔴"
        st.markdown(f"{profiler_status} **Profiler** {'Ready' if profiler_exists else 'Missing'}")
    
    with status_col2:
        ranking_status = "🟢" if ranking_exists else "🔴"
        st.markdown(f"{ranking_status} **Ranking** {'Ready' if ranking_exists else 'Missing'}")
    
    with status_col3:
        analytics_status = "🟢" if analytics_tool["available"] else "🔴"
        st.markdown(f"{analytics_status} **Analytics** {'Ready' if analytics_tool['available'] else 'Missing'}")
    
    with status_col4:
        collector_status = "🟢" if collector_tool["available"] else "🔴"
        st.markdown(f"{collector_status} **Collector** {'Ready' if collector_tool['available'] else 'Missing'}")

def display_quick_actions():
    """Display quick actions and workflows"""
    
    st.header("⚡ Quick Actions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 Recommended Workflows")
        
        workflows = [
            {
                "name": "🚀 First Time Setup",
                "steps": [
                    "1. Check system status above",
                    "2. Set up API keys in .env file", 
                    "3. Run Parameter Workshop to set preferences",
                    "4. Use Zillow Collector to get initial data",
                    "5. View results in Analytics Dashboard"
                ]
            },
            {
                "name": "📊 Daily House Hunting",
                "steps": [
                    "1. Check Analytics Dashboard for new insights",
                    "2. Use Live Dashboard to see top recommendations",
                    "3. Adjust preferences in Dynamic Dashboard",
                    "4. Collect fresh data if needed"
                ]
            },
            {
                "name": "🔄 Weekly Data Refresh", 
                "steps": [
                    "1. Run Comprehensive Collector for bulk update",
                    "2. Check Analytics Dashboard for trends",
                    "3. Update preferences based on new insights",
                    "4. Export top recommendations"
                ]
            }
        ]
        
        for workflow in workflows:
            with st.expander(workflow["name"]):
                for step in workflow["steps"]:
                    st.write(step)
    
    with col2:
        st.subheader("🛠️ Utilities")
        
        if st.button("📁 Open Project Directory"):
            if sys.platform == "win32":
                os.startfile(".")
            elif sys.platform == "darwin":
                subprocess.run(["open", "."])
            else:
                subprocess.run(["xdg-open", "."])
        
        if st.button("🔄 Refresh All Status"):
            st.cache_data.clear()
            st.rerun()
        
        if st.button("📝 View .env File"):
            if os.path.exists(".env"):
                with open(".env", "r") as f:
                    env_content = f.read()
                st.code(env_content, language="bash")
            else:
                st.warning(".env file not found")
        
        if st.button("📋 Generate Setup Report"):
            # Create a setup report
            report = {
                "timestamp": datetime.now().isoformat(),
                "system_status": hub.system_status,
                "data_status": hub.data_status,
                "available_tools": {k: {fname: finfo["available"] for fname, finfo in tools.items()} 
                                 for k, tools in hub.tools.items()}
            }
            
            st.download_button(
                "💾 Download Setup Report",
                json.dumps(report, indent=2, default=str),
                file_name=f"house_hunting_setup_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )

def main():
    """Main command center application"""
    
    # Initialize the hub
    hub = HouseHuntingHub()
    
    # Display header
    display_header()
    
    # Main content in tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🔧 Status", "📊 Data", "🛠️ Tools", "⚡ Quick Actions"])
    
    with tab1:
        display_system_status(hub)
    
    with tab2:
        display_data_overview(hub)
    
    with tab3:
        display_tools(hub)
    
    with tab4:
        display_quick_actions()
    
    # Sidebar with overview
    with st.sidebar:
        st.header("📋 Overview")
        
        # Quick metrics
        available_tools = sum(1 for category in hub.tools.values() 
                            for tool in category.values() if tool["available"])
        total_tools = sum(len(category) for category in hub.tools.values())
        
        st.metric("Available Tools", f"{available_tools}/{total_tools}")
        st.metric("Total Houses", hub.data_status["total_houses"])
        
        # Quick launch buttons for most common tools in workflow order
        st.markdown("### 🚀 Quick Launch")
        
        # Updated priority tools following the logical workflow
        priority_tools = [
            ("seamless_integrated_profiler.py", "1️⃣ Start Profiler"),
            ("dynamic_dashboard.py", "2️⃣ House Ranking"),
            ("zillow_data_analytics_dashboard.py", "3️⃣ Analytics"),
            ("comprehensive_data_collector.py", "🔄 Collect Data")
        ]
        
        for filename, label in priority_tools:
            # Check if file exists directly
            file_exists = os.path.exists(filename)
            
            # Try to find in discovered tools first, then fallback to file check
            tool_info = None
            for category_tools in hub.tools.values():
                if filename in category_tools:
                    tool_info = category_tools[filename]
                    break
            
            # If not in discovered tools but file exists, create basic tool info
            if not tool_info and file_exists:
                port_map = {
                    "seamless_integrated_profiler.py": 8501,
                    "dynamic_dashboard.py": 8502,
                    "zillow_data_analytics_dashboard.py": 8503,
                    "comprehensive_data_collector.py": None
                }
                tool_info = {"available": True, "port": port_map.get(filename)}
            
            if tool_info and tool_info["available"]:
                if st.button(label, key=f"sidebar_{filename}"):
                    success, message = hub.launch_tool(filename, tool_info.get("port"))
                    if success:
                        st.success("✅ Launched!")
                        if tool_info.get("port"):
                            st.caption(f"Port: {tool_info['port']}")
            else:
                st.caption(f"❌ {filename} missing")
        
        # Show workflow status
        st.markdown("### 📊 Workflow Status")
        
        workflow_files = [
            "seamless_integrated_profiler.py",
            "dynamic_dashboard.py", 
            "zillow_data_analytics_dashboard.py",
            "comprehensive_data_collector.py"
        ]
        
        ready_count = sum(1 for f in workflow_files if os.path.exists(f))
        st.metric("Workflow Ready", f"{ready_count}/4")
        
        if ready_count == 4:
            st.success("🎉 Complete setup!")
        elif ready_count >= 2:
            st.info("📈 Partially ready")
        else:
            st.warning("⚠️ Setup needed")
        
        # Debug info to help troubleshoot
        st.markdown("### 🔍 Detailed File Detection")
        
        # Show current directory
        current_dir = os.getcwd()
        st.caption(f"📁 **Current directory:** {current_dir}")
        
        # List all Python files
        py_files = [f for f in os.listdir('.') if f.endswith('.py')]
        st.caption(f"📄 **Python files found:** {len(py_files)}")
        
        # Check each workflow file specifically
        workflow_files = [
            "seamless_integrated_profiler.py",
            "dynamic_dashboard.py", 
            "zillow_data_analytics_dashboard.py",
            "comprehensive_data_collector.py"
        ]
        
        for f in workflow_files:
            exists = os.path.exists(f)
            status = "✅" if exists else "❌"
            st.caption(f"{status} {f}")
        
        # Look for similar files
        st.caption("**Files containing 'profiler':**")
        profiler_files = [f for f in py_files if 'profiler' in f.lower()]
        if profiler_files:
            for f in profiler_files:
                st.caption(f"  🔍 {f}")
        else:
            st.caption("  None found")
        
        st.caption("**Files containing 'integrated':**")
        integrated_files = [f for f in py_files if 'integrated' in f.lower()]
        if integrated_files:
            for f in integrated_files:
                st.caption(f"  🔍 {f}")
        else:
            st.caption("  None found")
        
        # Manual file check
        st.markdown("### 🔧 Manual Check")
        manual_file = st.text_input("Enter exact filename:", key="manual_file_check")
        if manual_file:
            file_exists = os.path.exists(manual_file)
            if file_exists:
                st.success(f"✅ {manual_file} exists!")
            else:
                st.error(f"❌ {manual_file} not found")
        
        st.markdown("---")
        st.caption(f"Last refreshed: {datetime.now().strftime('%H:%M:%S')}")

if __name__ == "__main__":
    main()