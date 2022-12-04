import philadelphia_parser
import fbi_api
import dc_parser
import baltimore_parser
import charlotte_parser
import socrata_api_call
import pandas as pd

def testFbiApi():
   apiKey = "?API_KEY=zZAJhHKFBdhY3xduUAUS9uGtLrnnc33EwMIgdCcz"
   fbi_api.national_crime_estimate_to_from_year(2019, 2022, apiKey)

def testDcParser():
   dc_parser.dc_crime_2022()

def testBaltimoreParser():
   baltimore_parser.baltimore_crime()

def testCharlotteParser():
   charlotte_parser.charlotte_incident_reports()
   #charlotte_parser.charlotte_violent_crime()


def apply_mask(df, column_name, value):
   mask = (df[column_name] == value)
   # apply mask to result
   res = df[mask]
   return res



def get_city_crime_data(start_year, end_year, city_name):

   path_2020 = f'combined_city_data/city_data-{2020}.csv'
   path_2021 = f'combined_city_data/city_data-{2021}.csv'

   column_types = {
      'CITY_NAME':'object',
      'STATE_NAME':'object',
      'CRIME_CODE':'object',
      'CRIME_DESCRIPTION':'object',
      'DATE_REPORTED':'object',
      'DATE_OCCURRED':'object',
      'LATITUDE':'float64',
      'LONGITUDE':'float64',
      'DATE_FORMAT':'object'
   }

   year_csvs={"2020": path_2020,
              "2021": path_2021
              }

   if (start_year in year_csvs.keys()) and (end_year in year_csvs.keys()):
      start_year_df = pd.read_csv(year_csvs[start_year],
                                  dtype=column_types
      )
      start_year_res = apply_mask(start_year_df, 'CITY_NAME', city_name)

      end_year_df = []
      end_year_res = []

      if (start_year != end_year):
         end_year_df = pd.read_csv(year_csvs[end_year],
                                   dtype=column_types)
         end_year_res = apply_mask(end_year_df, 'CITY_NAME', city_name)

      res = None
      if (len(end_year_res) != 0):
         res = pd.concat([start_year_res, end_year_res], axis=0)
      else:
         res = start_year_res

      print(res)


if __name__ == "__main__":
   pd.set_option('display.max_columns', None)

   token_socrata = 'T8kdBcPaIk15Bhose4cO3MDdH'

   new_york_api_key_secret = 'ebmbopds1rxknoxawdvv59301damceco2420hyoo7lm0ejz98'
   new_york_api_key_id = '3mctpgwecml66r6fig75s7r7r'
   new_york_data_id = "uip8-fykc"
   new_york_data_link = "data.cityofnewyork.us"


   austin_link = 'data.austintexas.gov'
   austin_id = "fdj4-gpfu"
   #socrata_api_call.socrata_source_zip_code(token_socrata, austin_link, austin_id, 76574)
   #socrata_api_call.socrata_source_all(token_socrata, new_york_data_link, new_york_data_id)

   #philadelphia_parser.philadelphia_data_by_year("2018")
   #testCharlotteParser()
   #testDcParser()
   # print("============================= BALTIMORE =============================")
   # print("\n")
   #testBaltimoreParser()

   get_city_crime_data("2020", "2021", "BALTIMORE")


