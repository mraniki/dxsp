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
        "talky_settings.toml",
        "settings.toml",
        ".secrets.toml",
        ".op.toml",
    ],
    load_dotenv=True,
    merge_enabled=True,
    environments=True,
    default_env="default",
)
