import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sys
import os

# Add backend modules to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import backend modules
from tourism_backend_engine import TourismBackendEngine, TouristProfile
from pdf_generator import PDFItineraryGenerator
from chatbot_integration import TravelChatbot

# Page configuration
st.set_page_config(
    page_title="AI Travel Planner",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Gemini API key (demo key provided for integration)
GEMINI_API_KEY = "AIzaSyCXdWiGQrnA5SqgQjM12xwfwR7zOMoRKqc"

# Initialize session state
if 'backend_engine' not in st.session_state:
    st.session_state.backend_engine = None
if 'chatbot' not in st.session_state:
    st.session_state.chatbot = None
if 'generated_itinerary' not in st.session_state:
    st.session_state.generated_itinerary = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Load backend engine (cached)
@st.cache_resource
def load_backend_engine(dataset_path):
    """Load and cache backend engine"""
    return TourismBackendEngine(dataset_path)

@st.cache_resource
def load_chatbot(_engine):
    """Load and cache chatbot"""
    return TravelChatbot(_engine)
    return TravelChatbot(_engine, api_key=GEMINI_API_KEY)

# Main app
def main():
    # Sidebar navigation
    st.sidebar.title("🌍 AI Travel Planner")
    st.sidebar.markdown("---")
    
    page = st.sidebar.radio(
        "Navigate to:",
        ["🏠 Home", "✈️ Plan Your Trip", "💡 Recommendations", 
         "💬 Travel Assistant", "📊 Analytics", "ℹ️ About"],
        label_visibility="collapsed"
    )
    
    st.sidebar.markdown("---")
    
    # Initialize backend
    try:
        if st.session_state.backend_engine is None:
            with st.spinner("Loading AI backend..."):
                st.session_state.backend_engine = load_backend_engine(
                    'master_tourism_dataset_v2_enhanced.csv'
                )
                st.session_state.chatbot = load_chatbot(st.session_state.backend_engine)
            st.sidebar.success("✅ Backend loaded!")
@@ -232,92 +235,99 @@ def show_itinerary_page(engine):
    # Input form
    with st.form("itinerary_form"):
        st.subheader("👤 About You")
        
        col1, col2 = st.columns(2)
        
        with col1:
            age = st.slider("Your Age", 18, 80, 30)
            
            interests = st.multiselect(
                "Your Interests (select multiple)",
                ['Art', 'History', 'Architecture', 'Cultural', 'Nature'],
                default=['Art', 'History']
            )
        
        with col2:
            duration = st.slider("Trip Duration (days)", 1, 14, 7)
            
            budget = st.selectbox(
                "Budget Preference",
                ['Mid-range', 'Luxury'],
                index=0
            )
        
        col3, col4 = st.columns(2)
        

        with col3:
            climate = st.selectbox(
                "Climate Preference",
                ['Any', 'Temperate'],
                ['Any', 'Cold', 'Temperate', 'Warm'],
                index=0
            )
        

        with col4:
            accessibility = st.checkbox("I need wheelchair accessibility")
            season = st.selectbox(
                "Season Preference",
                ['Any', 'Spring', 'Summer', 'Autumn', 'Winter'],
                index=0
            )

        accessibility = st.checkbox("I need wheelchair accessibility")
        
        st.write("")
        
        start_date = st.date_input(
            "Preferred Start Date",
            value=datetime.now() + timedelta(days=30),
            min_value=datetime.now()
        )
        
        st.write("")
        
        submitted = st.form_submit_button(
            "🎯 Generate My Itinerary",
            type="primary",
            use_container_width=True
        )
    
    # Generate itinerary
    if submitted:
        if not interests:
            st.error("⚠️ Please select at least one interest!")
            return
        
        with st.spinner("🤖 AI is creating your perfect itinerary..."):
            try:
                profile = TouristProfile(
                    age=age,
                    interests=interests,
                    accessibility_needs=accessibility,
                    preferred_duration=duration,
                    budget_preference=budget,
                    climate_preference=None if climate == 'Any' else climate
                    climate_preference=None if climate == 'Any' else climate,
                    season_preference=None if season == 'Any' else season
                )
                
                itinerary = engine.generate_itinerary(
                    tourist_profile=profile,
                    start_date=datetime.combine(start_date, datetime.min.time())
                )
                
                st.session_state.generated_itinerary = itinerary
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                return
        
        st.success("✅ Your personalized itinerary is ready!")
    
    # Display itinerary
    if st.session_state.generated_itinerary:
        display_itinerary(st.session_state.generated_itinerary, engine)

def display_itinerary(itinerary, engine):
    """Display generated itinerary"""
    
    if itinerary['status'] != 'success':
        st.error(itinerary.get('message', 'Failed to generate itinerary'))
        return
