import json
from pprintpp import pprint


file_reader = open("./output/陳.txt", "r")

for line in file_reader:
    data_json = json.loads(line.rstrip("\n"))

    pprint(data_json)