import requests as re
import pandas as pd
from bs4 import BeautifulSoup

def scrape_url(url):
    response = re.get(url)
    if response.status_code == 200:
        print("request was successful")
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Locate the table using the <markdown-accessiblity-table> tag
        table = soup.find('markdown-accessiblity-table')
        if table:
            print("table found... extracting data")
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

def prune_table(df):
    column_mapping = {
        'Company': ['Company', 'Employer', 'Organization'],
        'Role': ['Role', 'Job', 'Title', 'Position'],
        'Location': ['Location', 'City', 'Place'],
        'Link': ['Link', 'URL', 'Apply'],
        'Date': ['Date', 'Time', 'Posted']
    }
    
    new_column_names = {}
    for col in df.columns:
        print(col)
        for new_name, keywords in column_mapping.items():
            if any(keyword in col for keyword in keywords):
                new_column_names[col] = new_name
                break
    
    

    df.rename(columns=new_column_names, inplace=True)
    final_df = df[['Company', 'Role', 'Location', 'Link', 'Date']]
    return final_df

def get_datatoshow():
    url = "https://github.com/arunike/Summer-2025-Internship-List?tab=readme-ov-file#contributing"
    data = scrape_url(url)
    if not data.empty:
        datatoshow = prune_table(data)
        return datatoshow
    else:
        return pd.DataFrame()
