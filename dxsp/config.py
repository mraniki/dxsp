"""
 DEX SWAP CONFIG
"""
import os
from dynaconf import Dynaconf

ROOT = os.path.dirname(__file__)

settings = Dynaconf(
    envvar_prefix="DXSP",
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
