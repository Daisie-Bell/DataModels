import json
from pathlib import Path
from Tools import Tools

from svaeva import Svaeva


from icecream import ic

import argparse


class Setup:
    def __init__(self):
        self.tools = Tools()

        self.svaeva = Svaeva()

    def setup(self, setup_file):
        print("Setup start")
        allow_functions = [
            func
            for func in dir(Tools)
            if callable(getattr(Tools, func)) and not func.startswith("__")
        ]
        setup_file = json.loads(open(setup_file+".json", "r").read())
        cash = setup_file["cash"]
        for _ in cash:
            if cash[_] is not None:
                temp = _
                if _.endswith("s"):
                    _ = _.replace(_[-2:], _[-2])
                _ = _.replace("add_", "")
                if _ == "group":
                    _ = "group_config"
                if _ not in ["platform", "model"]:
                    json_data = setup_file[_]
                if temp in allow_functions:
                    action = getattr(self.tools, temp)
                    if len(cash[temp]) > 0:
                        if "add_group" in temp:
                            cash[temp].append(json_data)
                        inset_data = tuple(cash[temp])
                    else:
                        inset_data = cash[temp]
                    if len(inset_data) > 0:
                        print(inset_data)

                        action(*inset_data)
                    else:
                        action(json_data)
                else:
                    print("Function {} not found".format(_))
        print("Setup complete")

    def get_info(self, file):
        for _ in file.read().split("\n"):
            if "self.add_model(" in _:
                yield {
                    "type": "skeleton",
                    "skeleton": _.replace("   ", "")
                    .replace('self.add_model("', "")
                    .replace('")', ""),
                }
            elif "self.load_config(" in _:
                yield {
                    "type": "config",
                    "config": _.replace("   ", "")
                    .replace('self.load_config("', "")
                    .replace('")', ""),
                }

    def build_setup(self, model_name, platform_name):
        self.model_name = model_name
        self.platform_name = platform_name
        file = json.loads(open(f"./DataModel/{model_name}.py", "r"))
        data = self.get_info(file)
        config_build = self.export_skeleton_config(data, {})
        config_build.update({"cash": self.export_platform(platform_name)})
        config_build["cash"].update({"add_model": [model_name]})
        config_build["cash"].update({"add_group": [model_name + platform_name]})
        ic(config_build)  # Print with ic.
        config_build = self.export_wallet(config_build)
        Path("./Output/").mkdir(parents=True, exist_ok=True)
        if "config" not in config_build.keys():
            config_build["cash"]["add_configs"] = None
        open(f"./Output/{model_name}_{platform_name}.json", "w").write(
            json.dumps(config_build)
        )
        print(
            "Please don't forget to add your group_config on [{}]".format(
                f"{model_name}_{platform_name}.json"
            )
        )
        return config_build


    def export_platform(self, platform_name):
        ex_platform = self.svaeva.database.platform(id=platform_name)
        config_chash = {
            "add_platform": [platform_name, ex_platform["pf_prams"]],
            "add_skeletons": [],
            "add_configs": [],
            "add_wallet": [],
        }
        return config_chash

    def export_wallet(self, config_build):
        for api in config_build["skeleton"]:
            key = self.svaeva.multi_api.wallet()
            if api in key["key_wallet"].keys():
                if "wallet" in config_build.keys():
                    config_build["wallet"].update({api: key["key_wallet"][api]})
                else:
                    config_build.update({"wallet": {api: key["key_wallet"][api]}})
            else:
                print(
                    "Please add your wallet key on [{}]".format(
                        f"{self.model_name}_{self.platform_name}.json"
                    )
                )
        return config_build

    def export_skeleton_config(self, data, config_build):
        for _ in data:
            _[_["type"]] = _[_["type"]].replace(" ", "")
            data = self.svaeva.multi_api.__getattribute__(f"{_['type']}")(
                id=_[_["type"]]
            )
            if isinstance(data, list):
                data = data[0]
            del data["date_accessed_timestamp"]
            del data["date_created_timestamp"]
            del data["date_updated_timestamp"]
            if _["type"] == "skeleton":
                if "skeleton" in config_build.keys():
                    config_build["skeleton"].update({_[_["type"]]: data})
                else:
                    config_build.update({"skeleton": {_[_["type"]]: data}})
            elif _["type"] == "config":
                if "config" in config_build.keys():
                    config_build["config"].update({_[_["type"]]: data})
                else:
                    config_build.update({"config": {_[_["type"]]: data}})
        return config_build

def main(args):
    setup = Setup()

    if args.setup:
        if args.config_file_name is None:
            print("Please use -h for help")
        else:
            setup.setup(args.config_file_name)
    elif args.build:
        if args.model_name is None or args.platform_name is None:
            print("Please use -h for help")
        else:
            setup.build_setup(args.model_name, args.platform_name)
    else:
        print("Please use -h for help")

if __name__ == "__main__":
    setup = Setup()
    parser = argparse.ArgumentParser(description="My CLI")

    parser.add_argument("-s", "--setup", action="store_true", help="Setup using a config file")
    parser.add_argument("-c", "--config_file_name", help="The name of the config file")

    parser.add_argument("-b", "--build", action="store_true", help="Build setup")
    parser.add_argument("-m", "--model_name", help="The name of the model")
    parser.add_argument("-p", "--platform_name", help="The name of the platform")

    args = parser.parse_args()
    main(args)
args = parser.parse_args()