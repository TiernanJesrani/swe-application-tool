import streamlit as st
import pandas as pd
#from jobs import 
import plotly.graph_objects as go
from leetcode_folder import leetcodeClass
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, JsCode
from mongo import apply, fetch_data_to_dataframe, enter_leetcode_data
from datetime import datetime

# Set the page configuration at the very beginning
st.set_page_config(page_title="Hello, Tiernan", layout="wide")

# Initialize session state for goals
if 'leetcode_goal' not in st.session_state:
    st.session_state.leetcode_goal = 0

if 'applications_goal' not in st.session_state:
    st.session_state.applications_goal = 0

def handle_application_click(link):
    apply(link)

def handle_leetcode_click(title):
    enter_leetcode_data(title)

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

def make_clickable(link, text):
    return f'<a href="{link}" target="_blank">{text}</a>'

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
        margin=dict(t=0, b=0, l=25, r=25),  # Symmetric and minimal margins
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

with cols_main[0]:
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
    
    # Center the chart
    chart_cols = st.columns([1, 3, 1])
    with chart_cols[1]:
        st.plotly_chart(fig_applications, use_container_width=True)
    
    # Add a search bar
    search_query_app = st.text_input('Search Applications', '')
    
    # Get and process the data
    data = fetch_data_to_dataframe('app_listings')
    
    # format datetime objects
    data['date'] = data['date'].dt.strftime('%Y-%m-%d')

    # Now make the 'Role' column clickable
    data['role'] = data.apply(lambda x: make_clickable(x['link'], x['role']), axis=1)

    # Include the 'Link' column in the DataFrame but exclude it from display
    grid_columns = ['company', 'role', 'location', 'date', 'link']
    
    data_display = data[grid_columns]
    
    # Define the columns to search in
    search_columns = ['company', 'role', 'location', 'date']
    
    # Filter the DataFrame based on the search query
    if search_query_app:
        mask = data[search_columns].apply(lambda x: x.astype(str).str.contains(search_query_app, case=False, na=False)).any(axis=1)
        filtered_data = data_display[mask]
    else:
        filtered_data = data_display
    
    # Configure AgGrid options
    gb = GridOptionsBuilder.from_dataframe(filtered_data)
    gb.configure_default_column(editable=False, sortable=True, filter=True, resizable=True)
    
    # Hide the 'Link' column
    gb.configure_column('link', hide=True)
    
    # Enable HTML content in the 'Role' column
    gb.configure_column("role", cellRenderer=JsCode('''
        function(params) {
            params.eGridCell.innerHTML = params.value;
            return '';
        }
    '''))
    
    # Adjust the width and enable text wrapping for 'Location' column
    gb.configure_column(
        "location",
        width=150,  # Adjust the width as needed
        wrapText=True,
        autoHeight=True,
        cellStyle={'white-space': 'normal'}
    )

    gb.configure_selection('single')
    grid_options = gb.build()
    
    # Display the data frame using AgGrid with selection enabled
    grid_response = AgGrid(
        filtered_data,
        gridOptions=grid_options,
        enable_enterprise_modules=False,
        allow_unsafe_jscode=True,  # Allow rendering of HTML content
        update_mode=GridUpdateMode.MODEL_CHANGED | GridUpdateMode.SELECTION_CHANGED,
        height=400,
        theme='alpine',  # Ensure both tables use the same theme
        selection_mode='single'
    )
    
    try:
        selected_row = grid_response['selected_rows'].iloc[0]
        link = selected_row['link']
        handle_application_click(link)
    except Exception as e:
        print("try failed")
        print(e)
        print(grid_response['selected_rows'])
        pass



st.markdown("<h3 style='text-align: center;'>Applied Applications</h3>", unsafe_allow_html=True)


data_applied = fetch_data_to_dataframe('app_applied')
data_applied['date'] = data_applied['date'].dt.strftime('%Y-%m-%d')
data_applied['role'] = data_applied.apply(lambda x: make_clickable(x['link'], x['role']), axis=1)

grid_columns_applied = ['company', 'role', 'location', 'date', 'link']
data_display_applied = data_applied[grid_columns_applied]

search_columns_applied = ['company', 'role', 'location', 'date']

search_query_app_applied = st.text_input('Search Applied Applications', '')

if search_query_app_applied:
    mask_applied = data_applied[search_columns_applied].apply(
        lambda x: x.astype(str).str.contains(search_query_app_applied, case=False, na=False)
    ).any(axis=1)
    filtered_data_applied = data_display_applied[mask_applied]
