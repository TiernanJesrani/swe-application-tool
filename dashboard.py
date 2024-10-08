import streamlit as st
import pandas as pd
#from jobs import 
import plotly.graph_objects as go
from leetcode_folder import leetcodeClass
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, JsCode, DataReturnMode
from mongo import apply, fetch_data_to_dataframe, enter_leetcode_data, update_status_in_database, get_sankey_vals
from datetime import datetime, timedelta

# Set the page configuration at the very beginning
st.set_page_config(page_title="Hello, Tiernan", layout="wide")

st.markdown(
    """
    <!-- Import Roboto Mono from Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Roboto+Mono&display=swap" rel="stylesheet">
    
    <style>
    /* Apply a vertical gradient from white to light blue and set global font */
    .stApp {
        background: linear-gradient(to bottom, white, #ADD8E6);
        font-family: 'Roboto Mono', monospace; /* Set global font to Roboto Mono */
    }

    /* Ensure that all container backgrounds are semi-transparent to show the gradient */
    .stContainer {
        background-color: rgba(255, 255, 255, 0.85); /* Slight transparency */
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1); /* Add subtle shadow for depth */
        border-radius: 12px; /* Rounded corners for a modern look */
        padding: 20px; /* Consistent padding */
        margin: 10px; /* Space between containers */
    }

    /* Style headers with Roboto Mono */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Roboto Mono', monospace !important; /* Ensure overriding any other styles */
        color: #333333; /* Darker text for better readability */
    }

    /* Enhance text elements */
    body, p, div, span, label {
        font-family: 'Roboto Mono', monospace;
        font-size: 16px; /* Increase global font size for better readability */
        color: #444444; /* Slightly lighter than headers */
    }

    /* Style buttons */
    .stButton > button {
        background-color: #4CAF50; /* Green background */
        color: white; /* White text */
        border: none;
        border-radius: 8px; /* Rounded corners */
        padding: 10px 20px; /* Padding inside buttons */
        font-size: 16px;
        font-family: 'Roboto Mono', monospace;
        cursor: pointer;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2); /* Subtle shadow */
    }

    .stButton > button:hover {
        background-color: #45a049; /* Darker green on hover */
    }

    /* Style input fields */
    .stTextInput > div > div > input {
        border: 1px solid #cccccc; /* Light gray border */
        border-radius: 8px; /* Rounded corners */
        padding: 8px; /* Padding inside input */
        font-size: 16px;
        font-family: 'Roboto Mono', monospace;
    }

    /* Style data tables */
    .ag-theme-alpine .ag-header {
        background-color: #f0f0f0; /* Light gray header */
        font-family: 'Roboto Mono', monospace;
        font-size: 16px;
    }

    .ag-theme-alpine .ag-row {
        font-family: 'Roboto Mono', monospace;
        font-size: 14px;
    }

    /* Additional UI enhancements */
    .popover-content {
        background-color: rgba(255, 255, 255, 0.95);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        border-radius: 10px;
        padding: 15px;
    }

    </style>
    """,
    unsafe_allow_html=True
)

# Initialize session state for goals
if 'denominator_leetcode' not in st.session_state:
    st.session_state.temp_leetcode_goal = 10

if 'denominator_applications' not in st.session_state:
    st.session_state.temp_applications_goal = 10

def handle_application_click(link):
    apply(link)

def handle_leetcode_click(title):
    enter_leetcode_data(title)

def is_last_week(date):
    now = datetime.now()
    current_weekday = now.weekday() 
    days_since_monday = (current_weekday)
    last_monday_midnight = now - timedelta(days=days_since_monday, hours=now.hour, minutes=now.minute, seconds=now.second, microseconds=now.microsecond)
    return [date > last_monday_midnight]

# Function to toggle goal inputs using a popover
def toggle_goal_inputs():
    with st.popover("Set Goals"):
        st.session_state.denominator_leetcode = st.number_input(
            "Daily Leetcode Problems Completed",
            min_value=0,
            step=1,
            key='temp_leetcode_goal'
        )
        st.session_state.denominator_applications = st.number_input(
            "Daily Applications Submitted",
            min_value=0,
            step=1,
            key='temp_applications_goal'
        )


