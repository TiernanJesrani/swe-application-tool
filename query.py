from datetime import datetime   # This will be needed later
import os
import pandas as pd

from dotenv import load_dotenv
from pymongo import MongoClient

from jobs import scrape_url, convert_data_entry, master_df, not_in_db

def apply(link):
    listings_collection = open_collection("app_listings")
    applied_collection = open_collection("app_applied")

    listings_collection.find_one_and_update(
        { "link" : link },
        { "$set": {"hidden" : True} }
    )

    listing = listings_collection.find_one(
         { "link" : link }
    )

    print(listing)


    data = {
        "company": listing["company"],
        "role": listing["role"],
        "location": listing["location"],
        "link": listing["link"],
        "date": datetime.now(),
        "status": "Applied"
    }
    applied_collection.insert_one(data)


def open_collection(collection_name):
    load_dotenv()
    MONGODB_URI = os.environ['MONGODB_URI']

    # Connect to your MongoDB cluster:
    client = MongoClient(MONGODB_URI)

    # Select the database you want to use:
    db = client['dashboard']
    collection = db[collection_name]

    return collection

# pulls data from the database and converts it to a pandas DF
def fetch_data_to_dataframe(collection):
    data = list(collection.find())
    df = pd.DataFrame(data)
    return df

def enter_leetcode_data(title):
    lc_collection = open_collection("lc_cache")
    lc_collection.insert_one(
        {"title":title}
    )

    

# apps = open_collection("app_listings")

# print ("\n\n\n\nmongo.py: master_df")
# print(master_df)

# for index, row in master_df.iterrows():
#     if not_in_db(row['Link'], apps):
#         apps.insert_one(convert_data_entry(row))
    
# apply("http://redirect.cvrve.me/e36fd103a077bcbda08a?utm_source=ouckah")

def main():
    enter_leetcode_data("Two sum")

if __name__=="__main__":
    main()