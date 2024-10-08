from datetime import datetime, timedelta   # This will be needed later
import os
import pandas as pd

from dotenv import load_dotenv
from pymongo import MongoClient

from jobs import scrape_url, convert_data_entry, master_df, not_in_db

MONGODB_URI = os.environ['MONGODB_URI']
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

    # Connect to your MongoDB cluster:
    client = MongoClient(MONGODB_URI)

    # Select the database you want to use:
    db = client['dashboard']
    collection = db[collection_name]

    return collection

# pulls data from the database and converts it to a pandas DF
def fetch_data_to_dataframe(collection_name):
    collection = open_collection(collection_name)
    if collection_name == 'app_listings':
        data = list(collection.find({
            'hidden': False
        }))
    else:
        data = list(collection.find())
    df = pd.DataFrame(data)
    return df

def update_status_in_database(new_status, link):
    collection = open_collection('app_applied')
    
    # Update the status
    collection.find_one_and_update(
        { "link" : link },
        { "$set": {"status" : new_status} }
    )
    


def enter_leetcode_data(title):
    lc_collection = open_collection("lc_cache")
    if lc_collection.count_documents({"title": title}) == 0:
        lc_collection.insert_one(
            {"title":title}
        )

def get_sankey_vals():
    applied_collection = open_collection("app_applied")

    all_applications = applied_collection.find()

    ["Applied", "No Answer", "Rejected", "Interviews", "Offers", "Accepted"]
    applied = 0
    no_answer = 0
    rejected = 0
    interviews = 0
    offers = 0
    accepted = 0


    for application in all_applications:
        if application['status'] == 'Applied':
            applied += 1
        elif application['status'] == 'No Answer':
            applied += 1
            no_answer += 1
        elif application['status'] == 'Rejected':
            applied += 1
            rejected += 1
        elif application['status'] == 'Interview':
            applied += 1
            interviews += 1
        elif application['status'] == 'Offer':
            applied += 1
            interviews += 1
            offers += 1
        elif application['status'] == 'Accepted':
            applied += 1
            interviews += 1
            offers += 1
            accepted += 1
    
    return [no_answer, rejected, interviews, offers, accepted]
        
    

# apps = open_collection("app_listings")

# print ("\n\n\n\nmongo.py: master_df")
# print(master_df)

# for index, row in master_df.iterrows():
#     if not_in_db(row['Link'], apps):
#         apps.insert_one(convert_data_entry(row))
    
# apply("http://redirect.cvrve.me/e36fd103a077bcbda08a?utm_source=ouckah")

def main():
    print(fetch_data_to_dataframe('app_listings'))

if __name__=="__main__":
    main()