#!/usr/bin/env python

import json

with open("light.json" , "r") as f :
    data=json.load(f)

print(data['Light']['DistantLight'])