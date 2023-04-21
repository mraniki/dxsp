
from dynaconf import Dynaconf

settings = Dynaconf(
    envvar_prefix="DXSP",
    settings_files=['core.toml','settings.toml', '.secrets.toml'],
)
