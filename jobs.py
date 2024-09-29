from datetime import datetime
import requests as re
import pandas as pd
from bs4 import BeautifulSoup
from pymongo import MongoClient

# scrapes github template for jobs, does some light data cleaning, and returns a dataframe with raw column names
def scrape_url(url):
    response = re.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Locate the table using the <markdown-accessiblity-table> tag
        table = soup.find('markdown-accessiblity-table')
        if table:
            headers = [header.text for header in table.find_all('th')]
            
            rows = []
            for row in table.find_all('tr')[1:]:  # Skip the header row
                cells = row.find_all('td')
                row_data = []
                for i, cell in enumerate(cells):
                    # Check if the cell contains a link
                    link = cell.find('a')
                    if link and i != 0: # Skip the company column
                        row_data.append(link.get('href'))  # Extract the href attribute
                    else:
                        row_data.append(cell.get_text(separator=" ").strip())
                rows.append(row_data)
            
            df = pd.DataFrame(rows, columns=headers)

            # Handle the ↳ character in the Company column
            company_col = df.columns[df.columns.str.contains('Company', case=False, regex=True)][0]
            last_company = None
            for i, company in enumerate(df[company_col]):
                if '↳' in company:
                    df.at[i, company_col] = last_company
                else:
                    last_company = company

            # Replace "NYC" with "New York, NY" in the Location column
            location_col = df.columns[df.columns.str.contains('Location', case=False, regex=True)][0]
            df[location_col] = df[location_col].str.replace('NYC', 'New York, NY', case=False)
            df[location_col] = df[location_col].str.replace('SF', 'San Francisco, CA', case=False)
            df.loc[df[location_col].str.contains('remote', case=False, na=False), location_col] = 'Remote'
      
        else:
            print("table not found :(")

    return df

master_df = pd.DataFrame(columns=['Company', 'Role', 'Location', 'Link', 'Date'])

# updates master dataframe with new data, adjusted to fix column names
def prune_add_table(df):
    global master_df

    column_mapping = {
        'company': ['Company', 'Employer', 'Organization'],
        'role': ['Role', 'Job', 'Title', 'Position'],
        'location': ['Location', 'City', 'Place'],
        'link': ['Link', 'URL', 'Apply'],
        'date': ['Date', 'Time', 'Posted']
    }
    
    new_column_names = {}
    for col in df.columns:
        for new_name, keywords in column_mapping.items():
            if any(keyword in col for keyword in keywords):
                new_column_names[col] = new_name
                break
    
    

    df.rename(columns=new_column_names, inplace=True)
    final_df = df[['Company', 'Role', 'Location', 'Link', 'Date']]
    final_df = final_df[final_df['Link'].str.len() >= 6]

    master_df = pd.concat([master_df, final_df], ignore_index=True)

    return final_df

# converts a row from the dataframe to DB format
def convert_data_entry(row):
    data = {
        "company": row["Company"],
        "role": row["Role"],
        "location": row["Location"],
        "link": row["Link"],
        "date": parse_date(row["Date"]),
        "hidden" : False
    }
    print(data)
    return data

# parses a date string into a datetime object
def parse_date(date_str):
    try:
        # Try to parse the date assuming the format is "MMM DD" (e.g., "Sep 28")
        date_obj = datetime.strptime(date_str, "%b %d")
        date_obj = date_obj.replace(year=2024)
    except ValueError:
        try:
            # Try to parse the date assuming the format is "MM/DD/YYYY" (e.g., "05/19/2024")
            date_obj = datetime.strptime(date_str, "%m/%d/%Y")
        except ValueError:
            raise ValueError("Date format not recognized. Use 'MMM DD' or 'MM/DD/YYYY'.")
    
    return date_obj


def not_in_db(link, collection): 
    return collection.count_documents({"link": link}) == 0
    
    
        


# used to be in jobs.py "main" but was running on import so i put that jawn in this function    
def add_to_db():
    url_list = ["https://github.com/Ouckah/Summer2025-Internships#we-love-our-contributors-%EF%B8%8F%EF%B8%8F", "https://github.com/arunike/Summer-2025-Internship-List?tab=readme-ov-file#contributing", "https://github.com/SimplifyJobs/Summer2025-Internships#we-love-our-contributors-%EF%B8%8F%EF%B8%8F"]
    for url in url_list:
        data = scrape_url(url)
        prune_add_table(data)

        print(master_df)
        print(master_df.value_counts("Location"))
