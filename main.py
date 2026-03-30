"""
SPARTAN - Main Application
AI-Powered Item Placement & Classification System
"""

import streamlit as st
import pandas as pd
import time
from datetime import datetime

# SPARTAN imports
from config.settings import AWS_REGIONS, REQUIRED_COLUMNS, OPTIONAL_COLUMNS
from core.ai_assistant import ItemPlacementAI
from core.barcode_lookup import BarcodeProductLookup
from utils.aws_utils import test_bedrock_connection, get_model_display_name
from utils.ui_helpers import (
    apply_spartan_theme, render_spartan_header, render_section_header,
    display_cost_info, calculate_estimated_cost, display_file_validation_status,
    display_processing_metrics, create_results_expandables, render_file_upload_section
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


def render_file_upload_sections():
    """Render the file upload sections"""
    render_section_header("📁 File Upload")
    
    col1, col2, col3 = st.columns(3)
    
    bible_file = None
    reference_file = None
    items_file = None
    
    # Bible upload
    with col1:
        bible_file = render_file_upload_section("1. MCH Bible", "bible", "Upload MCH Levels")
        
        if bible_file:
            try:
                bible_df = load_file_data(bible_file)
                st.session_state.bible_df = bible_df
                st.success(f"✅ **{len(bible_df)} levels loaded**")
                with st.expander("Preview"):
                    st.dataframe(bible_df.head(3), height=120)
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    # Reference upload  
    with col2:
        reference_file = render_file_upload_section("2. Reference Data", "reference", "Upload Reference File")
        
        if reference_file:
            try:
                reference_df = load_file_data(reference_file)
                st.session_state.reference_df = reference_df
                st.success(f"✅ **{len(reference_df)} items loaded**")
                
                if display_file_validation_status(reference_df, REQUIRED_COLUMNS, OPTIONAL_COLUMNS):
                    with st.expander("Preview"):
                        st.dataframe(reference_df.head(3), height=120)
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    # Items upload
    with col3:
        items_file = render_file_upload_section("3. Items to Process", "items", "Upload Items")
        
        if items_file:
            try:
                items_df = load_file_data(items_file)
                st.session_state.items_df = items_df
                st.success(f"✅ **{len(items_df)} items loaded**")
                
                if display_file_validation_status(items_df, REQUIRED_COLUMNS, OPTIONAL_COLUMNS):
                    with st.expander("Preview"):
                        st.dataframe(items_df.head(3), height=120)
            except Exception as e:
                st.error(f"Error: {str(e)}")
                st.session_state.items_df = None
    
    return bible_file, reference_file, items_file


def render_processing_section(cost_mode, selected_region):
    """Render the processing section"""
    # Check if all files are loaded
    bible_df = st.session_state.get('bible_df')
    reference_df = st.session_state.get('reference_df')
    items_df = st.session_state.get('items_df')
    working_model = st.session_state.get('working_model')
    
    if not all([bible_df is not None, reference_df is not None, items_df is not None, working_model]):
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
        ai_assistant.load_reference_file(reference_df)
        
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
    
    # Render barcode test
    render_barcode_test_section()
    
    # Render sidebar and get settings
    cost_mode, selected_region = render_sidebar()
    
    # Render file upload sections
    render_file_upload_sections()
    
    # Render processing section
    render_processing_section(cost_mode, selected_region)


if __name__ == "__main__":
    main()