#------------------------------------------------------------------------------------------------------------------------------------------------------
#''' Library Imports '''
import numpy as np
import pandas as pd
import os
pd.options.display.max_columns = None
from datetime import datetime

import streamlit as st
# import extra_streamlit_components as stx
import lib_getaround_viz as viz
import lib_getaround_models as mdl
#------------------------------------------------------------------------------------------------------------------------------------------------------
#''' Data Imports & Loads'''
path_data_delay = './data/get_around_delay_analysis.xlsx'
path_data_delay_updated = './data/get_around_delay_analysis_updated.csv'
path_data_pricing = './data/get_around_pricing_project.csv'
def fetch_data(path, ext):
    # Fetch data from URL here, and then clean it up.
    if ext == 'xls':
        data = pd.read_excel(path)
    elif ext == 'csv':
        data = pd.read_csv(path, encoding='latin-1')
    return data
if os.path.exists(path_data_delay_updated): 
    df_eda = fetch_data(path_data_delay_updated, 'csv')
else:
    data_delay = fetch_data(path_data_delay, 'xls')
    df_eda = viz.update_data(data_delay).copy()        # for eda data viz
# df_churn = data_viz.copy()      # for churn feature analysis
# data_imported = fetch_data(path_dataset_kept)
# df_model = data_imported.copy()
#------------------------------------------------------------------------------------------------------------------------------------------------------
#''' Streamlit app '''
# Page Configuration
st.set_page_config(
    page_title="Getaround Dashboard",  # Sets the browser tab title
    page_icon="🚗",               # Sets the favicon (supports emojis, paths, or URLs)
    layout="wide",             # Options: "centered" (default) or "wide"
    initial_sidebar_state="expanded",  # Options: "auto", "expanded", "collapsed"
    menu_items={
        'Get Help': 'https://www.example.com/help',
        'Report a bug': 'https://www.example.com/bug',
        'About': "# This is a Streamlit app for deley threshold analysis"
    }
)
#------------------------------------------------------------------------------------------------------------------------------------------------------
# Top Section: Project Introduction
st.title("Getaround Delay Threshold Analysis and Rental Pricing Prediction", anchor='project')
multi = """
    This project aims to look into 
    1) the `threshold implementation` of a minimum delay between two rentals with descriptive analytics and 
    2) the `pricing optimization` of daily car rental using predictive analytics.
    
    Provided delay data (21310 lines) and pricing data (4843 lines) were used.\n
    The following dashboard has two objectives :
    1) provide insights which lead to better understanding and interpretation of suitable delay thresholds by scope (mobile, connect), and
    2) determine and predict optimal car rental pricing via the introduction of an API
    
    Thus helping stakeholders make better informed data-driven decisions on optimal delay thresholds and car rental pricings.
"""
st.markdown(multi)
# Section Break
st.markdown("---")
#------------------------------------------------------------------------------------------------------------------------------------------------------

# # Middle Section: Descriptive Analytics
# st.header("Descriptive Analytics", anchor='descriptive')
# # Row 1: Filtered Membership Data with Checkbox Filters (Horizontal Layout)
# st.subheader("Exploratory Data Analysis of Delay Data", anchor='eda')
# col1, col2 = st.columns([1, 9])  # Narrow col1 for the checkbox filters

# with col1:
#     for i in range(0):
#         st.write("") # if we need to move wording down
#     # Dropdown for feature selection
#     viz_feature = st.selectbox(
#         "Select feature to display breakdown and figure",
#         options = viz.get_eda_features()
#     )
    
# with col2:
#     # Horizontal checkboxes for membership filter
#     st.write("Select Membership Status")
#     checkbox_cols = st.columns(3)
#     opt_all = checkbox_cols[0].checkbox("Full Population", value=True)
#     opt_member = checkbox_cols[1].checkbox("Society Member", value=False)
#     opt_non_member = checkbox_cols[2].checkbox("Not Society Member", value=False)
       
#     # Filter data based on selected checkboxes 
#     if opt_all or opt_member or opt_non_member:
#         if opt_all:
#             data_filtered = viz.fetch_eda_breakdown('all', viz_feature, df_eda, col1)
#             figs_all = viz.display_eda_figure('all', viz_feature, df_eda, checkbox_cols[0])
#         if opt_member:
#             data_filtered = viz.fetch_eda_breakdown('member', viz_feature, df_eda, col1)
#             figs_member = viz.display_eda_figure('member', viz_feature, df_eda, checkbox_cols[1])
#         if opt_non_member:
#             data_filtered = viz.fetch_eda_breakdown('non-member', viz_feature, df_eda, col1)
#             figs_non_member = viz.display_eda_figure('non-member', viz_feature, df_eda, checkbox_cols[2])
#     else:
#         data_filtered = viz.fetch_eda_breakdown('none', viz_feature, df_eda, col1)   
#         # figs_none = viz.display_eda_figure('none', viz_feature, df_viz)

# # Section Break
# st.markdown("---")

#------------------------------------------------------------------------------------------------------------------------------------------------------
# Middle Section: Descriptive Analytics
st.header("Descriptive Analytics", anchor='descriptive')
# Row 1: Filtered Membership Data with Checkbox Filters (Horizontal Layout)
st.subheader("Exploratory Data Analysis of Delay Data", anchor='eda')

lst_eda_tabs = [' ', 'Impacted Revenue Scope', 'Affected Rentals', 'Late Impact', 'Solved Cases']
eda_tabs = st.tabs(lst_eda_tabs)

for i, tab_name in enumerate(lst_eda_tabs):
    viz.display_eda_figures(i, tab_name, df_eda, eda_tabs[i])

# Section Break
st.markdown("---")
# #------------------------------------------------------------------------------------------------------------------------------------------------------
# # Bottom Section: Predictive Analytics
# st.header("Predictive Analytics", anchor='predictive')
# # Tabs for Model Selection (Logistic Regression, Random Forest)
# lst_model_tabs = ["Logistic Regression", "Random Forest"]
# # # Initialize session state to store the active tab index
# # if "active_tab" not in st.session_state: st.session_state.active_tab = 0  # Default to the first tab
# model_tabs = st.tabs(lst_model_tabs)
# # chosen_id = stx.tab_bar(data=[
# #     stx.TabBarItemData(id="tab1", title="✍️ To Do", description="Tasks to take care of"),
# #     stx.TabBarItemData(id="tab2", title="📣 Done", description="Tasks taken care of"),])

# for model, i in zip( lst_model_tabs, range(len(lst_model_tabs)) ):
#     model_choice = mdl.display_model_stats(model, df_model, model_tabs[i])  
    
#------------------------------------------------------------------------------------------------------------------------------------------------------
### Side bar 
# st.sidebar.title("Navigation")
st.sidebar.header("Navigation Pane", anchor = '')
st.sidebar.markdown("""
    * [Project](#project)
    * [Descriptive Analytics](#descriptive)
        * [EDA](#eda)
    * [Predictive Analytics](#predictive)   
        * [Models](#rfr)
        * [Predict Optimal Pricing](#predict_pricing)
    * [Reset]()

""")
e = st.sidebar.empty()
e.write("")
st.sidebar.write("Brought to you by [Eric Thien, CFA](https://www.linkedin.com/in/eric-thien-cfa-9b96211/)")
#------------------------------------------------------------------------------------------------------------------------------------------------------