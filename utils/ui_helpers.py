"""
UI Helper Functions and Styling for SPARTAN
"""

import streamlit as st
from config.settings import SPARTAN_THEME, COST_MODE_INFO, COST_PER_ITEM


def apply_spartan_theme():
    """Apply the SPARTAN theme CSS"""
    st.markdown(f"""
    <style>
        /* Main theme colors */
        :root {{
            --spartan-purple: {SPARTAN_THEME["purple"]};
            --spartan-pink: {SPARTAN_THEME["pink"]};
            --spartan-black: {SPARTAN_THEME["black"]};
            --spartan-white: {SPARTAN_THEME["white"]};
        }}
        
        /* Header styling */
        .main-header {{
            background: linear-gradient(135deg, var(--spartan-purple), var(--spartan-pink));
            padding: 2rem;
            border-radius: 10px;
            margin-bottom: 2rem;
            text-align: center;
            box-shadow: 0 4px 6px -1px rgba(139, 92, 246, 0.1);
        }}
        
        .main-header h1 {{
            color: var(--spartan-white);
            font-size: 3rem;
            font-weight: 800;
            margin: 0;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            letter-spacing: 3px;
        }}
        
        .main-header p {{
            color: var(--spartan-white);
            font-size: 1.1rem;
            margin: 0.5rem 0 0 0;
            opacity: 0.9;
        }}
        
        /* Section headers */
        .section-header {{
            background: var(--spartan-black);
            color: var(--spartan-white);
            padding: 1rem;
            border-radius: 8px;
            margin-bottom: 1rem;
            border-left: 4px solid var(--spartan-purple);
        }}
        
        /* Metric cards */
        .stMetric {{
            background: var(--spartan-white);
            border: 2px solid var(--spartan-purple);
            border-radius: 8px;
            padding: 1rem;
        }}
        
        /* Success/error styling */
        .stSuccess {{
            background-color: rgba(139, 92, 246, 0.1);
            border-left: 4px solid var(--spartan-purple);
        }}
        
        .stError {{
            background-color: rgba(236, 72, 153, 0.1);
            border-left: 4px solid var(--spartan-pink);
        }}
        
        .stWarning {{
            background-color: rgba(139, 92, 246, 0.05);
            border-left: 4px solid var(--spartan-purple);
        }}
        
        /* Buttons */
        .stButton > button {{
            background: linear-gradient(135deg, var(--spartan-purple), var(--spartan-pink));
            color: var(--spartan-white);
            border: none;
            border-radius: 8px;
            font-weight: 600;
            transition: all 0.3s;
        }}
        
        .stButton > button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(139, 92, 246, 0.4);
        }}
        
        /* Progress bar */
        .stProgress > div > div > div {{
            background: linear-gradient(135deg, var(--spartan-purple), var(--spartan-pink));
        }}
        
        /* Expandable sections */
        .streamlit-expanderHeader {{
            background-color: var(--spartan-black);
            color: var(--spartan-white);
            border-radius: 5px;
        }}
    </style>
    """, unsafe_allow_html=True)


def render_spartan_header():
    """Render the main SPARTAN header"""
    st.markdown("""
    <div class="main-header">
        <h1>  </h1>
        <p>Item Placement & Classification System</p>
    </div>
    """, unsafe_allow_html=True)


def render_section_header(title: str):
    """Render a section header with SPARTAN styling"""
    st.markdown(f'<div class="section-header"><h3>{title}</h3></div>', unsafe_allow_html=True)


def display_cost_info(cost_mode: str):
    """Display cost optimization information"""
    icon, description = COST_MODE_INFO[cost_mode]
    st.info(f"{icon} {description}")


def calculate_estimated_cost(cost_mode: str, num_items: int) -> float:
    """Calculate estimated processing cost"""
    cost_per_item = COST_PER_ITEM[cost_mode]
    return num_items * cost_per_item


def format_model_name(model_id: str) -> str:
    """Format model ID into a readable name"""
    if not model_id:
        return "Unknown Model"
    
    model_name = model_id.split('.')[-1]
    model_name = model_name.replace('-', ' ').title()
    model_name = model_name.replace('V1', 'v1').replace('V2', 'v2')
    
    return model_name


def display_file_validation_status(df, required_cols: list, optional_cols: list):
    """Display file validation status with appropriate styling"""
    missing_required = [col for col in required_cols if col not in df.columns]
    available_optional = [col for col in optional_cols if col in df.columns]
    
    if missing_required:
        st.error(f"Missing required columns: {', '.join(missing_required)}")
        return False
    else:
        st.info("Format validated")
        if available_optional:
            st.info(f"Extra columns: {', '.join(available_optional)}")
        return True


def display_processing_metrics(results_df):
    """Display clean processing metrics"""
    total = len(results_df)
    lookups = len(results_df[results_df['online_lookup_found'] == True])
    references = len(results_df[results_df['reference_match_found'] == True])
    successful = len(results_df[~results_df['mch_levels'].str.contains('ERROR|UNCERTAIN')])
    errors = len(results_df[results_df['mch_levels'].str.contains('ERROR')])
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("**Processed**", total)
    with col2:
        st.metric("**Lookups**", lookups, f"{lookups/total*100:.0f}%" if total > 0 else "0%")
    with col3:
        st.metric("**References**", references, f"{references/total*100:.0f}%" if total > 0 else "0%")
    with col4:
        st.metric("**Success**", successful, f"{successful/total*100:.0f}%" if total > 0 else "0%")
    with col5:
        st.metric("**Errors**", errors, f"-{(1-errors/total)*100:.0f}%" if errors > 0 and total > 0 else "0%")
    
    return {
        'total': total,
        'lookups': lookups,
        'references': references,
        'successful': successful,
        'errors': errors
    }


def create_results_expandables(results_df, metrics):
    """Create expandable sections for detailed results analysis"""
    
    # Barcode Lookups
    if metrics['lookups'] > 0:
        with st.expander(f"**Barcode Lookups** ({metrics['lookups']} items)"):
            lookup_items = results_df[results_df['online_lookup_found'] == True]
            st.dataframe(lookup_items[['original_description', 'lookup_product_name', 'mch_levels', 'confidence_score']])
    
    # Reference Matches
    if metrics['references'] > 0:
        with st.expander(f"**Reference Matches** ({metrics['references']} items)"):
            ref_items = results_df[results_df['reference_match_found'] == True]
            st.dataframe(ref_items[['original_description', 'mch_levels', 'confidence_score']])
    
    # Errors
    if metrics['errors'] > 0:
        with st.expander(f"**Errors** ({metrics['errors']} items)"):
            error_items = results_df[results_df['mch_levels'].str.contains('ERROR')]
            st.dataframe(error_items[['original_description', 'mch_levels', 'reasoning']])


def render_file_upload_section(title: str, key: str, help_text: str = ""):
    """Render a standardized file upload section"""
    st.markdown(f"**{title}**")
    uploaded_file = st.file_uploader(
        help_text or f"Upload {title.lower()}",
        type=['csv', 'xlsx'],
        key=key,
        label_visibility="collapsed"
    )
    return uploaded_file
