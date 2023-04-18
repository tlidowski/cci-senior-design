VALID_YEARS = [2020, 2021]

def validateYears(start, end):
    # Check Existance 
    if not (start and end):
        return False
    
    if int(start) not in VALID_YEARS:
        return False
    if int(end) not in VALID_YEARS:
        return False
    if end < start:
        return False
    return True
    
def validateCity(cityName, dropdownCity):
    print(cityName, dropdownCity)
    return cityName.lower() == dropdownCity.lower()