else:
    filtered_data_applied = data_display_applied

gb_applied = GridOptionsBuilder.from_dataframe(filtered_data_applied)
gb_applied.configure_default_column(editable=False, sortable=True, filter=True, resizable=True)

gb_applied.configure_column('link', hide=True)

gb_applied.configure_column("role", cellRenderer=JsCode('''
    function(params) {
        return params.value;
    }
'''))

gb_applied.configure_column(
    "location",
    width=150, 
    wrapText=True,
    autoHeight=True,
    cellStyle={'white-space': 'normal'}
)

gb_applied.configure_selection('single')
grid_options_applied = gb_applied.build()

grid_response_applied = AgGrid(
    filtered_data_applied,
    gridOptions=grid_options_applied,
    enable_enterprise_modules=False,
    allow_unsafe_jscode=True, 
    update_mode=GridUpdateMode.MODEL_CHANGED | GridUpdateMode.SELECTION_CHANGED,
    height=400,
    theme='alpine',  
    selection_mode='single'
)


# Second Column: Events Near Me
with cols_main[1]:
    st.markdown("<h3 style='text-align: center;'>Events Near Me</h3>", unsafe_allow_html=True)
    st.write("Content for Events Near Me goes here.")

# Third Column: Leetcode Progress and Content
with cols_main[2]:
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
    
    # Center the chart
    chart_cols = st.columns([1, 3, 1])
    with chart_cols[1]:
        st.plotly_chart(fig_leetcode, use_container_width=True)
    
    # Get the Leetcode problem list
    leetcode_instance = leetcodeClass.LeetcodeInst()
    problem_list = leetcode_instance.get_problem_list()
    leetcode_df = pd.DataFrame(problem_list)

    # Add a search bar
    search_query_leet = st.text_input('Search Leetcode Problems', '')
    
    # Define the columns to search in
    search_columns = ['Title', 'Difficulty', 'Tags']
    
    # Process 'Tags' if necessary
    leetcode_df['Tags'] = leetcode_df['Tags'].apply(lambda x: ', '.join(x))
    
    # Create clickable links in the 'Title' column
    leetcode_df['Plain_Title'] = leetcode_df['Title']
    leetcode_df['Title'] = leetcode_df.apply(lambda x: make_clickable(x['url'], x['Title']), axis=1)
    
    # Include the 'url' column but exclude it from display
    grid_columns = ['Title', 'Difficulty', 'Tags', 'url', 'Plain_Title']
    display_columns = ['Title', 'Difficulty', 'Tags']

    leetcode_df_display = leetcode_df[grid_columns]
    
    
    # Filter the DataFrame based on the search query
    if search_query_leet:
        mask = leetcode_df[search_columns].apply(lambda x: x.astype(str).str.contains(search_query_leet, case=False, na=False)).any(axis=1)
        filtered_leetcode_df = leetcode_df_display[mask]
    else:
        filtered_leetcode_df = leetcode_df_display
    
    # Configure AgGrid options
    gb = GridOptionsBuilder.from_dataframe(filtered_leetcode_df)
    gb.configure_default_column(editable=False, sortable=True, filter=True, resizable=True)
    
    # Hide the 'url' column
    gb.configure_column('url', hide=True)
    gb.configure_column('Plain_Title', hide=True)
    
    # Enable HTML content in the 'Title' column
    gb.configure_column("Title", cellRenderer=JsCode('''
        function(params) {
            params.eGridCell.innerHTML = params.value;
            return '';
        }
    '''))
    
    gb.configure_selection('single')
    grid_options = gb.build()
    
    # Display the data frame using AgGrid with selection enabled
    grid_response = AgGrid(
        filtered_leetcode_df,
        gridOptions=grid_options,
        enable_enterprise_modules=False,
        allow_unsafe_jscode=True,  # Allow rendering of HTML content
        update_mode=GridUpdateMode.MODEL_CHANGED | GridUpdateMode.SELECTION_CHANGED,
        height=400,
        theme='alpine',  # Ensure both tables use the same theme
        selection_mode='single'
    )
    
    # Handle the selected row to print the link
    try:
        selected_row = grid_response['selected_rows'].iloc[0]
        title = selected_row['Plain_Title']
        handle_leetcode_click(title)
    except Exception as e:
        print("try failed")
        print(e)
        print(grid_response['selected_rows'])
        pass