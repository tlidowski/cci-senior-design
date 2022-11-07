import philadelphia_parser
import fbi_api
import dc_parser
import baltimore_parser

def testFbiApi():
   apiKey = "?API_KEY=zZAJhHKFBdhY3xduUAUS9uGtLrnnc33EwMIgdCcz"
   fbi_api.national_crime_estimate_to_from_year(2019, 2022, apiKey)

def testDcParser():
   dc_parser.dc_crime_2022()

def testBaltimoreParser():
   baltimore_parser.baltimore_crime()

if __name__ == "__main__":
   # testDcParser()
   print("============================= BALTIMORE =============================")
   print("\n")
   testBaltimoreParser()


