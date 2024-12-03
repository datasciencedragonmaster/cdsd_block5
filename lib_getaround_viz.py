#------------------------------------------------------------------------------------------------------------------------------------------------------
#''' Library Imports '''
import numpy as np
import pandas as pd
pd.options.display.max_columns = None
from datetime import datetime

import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objs as go
from plotly.subplots import make_subplots

import streamlit as st
#------------------------------------------------------------------------------------------------------------------------------------------------------
def update_data(delay_data):
    # Initialize the new column with NaN
    delay_data['next_rental_id'] = np.nan # None
    delay_data['delay_at_checkout_of_previous_transaction'] = np.nan # None
    delay_data['impacts_next_driver'] = None
    delay_data['delay_impact_in_minutes'] = np.nan
    # Iterate through each row to map the previous rental's delay to the current rental
    for idx, row in delay_data.iterrows():
        if not pd.isna(row['previous_ended_rental_id']):  # If there is a previous rental
            # Find the delay of the previous rental
            previous_rental_delay = delay_data.loc[
                delay_data['rental_id'] == row['previous_ended_rental_id'], 'delay_at_checkout_in_minutes']
            # print(previous_rental_delay.iloc[0])
            # Assign the delay value (if it exists) to the current row
            if not previous_rental_delay.empty:
                delay_data.at[idx, 'delay_at_checkout_of_previous_transaction'] = previous_rental_delay.iloc[0]
        
        next_rental_id = delay_data.loc[
            delay_data['previous_ended_rental_id'] == row['rental_id'], 'rental_id']           
        if not next_rental_id.empty:
            delay_data.at[idx, 'next_rental_id'] = (next_rental_id.iloc[0]).astype(np.int64)
    #--------------------------------------------------------------------------------------------------------------------------------------------
    for idx, row in delay_data.iterrows():    
        if not pd.isna(row['delay_at_checkout_of_previous_transaction']):  # If delay is not 0
            # print(f"Previous rental delay : {row['delay_at_checkout_of_previous_transaction']}")
            # print(f"Time between rentals : {row['time_delta_with_previous_rental_in_minutes']}")
            if row['delay_at_checkout_of_previous_transaction'] > row['time_delta_with_previous_rental_in_minutes']:
                delay_data.at[idx, 'impacts_next_driver'] = True
                delay_data.at[idx, 'delay_impact_in_minutes'] = (row['delay_at_checkout_of_previous_transaction'] - row['time_delta_with_previous_rental_in_minutes'])
            else: 
                delay_data.at[idx, 'impacts_next_driver'] = False
                delay_data.at[idx, 'delay_impact_in_minutes'] = np.nan
    #--------------------------------------------------------------------------------------------------------------------------------------------
    delay_data.to_csv('./data/get_around_delay_analysis_updated.csv')
    return delay_data
