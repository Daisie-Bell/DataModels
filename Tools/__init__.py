import json
from typing import Any

from svaeva import Svaeva

from dotenv import load_dotenv

import logging

import os

load_dotenv()
class Tools:

    def __init__(self) -> None:
        self.svaeva = Svaeva()
        # start Logging file

        logg = logging.getLogger("svaeva")
        logg.setLevel(logging.DEBUG)
        self.formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        self.fh = logging.FileHandler("svaeva.log")


    def add_platform(self,platform_name,data):
        try:
            logging.info("Adding platform {} with data {}".format(platform_name,data))
            self.svaeva.database.platform.__setattr__(platform_name, data)
        except Exception as e:
            logging.error("Error adding platform {} with data {} : {}".format(platform_name,data,e))
            #return False
            

    def add_skeletons(self,json_input):
        for row in json_input:
            try:
                self.svaeva.multi_api.skeleton.__setattr__(row,json_input[row])
            except Exception as e:
                logging.error("Error adding skeleton {} with data {} : {}".format(row,json_input[row],e))
                #return False

    def add_configs(self,json_input):
        for row in json_input:
            try:
                logging.info("Adding config {} with data {}".format(row,json_input[row]))
                self.svaeva.multi_api.config.__setattr__(row,json_input[row])
            except Exception as e:
                logging.error("Error adding config {} with data {} : {}".format(row,json_input[row],e))
                #return False
            
    def add_wallet(self,json_input):
        #wallets = self.svaeva.multi_api.wallet()
        #print(wallets)
        wallets = {"key_wallet":{}}
        for row in json_input:
            try:
                if row not in wallets["key_wallet"]:
                    logging.info("Adding wallet {} with data {}".format(row,json_input[row]))
                    self.svaeva.multi_api.wallet.add_key(row,json_input[row])
                else:
                    logging.info("Key already setted!")
            except Exception as e:
                logging.error("Error adding wallet {} with data {} : {}".format(row,json_input[row],e))
                #return False

    def add_model(self,model_name):
        input_dict = {
            "model_type" : "text2text voice2voice",
            "row_code" : open(f"./DataModel/{model_name}.py","r").read()
        }
        try:
            logging.info("Adding model {}".format(model_name))
            self.svaeva.multi_api.virtual.__setattr__(model_name, input_dict)
        except Exception as e:
            logging.error("Error adding model {} : {}".format(model_name,e))
            return False
        
    def add_group(self,name,json_i):
        try:
            logging.info("Adding group {}".format(name))
            self.svaeva.database.group.__setattr__(name, json_i)
        except Exception as e:
            logging.error("Error adding group {} : {}".format(name,e))
            return False