from api_calls import baltimore_parser, charlotte_parser, dc_parser, fbi_api
import pandas as pd


if __name__ == "__main__":
    pd.set_option('display.max_columns', None)
    #get_city_crime_data("2020", "2021", "BALTIMORE")

    # TESTING API CALLS
    # def testFbiApi():
    # apiKey = "?API_KEY=zZAJhHKFBdhY3xduUAUS9uGtLrnnc33EwMIgdCcz"
    # fbi_api.national_crime_estimate_to_from_year(2019, 2022, apiKey)
    #
    # token_socrata = 'T8kdBcPaIk15Bhose4cO3MDdH'
    # new_york_api_key_secret = 'ebmbopds1rxknoxawdvv59301damceco2420hyoo7lm0ejz98'
    # new_york_api_key_id = '3mctpgwecml66r6fig75s7r7r'
    # new_york_data_id = "uip8-fykc"
    # new_york_data_link = "data.cityofnewyork.us"
    # austin_link = 'data.austintexas.gov'
    # austin_id = "fdj4-gpfu"
    # socrata_api_call.socrata_source_zip_code(token_socrata, austin_link, austin_id, 76574)
    # socrata_api_call.socrata_source_all(token_socrata, new_york_data_link, new_york_data_id)
    #
    # philadelphia_parser.philadelphia_data_by_year("2018")
    # charlotte_parser.charlotte_incident_reports()
    # dc_parser.dc_crime_2022()
    # baltimore_parser.baltimore_crime()