def make_clickable(link, text):
    return f'<a href="{link}" target="_blank">{text}</a>'

# Function to save goals
def save_goals():
    st.session_state.denominator_leetcode = st.session_state.temp_leetcode_goal
    st.session_state.denominator_applications = st.session_state.temp_applications_goal
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
        marker=dict(colors=['#4CAF50', '#f0eded']),
        hoverinfo='label+percent',
        textinfo='none'
    )])

    fig.update_layout(
        showlegend=False,
        margin=dict(t=0, b=0, l=25, r=25),
        paper_bgcolor='rgba(0, 0, 0, 0)',
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
                Hello, Tiernan!
            </h1>
            """,
            unsafe_allow_html=True
        )
    with cols[2]:
        st.empty()

st.markdown("<br><br>", unsafe_allow_html=True)

# Main content with three columns
cols_main = st.columns(2, gap="large")


with cols_main[0]:
    st.markdown("<h3 style='text-align: center;'>Application Progress</h3>", unsafe_allow_html=True)
    
    # Example completed applications; replace with dynamic data as needed
    completed_applications = 0 

    apps = fetch_data_to_dataframe('app_applied')
    for app in apps['date']:
        if is_last_week(app):
            completed_applications += 1

    denominator_applications = st.session_state.denominator_applications
    numerator_applications = completed_applications
    # Calculate completion percentage
    if denominator_applications == 0:
        numerator_applications = 0
        percent_applications = 0
        
    
    # Display percentage as centered text
    st.markdown(
        f"<h2 style='text-align: center; font-size: 24px; color: #4CAF50;'>{numerator_applications}/{denominator_applications} Completed</h2>",
        unsafe_allow_html=True
    )
    
    # Create donut chart
    fig_applications = create_donut_chart(numerator_applications, denominator_applications)
    
    # Center the chart
    with st.container():
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
        pass


    st.markdown("<h3 style='text-align: center;'>Applied Applications</h3>", unsafe_allow_html=True)


    # Fetch data including 'status'
    data_applied = fetch_data_to_dataframe('app_applied')
    data_applied['_id'] = data_applied['_id'].astype(str)
    data_applied['date'] = data_applied['date'].dt.strftime('%Y-%m-%d')
    data_applied['role'] = data_applied.apply(lambda x: make_clickable(x['link'], x['role']), axis=1)

    # Prepare data for display
    grid_columns_applied = ['_id', 'company', 'role', 'location', 'date', 'status', 'link']
    data_display_applied = data_applied[grid_columns_applied]
    search_columns_applied = ['company', 'role', 'location', 'date', 'status']

    # Implement search functionality
    search_query_app_applied = st.text_input('Search Applied Applications', '')
    if search_query_app_applied:
        mask_applied = data_applied[search_columns_applied].apply(
            lambda x: x.astype(str).str.contains(search_query_app_applied, case=False, na=False)
        ).any(axis=1)
        filtered_data_applied = data_display_applied[mask_applied]
    else:
        filtered_data_applied = data_display_applied

    # Configure AgGrid
    gb_applied = GridOptionsBuilder.from_dataframe(filtered_data_applied)
    gb_applied.configure_default_column(sortable=True, filter=True, resizable=True)

    non_editable_columns = ['_id', 'company', 'role', 'location', 'date', 'link']
    for col in non_editable_columns:
        gb_applied.configure_column(col, editable=False)

    gb_applied.configure_column('_id', hide=True)
    gb_applied.configure_column('link', hide=True)
    gb_applied.configure_column(
        'status',
        editable=True,
        cellEditor='agSelectCellEditor',
        cellEditorParams={'values': ['Applied', 'No Answer',  'Rejected', 'Interview', 'Offer', 'Accepted']},
        cellStyle=JsCode('''
            function(params) {
                if (params.value == 'Accepted') {
                    return {'backgroundColor': 'purple', 'color': 'white'};
                } else if (params.value == 'Interview') {
                    return {'backgroundColor': 'yellow', 'color': 'black'};
                } else if (params.value == 'Rejected') {
                    return {'backgroundColor': 'red', 'color': 'white'};
                } else if (params.value == 'Offer') {
                    return {'backgroundColor': 'green', 'color': 'white'};
                } else if (params.value == 'No Answer') {
                    return {'backgroundColor': 'cyan', 'color': 'white'};
                } else {
                    return {};
                }
            }
        ''')
    )
    gb_applied.configure_column("role", cellRenderer=JsCode('''
        function(params) {
            params.eGridCell.innerHTML = params.value;
            return '';
        }
    '''))
    gb_applied.configure_column(
        "location",
        width=150, 
        wrapText=True,
        autoHeight=True,
        cellStyle={'white-space': 'normal'}
    )
    grid_options_applied = gb_applied.build()

    # Display the AgGrid table
    grid_response_applied = AgGrid(
        filtered_data_applied,
        gridOptions=grid_options_applied,
        data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
        update_mode=GridUpdateMode.MODEL_CHANGED,
        allow_unsafe_jscode=True,
        enable_enterprise_modules=False,
        height=400,
        theme='alpine',  
        editable=True
    )

    # Handle data changes
    updated_data = grid_response_applied['data']
    merged_data = data_display_applied.merge(updated_data, on='_id', suffixes=('_original', '_updated'))
    changed_rows = merged_data[merged_data['status_original'] != merged_data['status_updated']]

    for index, row in changed_rows.iterrows():
        record_id = row['_id']
        new_status = row['status_updated']
        link_tochange = row['link_original']
        update_status_in_database(new_status, link_tochange)

# Third Column: Leetcode Progress and Content
with cols_main[1]:
    leetcode_instance = leetcodeClass.LeetcodeInst()
    st.markdown("<h3 style='text-align: center;'>Leetcode Progress</h3>", unsafe_allow_html=True)
    
    # Example completed problems; replace with dynamic data as needed
    numerator_leetcode = leetcode_instance.get_progress_weekly()
    denominator_leetcode = st.session_state.denominator_leetcode
    # Calculate completion percentage
    if denominator_leetcode == 0:
        numerator_leetcode = 0 
        denominator_leetcode = 0
    
    # Display percentage as centered text
    st.markdown(
        f"<h2 style='text-align: center; font-size: 24px; color: #4CAF50;'>{numerator_leetcode}/{denominator_leetcode} Completed</h2>",
        unsafe_allow_html=True
    )
    
    # Create donut chart
    fig_leetcode = create_donut_chart(numerator_leetcode, denominator_leetcode)
    
    # Center the chart

    with st.container():
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
        pass

    node_labels = ["Applied", "No Answer", "Rejected", "Interviews", "Offers", "Accepted"]
    source = [0, 0, 0, 3, 4]  
    target = [1, 2, 3, 4, 5]  
    sankey_vals = get_sankey_vals()
    print(sankey_vals)
    values = sankey_vals

    link_colors = [
    "rgba(41, 185, 123, 0.5)",  # Blue
    "rgba(208, 38, 38, 0.5)",  # Red
    "rgba(236, 236, 83, 0.5)",  # Yellow
    "rgba(52, 185, 42, 0.5)",  # Green
    "rgba(205, 51, 229, 0.5)"  # Purple
    ]

    node_colors = [
    "rgba(41, 185, 123, 0.8)",  # Blue
    "rgba(41, 185, 123, 0.8)",  # Yellow
    "rgba(208, 38, 38, 0.8)",  # Red
    "rgba(52, 185, 42, 0.8)",  # Green
    "rgba(205, 51, 229, 0.8)",  # Purple
    "rgba(205, 51, 229, 0.8)"
    ]

    fig = go.Figure(go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=node_labels,
            color=node_colors,
        ),
        link=dict(
            source=source,  
            target=target, 
            value=values,  
            color=link_colors 
        )
    ))

    fig.update_layout(
        showlegend=False,
        margin=dict(t=20, b=0, l=25, r=25),
        paper_bgcolor='rgba(0, 0, 0, 0)',
    )

    st.markdown("<h3 style='text-align: center;'>Sankey Diagram</h3>", unsafe_allow_html=True)
    st.plotly_chart(fig)