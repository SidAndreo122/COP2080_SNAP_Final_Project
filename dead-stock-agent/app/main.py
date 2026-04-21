# streamlit 
import streamlit as st
import matplotlib

path = "dead-stock-agent/data"
doc_path = f"{path}/docs"


def main():
    st.title("Dead Stock Agent")
    
    
    # Example of using matplotlib to display a simple plot
    st.subheader("Inventory Analysis")
   
    st.pyplot(fig)