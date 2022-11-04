from sodapy import Socrata
import pandas as pd

def new_york_api(new_york_app_token):
    client = Socrata("data.cityofnewyork.us", new_york_app_token)
    results = client.get_all("uip8-fykc")
    results_df = pd.DataFrame.from_records(results)
    print(results_df)
