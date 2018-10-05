import json
from random import randint

def get_random_user_agent():
    with open("WebSpider/utils/user_agents.json", "r") as f:
        user_agents=json.load(f)
        return user_agents[randint(0, len(user_agents)-1)]
        

if __name__=="__main__":
    print(get_random_user_agent())
