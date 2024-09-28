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
                row_data = [cell.get_text(separator=" ").strip() for cell in cells]
                rows.append(row_data)
            
            df = pd.DataFrame(rows, columns=headers)
        else:
            print("table not found :(")

    return df

# reduce the table to only the columns we need: 'Company', 'Role', 'Location', 'Link', 'Date'
def prune_table(df):
    column_mapping = {
        'Company': ['Company', 'Employer', 'Organization'],
        'Role': ['Role', 'Job', 'Title', 'Position'],
        'Location': ['Location', 'City', 'Place'],
        'Link': ['Link', 'URL', 'Website'],
        'Date': ['Date', 'Time', 'Posted']
    }
    
    new_column_names = {}
    print("columns:")
    print(df.columns)
    for col in df.columns:
        print(col)
        for new_name, keywords in column_mapping.items():
            if any(keyword in col for keyword in keywords):
                new_column_names[col] = new_name
                break
    
    df.rename(columns=new_column_names, inplace=True)
    final_df = df[['Company', 'Role', 'Location', 'Link', 'Date']]

    return final_df



url = "https://github.com/SimplifyJobs/Summer2025-Internships#we-love-our-contributors-%EF%B8%8F%EF%B8%8F"

url = "https://github.com/Ouckah/Summer2025-Internships#we-love-our-contributors-%EF%B8%8F%EF%B8%8F"
url = "https://github.com/arunike/Summer-2025-Internship-List?tab=readme-ov-file#contributing"

data = scrape_url(url)
print(data)
print(prune_table(data))
print("done!")