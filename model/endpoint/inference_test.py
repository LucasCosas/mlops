import numpy as np

endpoint = 'http://52.177.235.191:80/api/v1/service/myservice2/score' #Replace with your endpoint
key = 'vU2NEhi57JOwSTlYpGtT0co0oBCLUwik' #Replace with your key

import urllib.request
import json
import os

data =  {
            "data" : 
                [[
                    2,
                    -0.2932178066508,
                    -0.796488369553942,
                    -0.0362756945287408,
                    0.249390493938338,
                    0.366121029495651,
                    0.811995216036305,
                    0.0425044669723487,
                    -0.96118896511112,
                    0.114045642480561,
                    -0.774492291956289,
                    0.761536480022156,
                    -0.27771156892704,
                    -0.930571990698816,
                    -0.796691904584296,
                    -0.0960232897438156,
                    -0.12887862848002,
                    -0.961080198315487,
                    0.605167592741799,
                    -0.601748719730827,
                    -0.46062510066285,
                    0.285399402500687,
                    -0.960327550921989,
                    0.0420878626846366,
                    0.208626054271858,
                    -0.54005313048907,
                    0.897769089433188,
                    -0.372639695667982,
                    -0.815240719457652,
                    15.32
                ]]
}


body = str.encode(json.dumps(data))

printable = np.array(json.loads(body)['data'])

headers = {'Content-Type':'application/json', 'Authorization':('Bearer '+ key)}

req = urllib.request.Request(endpoint, body, headers)

try:
    response = urllib.request.urlopen(req)
    result = response.read()
    json_result = json.loads(result)[2:-2]
    print(json_result)
except urllib.error.HTTPError as error:
    print("The request failed with status code: " + str(error.code))

    # Print the headers to help debug
    print(error)
    #print(json.loads(error.read()))