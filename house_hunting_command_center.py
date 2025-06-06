# house_hunting_command_center.py
# Central hub for all house hunting tools and applications - FIXED VERSION

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
            
            # Analytics Tools
            "zillow_data_analytics_dashboard.py": {
                "category": "📊 Analytics & Insights",
                "name": "Data Analytics Dashboard",
                "description": "Analyze your collected house data with maps and metrics",
                "purpose": "Understand what data you've collected",
                "when_to_use": "To analyze trends and see geographic distribution",
                "port": 8502
            },
            "dynamic_dashboard.py": {
                "category": "📊 Analytics & Insights",
                "name": "House Ranking Dashboard",
                "description": "Real-time house scoring and recommendations",
                "purpose": "Score and rank houses based on your criteria",
                "when_to_use": "To see scored houses and adjust ranking criteria",
                "port": 8503
            },
            
            # Configuration Tools
            "seamless_integrated_profiler.py": {
                "category": "🎯 Configuration & Setup",
                "name": "Seamless Integrated Profiler",
                "description": "Complete preference setup and ideal home profiling with AI",
                "purpose": "Define your dream home criteria and preferences",
                "when_to_use": "Start here - before any data collection",
                "port": 8504
            },
            "parameter_workshop_fixed.py": {
                "category": "🎯 Configuration & Setup",
                "name": "Parameter Workshop",
                "description": "Enhanced parameter configuration tool",
                "purpose": "Advanced preference configuration",
                "when_to_use": "For detailed preference setup",
                "port": 8505
            },
            
            # Utilities
            "all_in_one_house_hunter.py": {
                "category": "🔧 Utilities & Management",
                "name": "All-in-One House Hunter",
                "description": "Complete house hunting system with scoring",
                "purpose": "Comprehensive house analysis tool",
                "when_to_use": "For complete analysis workflow",
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

def display_workflow_tools(hub):
    """Display tools in logical workflow order"""
    
    st.header("🛠️ House Hunting Workflow")
    st.markdown("*Follow this sequence for optimal house hunting*")
    
    # Step 1: Define Your Ideal Home
    st.subheader("1️⃣ Define Your Ideal Home")
    st.markdown("*Start here to clarify what you're looking for*")
    
    profiler_files = [
        "seamless_integrated_profiler.py",
        "integrated_house_profiler.py",
        "parameter_workshop_fixed.py"
    ]
    
    profiler_file = None
    for filename in profiler_files:
        if os.path.exists(filename):
            profiler_file = filename
            break
    
    if profiler_file:
        tool_info = hub.tools.get("🎯 Configuration & Setup", {}).get(profiler_file, {
            "name": "Profile Setup Tool",
            "description": "Set up your house hunting preferences",
            "port": 8504,
            "available": True
        })
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown(f"""
            <div class="tool-card status-good">
                <h4>✅ {tool_info['name']}</h4>
                <p><strong>Purpose:</strong> Define your dream home criteria and preferences</p>
                <p><strong>When to use:</strong> Start here before any data collection</p>
                <p><em>{tool_info['description']}</em></p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            if st.button("🚀 Launch Profiler", key="profiler_launch"):
                success, message = hub.launch_tool(profiler_file, tool_info.get("port", 8504))
                if success:
                    st.success(f"✅ {message}")
                else:
                    st.error(f"❌ {message}")
    else:
        st.error("❌ No profiler tool found. Looking for: seamless_integrated_profiler.py")
    
    st.markdown("---")
    
    # Step 2: House Ranking Dashboard
    st.subheader("2️⃣ House Ranking Dashboard")
    st.markdown("*Score and rank houses based on your criteria*")
    
    ranking_file = "dynamic_dashboard.py"
    if os.path.exists(ranking_file):
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown(f"""
            <div class="tool-card status-good">
                <h4>✅ House Ranking Dashboard</h4>
                <p><strong>Purpose:</strong> Score, rank, and compare houses using your criteria</p>
                <p><strong>When to use:</strong> After profiling, to see scored houses</p>
                <p><em>AI-powered house scoring with real-time adjustments</em></p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            if st.button("🚀 Launch Ranking", key="ranking_launch"):
                success, message = hub.launch_tool(ranking_file, 8503)
                if success:
                    st.success(f"✅ {message}")
                else:
                    st.error(f"❌ {message}")
    else:
        st.error("❌ dynamic_dashboard.py not found")
    
    st.markdown("---")
    
    # Step 3: Data Collection & Analytics
    st.subheader("3️⃣ Data Collection & Analytics")
    st.markdown("*Gather house data and monitor your collection*")
    
    # Analytics Dashboard
    analytics_file = "zillow_data_analytics_dashboard.py"
    collector_file = "comprehensive_data_collector.py"
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("##### 📊 Analytics Dashboard")
        if os.path.exists(analytics_file):
            st.markdown(f"""
            <div class="tool-card status-good">
                <h4>✅ Data Analytics</h4>
                <p>Monitor your data collection with maps and metrics</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("📊 View Analytics", key="analytics_launch"):
                success, message = hub.launch_tool(analytics_file, 8502)
                if success:
                    st.success(f"✅ {message}")
                else:
                    st.error(f"❌ {message}")
        else:
            st.error("❌ zillow_data_analytics_dashboard.py not found")
    
    with col2:
        st.markdown("##### 🔄 Data Collection")
        if os.path.exists(collector_file):
            st.markdown(f"""
            <div class="tool-card status-good">
                <h4>✅ Data Collector</h4>
                <p>Bulk collection of house data from Zillow</p>
            </div>
            """, unsafe_allow_html=True)
            
            api_key = os.getenv('RAPIDAPI_KEY')
            if api_key:
                if st.button("🚀 Run Collector", key="collector_launch"):
                    success, message = hub.launch_tool(collector_file, None)
                    if success:
                        st.success(f"✅ {message}")
                    else:
                        st.error(f"❌ {message}")
                st.caption(f"API Key: {api_key[:8]}...")
            else:
                st.error("❌ No RAPIDAPI_KEY in .env file")
        else:
            st.error("❌ comprehensive_data_collector.py not found")

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
            else:
                st.success("✅ Data is fresh")

def main():
    """Main command center application"""
    
    # Initialize the hub
    hub = HouseHuntingHub()
    
    # Display header
    display_header()
    
    # Main content in tabs
    tab1, tab2, tab3 = st.tabs(["🔧 Status", "📊 Data", "🛠️ Workflow"])
    
    with tab1:
        display_system_status(hub)
    
    with tab2:
        display_data_overview(hub)
    
    with tab3:
        display_workflow_tools(hub)
    
    # Sidebar with quick launch
    with st.sidebar:
        st.header("📋 Quick Launch")
        
        # Priority tools in workflow order
        priority_tools = [
            ("seamless_integrated_profiler.py", "1️⃣ Profiler", 8504),
            ("dynamic_dashboard.py", "2️⃣ Ranking", 8503),
            ("zillow_data_analytics_dashboard.py", "📊 Analytics", 8502),
            ("comprehensive_data_collector.py", "🔄 Collector", None)
        ]
        
        for filename, label, port in priority_tools:
            if os.path.exists(filename):
                if st.button(label, key=f"sidebar_{filename}"):
                    success, message = hub.launch_tool(filename, port)
                    if success:
                        st.success("✅ Launched!")
                        if port:
                            st.caption(f"Port: {port}")
                    else:
                        st.error(f"❌ {message}")
            else:
                st.caption(f"❌ {filename} missing")
        
        st.markdown("---")
        
        # Workflow status
        st.subheader("📊 Workflow Status")
        
        workflow_files = [
            "seamless_integrated_profiler.py",
            "dynamic_dashboard.py",
            "zillow_data_analytics_dashboard.py", 
            "comprehensive_data_collector.py"
        ]
        
        ready_count = sum(1 for f in workflow_files if os.path.exists(f))
        st.metric("Tools Ready", f"{ready_count}/4")
        
        if ready_count == 4:
            st.success("🎉 Complete setup!")
        elif ready_count >= 2:
            st.info("📈 Partially ready")
        else:
            st.warning("⚠️ Setup needed")
        
        # Quick status indicators
        for f in workflow_files:
            exists = os.path.exists(f)
            status = "✅" if exists else "❌"
            short_name = f.replace("_", " ").replace(".py", "").title()
            st.caption(f"{status} {short_name}")

if __name__ == "__main__":
    main()