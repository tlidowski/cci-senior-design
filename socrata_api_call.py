from sodapy import Socrata
import pandas as pd


def socrata_source_all(app_token, data_link, data_id):
    client = Socrata(data_link, app_token)
    results = client.get_all(data_id)
    results_df = pd.DataFrame.from_records(results)
    print(results_df)
