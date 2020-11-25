from crawlers.emed import PortfolioCrawler
from getpass import getpass

import json
import os

if __name__ == "__main__":
    if not os.path.exists("login_settings.json"):
        username = input("Please enter your zID/username (z1234567): ")
        password = getpass("Please enter your password: ")
        my_settings = dict(username=username, password=password)
        with open("login_settings.json", "w") as ofp:
            json.dump(my_settings, ofp)
    pc = PortfolioCrawler()
    with pc as dl_ifp:
        pc.download_all()
    os.remove("login_settings.json")