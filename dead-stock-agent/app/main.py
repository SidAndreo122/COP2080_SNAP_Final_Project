# streamlit 
import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

path = "dead-stock-agent/data"
doc_path = f"{path}/docs"

st.set_page_config(page_title="Dead Stock Agent", page_icon=":bar_chart:", layout="wide")
st.title("Dead Stock Agent")
    
inventory_data_file = st.file_uploader("Upload Inventory Data", type=["csv"])
##TEST##
#with open(f"{path}/inventory.csv", "r") as f:
#    test_inventory_data = pd.read_csv(f)
#    test_df = pd.DataFrame(test_inventory_data)
#    test_cost = [unit * holding_cost for unit, holding_cost in zip(test_df['units_on_hand'], test_df['holding_cost_per_day'])]
#    test_df['cost'] = test_cost
#    test_profit = [unit * profit for unit, profit in zip(test_df['daily_demand'], test_df['cost_per_unit'])]
#    test_df['profit'] = test_profit
#    test_net= test_df['profit'] - test_df['cost']
#    test_df['net_profit'] = test_net
#    st.subheader("Test Inventory Data")
#    st.dataframe(test_df)
##END TEST##
if inventory_data_file is not None:
        inventory_data = pd.read_csv(inventory_data_file)
        inv_df=pd.DataFrame(inventory_data)
        cost = [unit * holding_cost for unit, holding_cost in zip(inv_df['units_on_hand'], inv_df['holding_cost_per_day'])]
        profit = [unit * profit for unit, profit in zip(inv_df['daily_demand'], inv_df['cost_per_unit'])]
        inv_df['cost'] = cost
        inv_df['profit'] = profit
        inv_df['net_profit'] = inv_df['profit'] - inv_df['cost']
        #inv_df['color'] = ['green' if net_profit > 0 else 'red' for net_profit in inv_df['net_profit']]
        inv_df['positive_profit'] = inv_df['net_profit'] > 0
        st.subheader("Inventory Analysis")
        st.bar_chart(inv_df.set_index('sku_id')['net_profit'], color=inv_df['positive_profit'].map({True: 'green', False: 'red'}))

st.sidebar.header("Chat Agent")
st.sidebar.text_input("Ask about inventory insights or recommendations:", key="chat_input")
##CALL AI PLACEHOLDER##
if st.chat_input is not None:
    st.sidebar.write("AI Response: This is where the AI's response will be displayed based on the user's query about inventory insights or recommendations.")