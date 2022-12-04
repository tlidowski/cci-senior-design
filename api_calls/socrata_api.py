from sodapy import Socrata
import pandas as pd


def socrata_source_all(app_token, data_link, data_id):
    client = Socrata(data_link, app_token)
    results = client.get_all(data_id)
    results_df = pd.DataFrame.from_records(results)
    print(results_df)


def socrata_source_zip_code(app_token, data_link, data_id, zip):
    client = Socrata(data_link, app_token)
    results = client.get(data_id, where="zip_code=" + str(zip))
    results_df = pd.DataFrame.from_records(results)
    print(results_df)
