"""
SPARTAN - Main Application (Simplified Version)
AI-Powered Item Placement & Classification System
"""

import streamlit as st
import pandas as pd
import time
import os
from datetime import datetime
from pathlib import Path

# SPARTAN imports
from config.settings import AWS_REGIONS, REQUIRED_COLUMNS, OPTIONAL_COLUMNS
from core.ai_assistant import ItemPlacementAI
from core.barcode_lookup import BarcodeProductLookup
from utils.aws_utils import test_bedrock_connection, get_model_display_name
from utils.ui_helpers import (
    apply_spartan_theme, render_spartan_header, render_section_header,
    display_cost_info, calculate_estimated_cost, display_file_validation_status,
    display_processing_metrics, create_results_expandables
)

# Page configuration
st.set_page_config(
    page_title="SPARtan - AI Item Placement",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply theme
apply_spartan_theme()


def get_data_directory():
    """Get the data directory path"""
    # Check if running from current directory
    if os.path.exists("data"):
        return "data"
    # Check if in parent directory (for different deployment scenarios)
    elif os.path.exists("../data"):
        return "../data"
    # Default to current directory
    return "data"


def load_hardcoded_data():
    """Load MCH Bible and Reference Data from hardcoded files"""
    data_dir = get_data_directory()
    
    bible_df = None
    reference_df = None
    
    # Load MCH Bible
    bible_path = os.path.join(data_dir, "mch_bible.csv")
    if os.path.exists(bible_path):
        try:
            bible_df = pd.read_csv(bible_path)
            st.session_state.bible_df = bible_df
        except Exception as e:
            st.error(f"Error loading MCH Bible: {str(e)}")
    
    # Load Reference Data
    reference_path = os.path.join(data_dir, "reference_data.csv")
    if os.path.exists(reference_path):
        try:
            reference_df = pd.read_csv(reference_path)
            st.session_state.reference_df = reference_df
        except Exception as e:
            st.warning(f"Could not load reference data: {str(e)}")
            # Continue without reference data
            st.session_state.reference_df = None
    
    return bible_df, reference_df


def render_barcode_test_section():
    """Render barcode lookup test section"""
    with st.expander("🔍 **Barcode Lookup Test**", expanded=False):
        col1, col2 = st.columns([3, 1])
        with col1:
            test_barcode = st.text_input(
                "Test a barcode:", 
                placeholder="e.g., 9780142000052", 
                label_visibility="collapsed"
            )
        with col2:
            test_lookup = st.button("**Test**", key="test_barcode")
        
        if test_lookup and test_barcode:
            with st.spinner("Looking up..."):
                lookup = BarcodeProductLookup()
                result = lookup.lookup_barcode(test_barcode)
                if result["found"]:
                    st.success(f"✅ **Found:** {result.get('title', 'Unknown Product')}")
                    st.json(result)
                else:
                    st.warning("❌ Product not found in databases")


def render_sidebar():
    """Render the sidebar configuration"""
    with st.sidebar:
        render_section_header("⚙️ Configuration")
        
        # Cost optimization
        cost_mode = st.selectbox(
            "**Optimization Mode**",
            ["budget", "balanced", "performance"],
            index=1,
            help="Budget: ~$0.45/1000 items | Performance: ~$5.40/1000 items"
        )
        
        display_cost_info(cost_mode)
        
        # AWS Region
        selected_region = st.selectbox("**AWS Region**", AWS_REGIONS)
        
        # Connection test
        if st.button("🔗 **Test Connection**", type="primary"):
            with st.spinner("Testing..."):
                connection_ok, working_model = test_bedrock_connection(selected_region)
                if working_model:
                    st.session_state.working_model = working_model
        
        # Display connection status
        if st.session_state.get('working_model'):
            model_name = get_model_display_name(st.session_state.working_model)
            st.success(f"✅ **Connected:** {model_name}")
        else:
            st.info("Test connection to continue")
    
    return cost_mode, selected_region


def load_file_data(uploaded_file):
    """Load data from uploaded file"""
    if uploaded_file.name.endswith('.csv'):
        return pd.read_csv(uploaded_file)
    else:
        return pd.read_excel(uploaded_file)


def render_data_status_section():
    """Render status of hardcoded data"""
    render_section_header("📊 Data Status")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📚 MCH Bible**")
        bible_df = st.session_state.get('bible_df')
        if bible_df is not None:
            st.success(f"✅ **{len(bible_df)} MCH levels loaded**")
            with st.expander("Preview MCH Bible"):
                st.dataframe(bible_df.head(10), height=200)
        else:
            st.error("❌ MCH Bible not loaded")
    
    with col2:
        st.markdown("**📖 Reference Database**")
        reference_df = st.session_state.get('reference_df')
        if reference_df is not None:
            st.success(f"✅ **{len(reference_df)} reference items loaded**")
            with st.expander("Preview Reference Data"):
                st.dataframe(reference_df.head(10), height=200)
        else:
            st.info("ℹ️ No reference data (will use AI only)")


def render_file_upload_section():
    """Render the simplified file upload section"""
    render_section_header("📁 Upload Items to Process")
    
    st.markdown("""
    Upload a CSV or Excel file with items to classify. 
    
    **Required column:** `description`  
    **Optional columns:** `manufacturer`, `barcode`, `barcode_number`, `ean`, `upc`
    """)
    
    items_file = st.file_uploader(
        "Choose your file",
        type=['csv', 'xlsx'],
        key="items_upload",
        help="Upload CSV or Excel file with items to classify"
    )
    
    if items_file:
        try:
            items_df = load_file_data(items_file)
            st.session_state.items_df = items_df
            
            # Validate file
            if display_file_validation_status(items_df, REQUIRED_COLUMNS, OPTIONAL_COLUMNS):
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.success(f"✅ **{len(items_df)} items loaded and validated**")
                with col2:
                    if st.button("📋 Preview Data"):
                        st.session_state.show_preview = True
                
                if st.session_state.get('show_preview', False):
                    with st.expander("📊 Data Preview", expanded=True):
                        st.dataframe(items_df.head(10), height=250)
                        if st.button("Hide Preview"):
                            st.session_state.show_preview = False
        except Exception as e:
            st.error(f"Error loading file: {str(e)}")
            st.session_state.items_df = None
    else:
        st.session_state.items_df = None


def render_processing_section(cost_mode, selected_region):
    """Render the processing section"""
    # Check if all required data is loaded
    bible_df = st.session_state.get('bible_df')
    items_df = st.session_state.get('items_df')
    working_model = st.session_state.get('working_model')
    
    # Reference data is optional
    reference_df = st.session_state.get('reference_df')
    
    if not all([bible_df is not None, items_df is not None, working_model]):
        if bible_df is None:
            st.warning("⚠️ MCH Bible data not loaded. Please check data directory.")
        if items_df is None:
            st.info("📤 Upload a file with items to process")
        if working_model is None:
            st.info("🔗 Test AWS connection in sidebar")
        return
    
    render_section_header("⚡ Processing")
    
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    with col1:
        process_button = st.button("🚀 **PROCESS ITEMS**", type="primary")
    with col2:
        max_items = st.number_input(
            "Max items", 
            1, 
            len(items_df), 
            min(25, len(items_df)), 
            label_visibility="collapsed"
        )
    with col3:
        st.metric("**Total**", len(items_df))
    with col4:
        estimated_cost = calculate_estimated_cost(cost_mode, max_items)
        st.metric("**Est. Cost**", f"${estimated_cost:.2f}")
    
    # Show reference data status
    if reference_df is not None:
        st.info(f"ℹ️ Using reference database with {len(reference_df)} items for improved accuracy")
    else:
        st.info("ℹ️ No reference data - using AI classification only")
    
    if process_button:
        process_items(bible_df, reference_df, items_df, max_items, cost_mode, selected_region, working_model)


def process_items(bible_df, reference_df, items_df, max_items, cost_mode, selected_region, working_model):
    """Process the items using SPARTAN AI"""
    try:
        # Initialize AI assistant
        ai_assistant = ItemPlacementAI(
            region_name=selected_region,
            model_id=working_model,
            cost_optimization=cost_mode
        )
        
        # Load data
        ai_assistant.load_bible(bible_df)
        
        # Load reference data only if available
        if reference_df is not None:
            ai_assistant.load_reference_file(reference_df)
            st.info("✅ Reference database loaded for enhanced matching")
        else:
            st.info("ℹ️ Processing without reference data - relying on AI analysis")
        
        # Prepare items subset
        items_subset = items_df.head(max_items)
        
        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        def update_progress(current, total):
            progress = current / total
            progress_bar.progress(progress)
            status_text.text(f"Processing {current}/{total}...")
        
        # Process items
        with st.spinner("SPARTAN AI analyzing items..."):
            start_time = time.time()
            results_df = ai_assistant.process_batch(items_subset, update_progress)
            processing_time = time.time() - start_time
        
        # Clear progress indicators
        status_text.empty()
        progress_bar.empty()
        
        # Display success message
        st.success(f"✅ **Processing completed in {processing_time:.1f}s**")
        
        # Display results
        render_results_section(results_df)
        
    except Exception as e:
        st.error(f"Failed to process items: {str(e)}")
        import traceback
        st.error(f"Details: {traceback.format_exc()}")


def render_results_section(results_df):
    """Render the results section"""
    render_section_header("📊 Results")
    
    # Display metrics
    metrics = display_processing_metrics(results_df)
    
    # Results table
    st.dataframe(results_df, height=400, use_container_width=True)
    
    # Download button
    csv = results_df.to_csv(index=False)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    st.download_button(
        "📥 **Download Results**",
        data=csv,
        file_name=f"spartan_results_{timestamp}.csv",
        mime="text/csv",
        type="primary"
    )
    
    # Analysis expandables
    create_results_expandables(results_df, metrics)


def main():
    """Main application function"""
    # Render header
    render_spartan_header()
    
    # Display app info
    st.markdown("""
    **Welcome to SPARTAN!** This AI-powered system automatically classifies retail items into appropriate MCH categories.
    Simply upload your items file and let the AI do the work! 🚀
    """)
    
    # Load hardcoded data
    if 'bible_df' not in st.session_state or 'reference_df' not in st.session_state:
        with st.spinner("Loading MCH Bible and Reference Data..."):
            bible_df, reference_df = load_hardcoded_data()
    
    # Render barcode test
    render_barcode_test_section()
    
    # Render sidebar and get settings
    cost_mode, selected_region = render_sidebar()
    
    # Show data status
    render_data_status_section()
    
    # Render file upload section
    render_file_upload_section()
    
    # Render processing section
    render_processing_section(cost_mode, selected_region)


if __name__ == "__main__":
    main()
