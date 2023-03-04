VALID_YEARS = [2020, 2021]

# Needs to be lowercase
VALID_CITIES = [
'philadelphia',
'new york city',
'los angelos',
'chicago',
'austin',
'boston',
'seattle',
'detroit',
'denver',
'baltimore',
'washington dc.',
'charlotte'
]

def validateYears(start, end):
    if int(start) not in VALID_YEARS:
        return False
    if int(end) not in VALID_YEARS:
        return False
    if end < start:
        return False
    return True
    
def validateCity(cityName):
    return cityName.lower() in VALID_CITIES