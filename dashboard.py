import streamlit as st
import pandas as pd
from jobs import get_datatoshow
import plotly.graph_objects as go

# Set the page configuration at the very beginning
st.set_page_config(page_title="Hello, Rishab", layout="wide")

# Initialize session state for goals
if 'leetcode_goal' not in st.session_state:
    st.session_state.leetcode_goal = 0

if 'applications_goal' not in st.session_state:
    st.session_state.applications_goal = 0

# Function to toggle goal inputs using a popover
def toggle_goal_inputs():
    with st.popover("Set Goals"):
        st.session_state.leetcode_goal = st.number_input(
            "Daily Leetcode Problems Completed",
            min_value=0,
            step=1,
            key='temp_leetcode_goal'
        )
        st.session_state.applications_goal = st.number_input(
            "Daily Applications Submitted",
            min_value=0,
            step=1,
            key='temp_applications_goal'
        )

# Function to save goals
def save_goals():
    st.session_state.leetcode_goal = st.session_state.temp_leetcode_goal
    st.session_state.applications_goal = st.session_state.temp_applications_goal
    st.session_state.show_goal_inputs = False
    st.success("Goals have been updated successfully!")

# Function to create a donut chart
def create_donut_chart(current, goal):
    if goal > 0:
        progress = min(current / goal, 1.0)
    else:
        progress = 0
    remaining = 1.0 - progress

    fig = go.Figure(data=[go.Pie(
        labels=['Completed', 'Remaining'],
        values=[progress, remaining],
        hole=.6,
        marker=dict(colors=['#4CAF50', '#d3d3d3']),
        hoverinfo='label+percent',
        textinfo='none'
    )])

    fig.update_layout(
        showlegend=False,
        margin=dict(t=0, b=200, l=25, r=25),  # Symmetric and minimal margins
    )

    return fig

# Header section
header_container = st.container()
with header_container:
    cols = st.columns([1, 6, 1])  
    with cols[0]:
        toggle_goal_inputs()
                
    with cols[1]:
        st.markdown(
            """
            <h1 style='text-align: center; font-family: Arial, sans-serif;'>
                Hello, Rishab!
            </h1>
            """,
            unsafe_allow_html=True
        )
    with cols[2]:
        st.empty()

st.markdown("<br><br>", unsafe_allow_html=True)

# Main content with three columns
cols_main = st.columns(3, gap="large")

# First Column: Applications Progress and Data
with cols_main[0]:
    
    # Applications Header (Moved Up)
    st.markdown("<h3 style='text-align: center;'>Application Progress</h3>", unsafe_allow_html=True)
    
    # Example completed applications; replace with dynamic data as needed
    completed_applications = 5 
    applications_goal = st.session_state.applications_goal
    
    # Calculate completion percentage
    if applications_goal > 0:
        percent_applications = min(completed_applications / applications_goal, 1.0) * 100
    else:
        percent_applications = 0
    
    # Display percentage as centered text
    st.markdown(
        f"<h2 style='text-align: center; font-size: 24px; color: #4CAF50;'>{percent_applications:.1f}% Completed</h2>",
        unsafe_allow_html=True
    )
    
    # Create donut chart
    fig_applications = create_donut_chart(completed_applications, applications_goal)
    
    # Center the chart using adjusted columns
    chart_cols = st.columns([1, 3, 1])  # Wider middle column for better centering
    with chart_cols[1]:
        st.plotly_chart(fig_applications, use_container_width=True)
    
    # Display data if available
    data = get_datatoshow()
    if not data.empty:
        st.dataframe(data, height=400)
    else:
        st.markdown("<div style='text-align: center;'>No data available.</div>", unsafe_allow_html=True)

# Second Column: Events Near Me
with cols_main[1]:
    st.markdown("<h3 style='text-align: center;'>Events Near Me</h3>", unsafe_allow_html=True)
    st.write("Content for Events Near Me goes here.")

# Third Column: Leetcode Progress and Content
with cols_main[2]:
    
    # Leetcode Header (Moved Up)
    st.markdown("<h3 style='text-align: center;'>Leetcode Progress</h3>", unsafe_allow_html=True)
    
    # Example completed problems; replace with dynamic data as needed
    completed_problems = 5  
    leetcode_goal = st.session_state.leetcode_goal
    
    # Calculate completion percentage
    if leetcode_goal > 0:
        percent_leetcode = min(completed_problems / leetcode_goal, 1.0) * 100
    else:
        percent_leetcode = 0
    
    # Display percentage as centered text
    st.markdown(
        f"<h2 style='text-align: center; font-size: 24px; color: #4CAF50;'>{percent_leetcode:.1f}% Completed</h2>",
        unsafe_allow_html=True
    )
    
    # Create donut chart
    fig_leetcode = create_donut_chart(completed_problems, leetcode_goal)
    
    # Center the chart using adjusted columns
    chart_cols = st.columns([1, 3, 1])  # Wider middle column for better centering
    with chart_cols[1]:
        st.plotly_chart(fig_leetcode, use_container_width=True)
    
    st.write("Content for Leetcode goes here.")
