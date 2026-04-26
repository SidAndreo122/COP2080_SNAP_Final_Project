# streamlit 
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import streamlit as st
import pandas as pd
import altair as alt
from app.agent import run_agent, create_agent, set_inventory_df
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
        inv_df['color'] = inv_df['net_profit'].apply(lambda x: 'Profitable' if x > 0 else 'Loss')
        st.subheader("Inventory Analysis: Net Profit ($) by Product")
        
        # Create Altair chart with color-coded bars
        chart = alt.Chart(inv_df).mark_bar().encode(
            x='product_name:N',
            y='net_profit:Q',
            color=alt.Color('color:N', scale=alt.Scale(domain=['Profitable', 'Loss'], range=['green', 'red']))
        ).properties(height=400)
        st.altair_chart(chart, width='stretch')
        st.dataframe(inv_df)



@st.cache_resource
def load_agent():
    return create_agent()

st.sidebar.header("Chat Agent")

with st.sidebar.form("Enter a question for the Agent."):
      user_query = st.text_input("Ask the Chat Agent a question!")
      submitted = st.form_submit_button("Submit")
if submitted:
    if inventory_data_file is None:
        st.sidebar.warning("Please upload inventory data first.")
    elif not user_query:
        st.sidebar.warning("Please enter a question.")
    else:
        set_inventory_df(inv_df)

        agent = load_agent()

        with st.sidebar:
            with st.spinner("Thinking..."):
                response = run_agent(user_query, agent)
    
        st.sidebar.write("AI Response:")
        st.sidebar.write(response)
