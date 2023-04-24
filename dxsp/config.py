
from dynaconf import Dynaconf

settings = Dynaconf(
    envvar_prefix="DXSP",
    settings_files=['core.toml','settings.toml', '.secrets.toml'],
    load_dotenv=True,
    environments=True,
    default_env="default",
)
