import os
import pandas as pd

DEFAULT_HEADER = {'Content-Type': 'application/json'}

SB_KEY_LIST = list(pd.read_excel("Social Researcher-KEY.xlsx")['User Key'])
#["7a8ffcb1f29c9f713d0334c599e1c580", "938b641f6e86d92bccc6f68fbb72502a", "dfe2c5188c942084a7c81092ac18da73", "22574159d516e79dc742120daef00ed6", "fc6ce661d51a4cb252ea4249f3818837", "a6c10d7ae390407859e312061ea59114"]

# 800: 7a8ffcb1f29c9f713d0334c599e1c580
# 400: 938b641f6e86d92bccc6f68fbb72502a
# 100: fc6ce661d51a4cb252ea4249f3818837, dfe2c5188c942084a7c81092ac18da73, "a6c10d7ae390407859e312061ea59114", "22574159d516e79dc742120daef00ed6"]


SB_KEY = os.getenv('SB_KEY', "dfe2c5188c942084a7c81092ac18da73")
SB_NETWORK= os.getenv('SB_NETWORK', "facebook")

SB_URL_TEMPLATE = "https://api.social-searcher.com/v2/users?q=\"{}\"&key={}&network={}"

NAME_LIST_FILE = os.getenv('NAME_LIST_FILE', "fb_name_all.txt")

SKIP_START_FLAG = int(os.getenv('SKIP_START_FLAG', "1"))
START_LINE_COUNT = int(os.getenv('START_LINE_COUNT', "3223"))
START_LINE_COUNT_FILE = "number2.txt"


SKIP_END_FLAG = int(os.getenv('SKIP_END_FLAG', "0"))
FINISH_LINE_COUNT = int(os.getenv('FINISH_LINE_COUNT', "550"))

MAX_GET_COUNT_FLAG = int(os.getenv('MAX_GET_COUNT_FLAG', "0"))
MAX_GET_LINE_COUNT = int(os.getenv('MAX_GET_LINE_COUNT', "50"))