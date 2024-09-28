import streamlit as st
import pandas as pd

# 1. Set the page configuration to wide for maximum horizontal space
st.set_page_config(page_title="Hello, Rishab", layout="wide")

# 2. Centered Header using HTML
st.markdown(
    """
    <h1 style='text-align: center; font-family: Arial, sans-serif;'>
        Hello, Rishab!
    </h1>
    """,
    unsafe_allow_html=True
)

# 3. Create Columns with Spacer Columns to Spread Subheaders
# Define 7 columns with relative widths: Spacer, Content, Spacer, Content, Spacer, Content, Spacer
st.markdown("<br><br>", unsafe_allow_html=True)

cols = st.columns([1, 3, 1, 3, 1, 3, 1], gap="large")

# Insert subheaders into the content columns
with cols[1]:
    st.markdown("<h3 style='text-align: center;'>Applications</h3>", unsafe_allow_html=True)
    st.write(pd.DataFrame())

with cols[3]:
    st.markdown("<h3 style='text-align: center;'>Recruiting Center</h3>", unsafe_allow_html=True)

with cols[5]:
    st.markdown("<h3 style='text-align: center;'>Leetcode</h3>", unsafe_allow_html=True)
