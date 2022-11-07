import json
from urllib.request import Request, urlopen


def pheonix_crime_by_zip(zip):
    url = f'https://www.phoenixopendata.com/api/3/action/datastore_search?resource_id=0ce3411a-2fc6-4302-a33f-167f68608a20&q={zip}'  
    req = Request(
        url = url,
        headers={'User-Agent': 'Mozilla/5.0'}
    )
    fileobj = urlopen(req).read()
    response_dict = json.loads(fileobj)
    print(response_dict)

pheonix_crime_by_zip(85042)
#pheonix_crime_by_zip(85029)