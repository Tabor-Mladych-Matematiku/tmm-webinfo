from yaml import load
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

with open("tmm_webinfo.yaml", "r") as file:
    config = load(file, Loader)
