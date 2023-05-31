"""
 DEX SWAP CONFIG
"""
import os
from dynaconf import Dynaconf

ROOT = os.path.dirname(__file__)

settings = Dynaconf(
    envvar_prefix="TT",
    root_path=os.path.dirname(ROOT),
    settings_files=[
        os.path.join(ROOT, "default_settings.toml"),
        'settings.toml',
        '.secrets.toml'
    ],
    load_dotenv=True,
    environments=True,
    default_env="default",
)

if settings.loglevel == "DEBUG":
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    #logging.getLogger("ccxt").setLevel(logging.WARNING)
    