#------------------------------------------------------------------------------------------------------------------------------------------------------
# Plot eda figures with Plotly based on churn feature type
def display_eda_figures(i_feature, tab_name, delay_data, obj):
    figs = []; commentary1 = ''; commentary2 = ''; commentary3 = ''
    #--------------------------------------------------------------------------------------------------------------------------------------------
    state_ended = (delay_data['state'] == 'ended')
    state_canceled = (delay_data['state'] == 'canceled')
    type_mobile = (delay_data['checkin_type'] == 'mobile')
    type_connect = (delay_data['checkin_type'] == 'connect')
    no_time_delta = (delay_data['time_delta_with_previous_rental_in_minutes'].isna())       # next day rental
    with_time_delta = (delay_data['time_delta_with_previous_rental_in_minutes'].notna())    # same day rental
    nextday_ended = no_time_delta & state_ended
    nextday_canceled = no_time_delta & state_canceled
    sameday_ended = with_time_delta & state_ended
    sameday_canceled = with_time_delta & state_canceled
    sameday_mobile = with_time_delta & type_mobile
    sameday_connect = with_time_delta & type_connect
    sameday_ended_mobile = sameday_ended & type_mobile
    sameday_ended_connect = sameday_ended & type_connect
    #--------------------------------------------------------------------------------------------------------------------------------------------
    sameday_data = delay_data[with_time_delta].copy()
    data_sameday_mobile = delay_data[sameday_mobile].copy()
    data_sameday_connect = delay_data[sameday_connect].copy()
    time_delta_values = sorted(delay_data['time_delta_with_previous_rental_in_minutes'].unique())
    time_delta_range = [x for x in time_delta_values if not np.isnan(x)]
    impacted = ( delay_data['impacts_next_driver'] == True ) 
    scope_impacted_mobile = delay_data[impacted & type_mobile]
    scope_impacted_connect = delay_data[impacted & type_connect]
    #--------------------------------------------------------------------------------------------------------------------------------------------
    if tab_name == 'Impacted Revenue Scope':
        delay_data['day_booking_group'] = None
        delay_data.loc[no_time_delta, 'day_booking_group'] = 'Next day booking'
        delay_data.loc[with_time_delta, 'day_booking_group'] = 'Same day booking'
        color_map1 = { 'Next day booking': '#636EFA','Same day booking': '#EF553B',}
        fig1 = px.pie(delay_data, names='day_booking_group', title=f'Types of Rental Transactions (Same vs Next day bookings)',
                color='day_booking_group', color_discrete_map= color_map1,  # This maps the feature_impact_group column to the color scheme
                hole=0.3) 
        fig1.update_traces(textinfo='label+value+percent', rotation=30, textfont=dict(size=12))
        fig1.update_layout( 
            width=400, height=400, # Adjust height of the pie chart
            margin=dict(t=100, b=25, l=25, r=25),  title=dict(font=dict(size=16)), )
        commentary1 = "Majority (~92%) are next day bookings (with no time deltas) and will not be affected by the new feature (adding delay between rentals on same day bookings). \
                    \n\nOur examined scope will hence concern only same day bookings (~8%). "
        figs.append(fig1)
        #----------------------------------------------------------------------------------------------------------------------------------
        color_map2 = { 'ended': 'Green','canceled': 'Violet',}
        fig2 = px.pie(delay_data, names='state', title=f'Types of Rental Transactions (Ended vs Canceled bookings)',
                color='state', color_discrete_map= color_map2,  # This maps the feature_impact_group column to the color scheme
                hole=0.3) 
        fig2.update_traces(textinfo='label+value+percent', rotation=54, textfont=dict(size=12))
        fig2.update_layout( 
            width=400, height=400, # Adjust height of the pie chart
            margin=dict(t=100, b=25, l=25, r=25),  title=dict(font=dict(size=16)), )
        commentary2 = "A sizable portion of bookings (~15%) were canceled. \
                    \n\n Same day cancellations in our scope could be due to impact of late returns from previous rentals."
        figs.append(fig2)
        #----------------------------------------------------------------------------------------------------------------------------------
        color_map3 = { 'mobile': 'f70e37','connect': 'orange',}
        fig3 = px.pie(delay_data, names='checkin_type', title=f'Types of Rental Transactions (Mobile vs Connect bookings)',
                color='checkin_type', color_discrete_map= color_map3,  # This maps the feature_impact_group column to the color scheme
                hole=0.3) 
        fig3.update_traces(textinfo='label+value+percent', rotation=73, textfont=dict(size=12))
        fig3.update_layout( 
            width=600, height=600, # Adjust height of the pie chart
            margin=dict(t=300, b=25, l=25, r=25),  title=dict(font=dict(size=16)), )
        commentary3 = "Most transactions are mobile (~80%)."
        figs.append(fig3)
        #----------------------------------------------------------------------------------------------------------------------------------
        delay_data['feature_impact_group'] = None
        delay_data.loc[nextday_ended, 'feature_impact_group'] = 'Next day ended'
        delay_data.loc[nextday_canceled, 'feature_impact_group'] = 'Next day canceled'
        # delay_data.loc[sameday_canceled, 'feature_impact_group'] = 'Same day canceled'
        # delay_data.loc[sameday_ended_mobile, 'feature_impact_group'] = 'Same day ended (mobile)'
        # delay_data.loc[sameday_ended_connect, 'feature_impact_group'] = 'Same day ended (connect)'
        delay_data.loc[sameday_mobile, 'feature_impact_group'] = 'Same day (mobile)'
        delay_data.loc[sameday_connect, 'feature_impact_group'] = 'Same day (connect)'
        # Define the order and colors for the feature_impact_group
        # category_order4 = ['Next day ended', 'Next day canceled', 'Same day canceled', 'Same day ended (mobile)', 'Same day ended (connect)']   # Define the order of categories
        category_order4 = ['Next day ended', 'Next day canceled', 'Same day ended (mobile)', 'Same day ended (connect)']   # Define the order of categories
        color_map4 = {
            'Next day ended': 'Green', 'Next day canceled': 'Lime',
            # 'Same day canceled': 'Violet', 'Same day ended (mobile)': 'f70e37', 'Same day ended (connect)': 'orange',
            'Same day (mobile)': 'f70e37', 'Same day (connect)': 'orange',
        }
        fig4 = px.pie(delay_data, names='feature_impact_group', title=f'Breakdown of Rental Transactions (Delay interval, State & Scope)',
                color='feature_impact_group', color_discrete_map= color_map4,  # This maps the feature_impact_group column to the color scheme
                category_orders={'feature_impact_group': category_order4}, hole=0.3) 
        fig4.update_traces(textinfo='label+value+percent', rotation=30, textfont=dict(size=11))    
        fig4.update_layout( 
            width=600, height=600, # Adjust height of the pie chart
            margin=dict(t=300, b=25, l=25, r=25),  title=dict(font=dict(size=16)), )
        # commentary4 = "Our final to-be-examined and impacted scope consists of 930 ended mobile bookings and 682 ended connect bookings, \
        #             for a total of 1612 bookings (~7.56% of total scope of 21310 bookings). \
        #             \n\nThis scope of 1612 bookings would potentially be affected by the new delay threshold feature."
        commentary4 = "Our final to-be-examined and impacted scope consists of 1028 ended mobile bookings and 813 ended connect bookings, \
            for a total of 1841 bookings (~8.64% of total scope of 21310 bookings). \
            \n\nThis scope of 1841 bookings would potentially be affected by the new delay threshold feature."
        figs.append(fig4)

        #----------------------------------------------------------------------------------------------------------------------------------
        with obj:
            col1, col2 = st.columns([1, 1])
            col1.plotly_chart(fig1, use_container_width=True)
            col1.write(f"**Commentary** : \n\n{commentary1}", unsafe_allow_html=True)
            col2.plotly_chart(fig2, use_container_width=True)
            col2.write(f"**Commentary** : \n\n{commentary2}", unsafe_allow_html=True)
            col3, col4 = st.columns([1, 1])
            col3.plotly_chart(fig3, use_container_width=True)
            col3.write(f"**Commentary** : \n\n{commentary3}", unsafe_allow_html=True)
            col4.plotly_chart(fig4, use_container_width=True)
            col4.write(f"**Commentary** : \n\n{commentary4}", unsafe_allow_html=True)
    #--------------------------------------------------------------------------------------------------------------------------------------------
    elif tab_name == 'Affected Rentals':
        # ended_data = delay_data[sameday_ended].copy()
        vcounts_time_delta_sameday = sameday_data.rename(columns={'time_delta_with_previous_rental_in_minutes': 'time_delta'})['time_delta'].value_counts().sort_index()
        total_time_delta_sameday = vcounts_time_delta_sameday.sum() 
        vcounts_time_delta_pct_sameday = vcounts_time_delta_sameday.to_frame(name='count').reset_index()  # Convert to DataFrame
        vcounts_time_delta_pct_sameday['cumul_cnt'] = vcounts_time_delta_pct_sameday['count'].cumsum()  # Cumulative sum
        vcounts_time_delta_pct_sameday['pct'] = round( (vcounts_time_delta_pct_sameday['count'] / total_time_delta_sameday) * 100, 2) # Calculate percentage
        vcounts_time_delta_pct_sameday['cumul_pct'] = round( (vcounts_time_delta_pct_sameday['cumul_cnt'] / total_time_delta_sameday) * 100, 2)
        with obj:
            col1, col2 = st.columns([3, 7])
        #----------------------------------------------------------------------------------------------------------------------------------
        with col1:
            st.write("") 
            scope = st.selectbox(
                "Select scope for time delay affected rental breakdown and figure",
                options = ['Mobile', 'Connect']
            )
            data_map = {'Mobile': data_sameday_mobile , 'Connect': data_sameday_connect}
            scope_data = data_map.get(scope)
            vcounts_time_delta_scope = scope_data.rename(columns={'time_delta_with_previous_rental_in_minutes': 'time_delta'})['time_delta'].value_counts().sort_index()
            total_time_delta_scope = vcounts_time_delta_scope.sum() 
            vcounts_time_delta_pct_scope = vcounts_time_delta_scope.to_frame(name='count').reset_index()  # Convert to DataFrame
            vcounts_time_delta_pct_scope['cumul_cnt'] = vcounts_time_delta_pct_scope['count'].cumsum()  # Cumulative sum
            vcounts_time_delta_pct_scope['pct'] = round( (vcounts_time_delta_pct_scope['count'] / total_time_delta_scope) * 100, 2) # Calculate percentage
            vcounts_time_delta_pct_scope['cumul_pct'] = round( (vcounts_time_delta_pct_scope['cumul_cnt'] / total_time_delta_scope) * 100, 2)
            st.write(f"Out of {len(scope_data)} {scope} rentals: ")
            st.dataframe(vcounts_time_delta_pct_scope, use_container_width=True)  # Expands the dataframe to use the container's width
        #----------------------------------------------------------------------------------------------------------------------------------
        with col2:
            # print(f"We're displaying {scope} figures...")
            list_vcounts = [ vcounts_time_delta_pct_sameday, vcounts_time_delta_pct_scope]
            color_map = {'mobile': 'red', 'connect': 'orange'}
            legend_map = {'mobile': 'sameday_mobile', 'connect': 'sameday_connect'}
            trace_name_map = {'mobile': 'Sameday(Mobile) Transactions', 'connect': 'Sameday(Connect) Transactions'}
            textpos_map = {'mobile': 'bottom left', 'connect': 'bottom right'}
            annotation_name_map = {'mobile': 'Sameday(Mobile) Annotations', 'connect': 'Sameday(Connect) Annotations'}
            x1_map = {'mobile': 0, 'connect': 0}; x2_map = {'mobile': 60, 'connect': 60}
            commentary_map = {'mobile': f'For mobile transactions, a threshold of 180m(3h) already affects a cumulative total of 52.92% of scope\n\n (544 out of 1028 same day mobile bookings)', 
                              'connect': f'For connect transactions, a threshold of 180m(3h) already affects a cumulative total of 50.31% of scope\n\n (409 out of 813 same day connect bookings)'}
            # Create the figure
            fig = go.Figure()
            # Add traces for each dataset
            for count, vcount_df in enumerate(list_vcounts, start=1):
                if count == 1:
                    color = 'blue'; legend = 'sameday'; trace_name = 'All Transactions'; textpos = 'top left';
                    annotation_name = 'All Annotations'; x1 = 0; x2 = -60
                else:
                    color = color_map.get(scope.lower()); legend = legend_map.get(scope.lower())
                    trace_name = trace_name_map.get(scope.lower()); textpos = textpos_map.get(scope.lower())
                    annotation_name = annotation_name_map.get(scope.lower())
                    x1 = x1_map.get(scope.lower());  x2 = x2_map.get(scope.lower())
                fig.add_trace(go.Scatter(
                    x=vcount_df['time_delta'],    y=vcount_df['cumul_pct'],
                    mode='lines+markers', line=dict(color=color), marker=dict(size=8),
                    name=trace_name, legendgroup=legend, showlegend=True # Group for toggling    
                ))
                # Add annotations as scatter traces for each dataset
                for i, row in vcount_df.iterrows():
                    fig.add_trace(go.Scatter(
                        x=[row['time_delta'] + x1, row['time_delta'] +x2],
                        y=[row['cumul_pct'], row['cumul_pct'] + 0],  # Adjust arrow length
                        mode='lines+text', line=dict(color=color, dash='dot'),
                        text=[None, f"{row['cumul_pct']:.2f}%"],  # Place text at the arrowhead
                        textposition=textpos, textfont=dict(size=10),
                        name=annotation_name, legendgroup=legend, showlegend=False # Group with initial dataset # Only show in legend for the main dataset
                    ))            
            col2.plotly_chart(fig, use_container_width=True)
            col2.write(f"**Commentary** : \n\n{commentary_map.get(scope.lower())}", unsafe_allow_html=True)
    #--------------------------------------------------------------------------------------------------------------------------------------------
    elif tab_name == 'Late Impact':
        #----------------------------------------------------------------------------------------------------------------------------------
        sameday_data = delay_data[with_time_delta]
        late = ( sameday_data['delay_at_checkout_of_previous_transaction'] > 0 )
        impacted = ( sameday_data['impacts_next_driver'] == True ) 
        # print(len(sameday_data[late]))
        # print(len(sameday_data[impacted]))
        pct_late_drivers = round(len(sameday_data[late])/ len(sameday_data)*100, 2)
        pct_impacted_drivers = round(len(sameday_data[impacted])/ len(sameday_data[late])*100, 2)
        pct_impacted_drivers_total = round(len(sameday_data[impacted])/ len(sameday_data)*100, 2)
        # print(sameday_data.head())
        commentary = (f"Percentage of late drivers for same day bookings : \
                    \n\n{pct_late_drivers}%  with {len(sameday_data[late])} late return drivers out of {len(sameday_data)} same day bookings. \
                    \n\nPercentage of impacted drivers from previous late rental returns : \
                    \n\n{pct_impacted_drivers}%  with {len(sameday_data[impacted])} impacted drivers for {len(sameday_data[late])} late return drivers, and \
                    \n\n{pct_impacted_drivers_total}%  with {len(sameday_data[impacted])} impacted drivers out of {len(sameday_data)} same day bookings.")
        # obj.write(len(sameday_data))
        obj.write(commentary)
    #--------------------------------------------------------------------------------------------------------------------------------------------
    elif tab_name == 'Solved Cases':
        #----------------------------------------------------------------------------------------------------------------------------------
        with obj:
            col1, col2 = st.columns([2, 3])
        with col1:
            st.write("") 
            scope = st.selectbox(
                "Select scope for time delay affected rental breakdown and figure",
                options = ['Mobile', 'Connect'], key="scope_solved"
            )
        results = []
        scope_mapping = {'Mobile': scope_impacted_mobile, 'Connect' : scope_impacted_connect}
        commentary_map = {'mobile': f'For mobile transactions, a threshold of 90m(1.5h) to 150m(2.5h) will be suitable, solving 60-70% (90-105 out of 149 current issue cases)', 
                              'connect': f'For connect transactions, a threshold of 90m(1.5h) to 120m(2h) will be suitable, solving 60-70% (41-48 out of 69 current issue cases)'}
        scope_data = scope_mapping.get(scope)
        # Iterate through the time delta thresholds
        for threshold in time_delta_range:
            # Filter problematic cases resolved by the current threshold
            resolved_cases = scope_data[
                scope_data['delay_at_checkout_of_previous_transaction'] < threshold
            ]
            # Count the number of resolved transactions
            resolved_count = len(resolved_cases)
            # Append the threshold and count to the results
            results.append({'time_delta_threshold': threshold, 'resolved_count': resolved_count})
        #----------------------------------------------------------------------------------------------------------------------------------
        # Convert the results to a DataFrame
        resolved_df = pd.DataFrame(results)
        # Add percentage for each threshold
        resolved_df['percentage'] = round (resolved_df['resolved_count'] / len(scope_data) * 100, 2)
        #----------------------------------------------------------------------------------------------------------------------------------
        with col1:
            st.write(f"Out of {len(scope_data)} {scope} rentals: ")
            st.dataframe(resolved_df, use_container_width=True)  # Expands the dataframe to use the container's width
            st.write(f"**Commentary** : \n\n{commentary_map.get(scope.lower())}", unsafe_allow_html=True)
            # obj.write(len(scope_impacted_mobile))
            # obj.write(len(scope_impacted_connect))      
        pass
    #--------------------------------------------------------------------------------------------------------------------------------------------
    else:
        obj.markdown("***:red[Click on any tab for exploratory data analysis on delay data.]***") 
    #--------------------------------------------------------------------------------------------------------------------------------------------
    # for i, fig in enumerate(figs):
    #     obj.plotly_chart(fig, use_container_width=True)
    #     commentary = eval(f'commentary{str(eval('i+1'))}')
    #     if commentary: obj.write(f"**Commentary** : {commentary}", unsafe_allow_html=True)
