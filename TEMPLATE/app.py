#!/usr/bin/env python3
"""
🎯 PyMapGIS Showcase Demo Template

This template provides a starting point for creating new PyMapGIS showcase demos.
Replace this content with your specific demo implementation.

Author: Your Name
Created: 2025-06-15
"""

import streamlit as st
import pymapgis as pmg
import plotly.express as px
import pandas as pd
from typing import Optional


def load_sample_data() -> pd.DataFrame:
    """
    Load sample geospatial data for the demo.
    
    Replace this with your specific data loading logic.
    
    Returns:
        pd.DataFrame: Sample geospatial data
    """
    try:
        # Example: Load Census ACS data
        data = pmg.read("census://acs/acs5?year=2022&geography=county&variables=B01003_001E")
        return data
    except Exception as e:
        st.error(f"Error loading data: {e}")
        # Return sample data as fallback
        return pd.DataFrame({
            'NAME': ['Sample County 1', 'Sample County 2'],
            'B01003_001E': [50000, 75000],
            'geometry': [None, None]  # Add actual geometry in real implementation
        })


def create_visualization(data: pd.DataFrame) -> Optional[object]:
    """
    Create the main visualization for the demo.
    
    Args:
        data: Processed geospatial data
        
    Returns:
        Plotly figure or other visualization object
    """
    try:
        if hasattr(data, 'plot'):
            # Use PyMapGIS plotting capabilities
            fig = data.plot.choropleth(
                column="B01003_001E",
                title="Population by County (2022)",
                color_continuous_scale="Viridis"
            )
        else:
            # Fallback to basic Plotly
            fig = px.bar(
                data, 
                x='NAME', 
                y='B01003_001E',
                title="Sample Data Visualization"
            )
        return fig
    except Exception as e:
        st.error(f"Error creating visualization: {e}")
        return None


def main():
    """
    Main demo application.
    
    This function sets up the Streamlit interface and orchestrates the demo.
    """
    # Page configuration
    st.set_page_config(
        page_title="PyMapGIS Demo Template",
        page_icon="🎯",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Header
    st.title("🎯 PyMapGIS Showcase Demo Template")
    st.markdown("""
    **Welcome to the PyMapGIS Demo Template!** 
    
    This template demonstrates how to create interactive geospatial applications using PyMapGIS.
    Replace this content with your specific demo implementation.
    """)
    
    # Sidebar controls
    st.sidebar.header("🛠️ Demo Controls")
    st.sidebar.markdown("Add your demo controls here:")
    
    # Example controls (replace with your specific controls)
    show_data = st.sidebar.checkbox("Show Raw Data", value=False)
    data_source = st.sidebar.selectbox(
        "Data Source",
        ["Census ACS", "Sample Data", "Custom Upload"]
    )
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📊 Visualization")
        
        # Load and process data
        with st.spinner("Loading data..."):
            data = load_sample_data()
        
        # Create and display visualization
        if data is not None and not data.empty:
            fig = create_visualization(data)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.error("Could not create visualization")
        else:
            st.error("No data available")
    
    with col2:
        st.subheader("ℹ️ Demo Information")
        st.markdown("""
        **About This Demo:**
        - Replace with your demo description
        - Explain the use case and value
        - Highlight PyMapGIS features used
        
        **Data Sources:**
        - List your data sources here
        - Include attribution as needed
        
        **Technologies:**
        - PyMapGIS
        - Streamlit
        - Plotly
        - Add others as needed
        """)
        
        # Display metrics or summary statistics
        if data is not None and not data.empty:
            st.subheader("📈 Summary Statistics")
            st.metric("Total Records", len(data))
            if 'B01003_001E' in data.columns:
                st.metric("Total Population", f"{data['B01003_001E'].sum():,}")
    
    # Optional: Show raw data
    if show_data and data is not None:
        st.subheader("📋 Raw Data")
        st.dataframe(data)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    **🚀 Built with PyMapGIS** | 
    [📖 Documentation](https://github.com/pymapgis/core) | 
    [🐛 Report Issues](https://github.com/pymapgis/core/issues) |
    [🤝 Contribute](https://github.com/pymapgis/core/blob/main/CONTRIBUTING.md)
    """)


if __name__ == "__main__":
    main()
