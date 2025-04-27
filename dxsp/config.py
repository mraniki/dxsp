"""
 DEX SWAP CONFIG
"""
import os

from dynaconf import Dynaconf

# Define the root path of the project library
ROOT = os.path.dirname(__file__)
# Define the library's internal default settings path
DEFAULT_SETTINGS_PATH = os.path.join(ROOT, "default_settings.toml")

# --- Start Modification ---
# Check for the application's config directory via environment variable
# e.g., /app or ./ if run locally from tt root
APP_CONFIG_DIR = os.environ.get("TT_CONFIG_DIR")

# Construct paths to app/user config files if the directory is specified
talky_settings_path = None
user_settings_path = None
secrets_path = None
op_path = None

if APP_CONFIG_DIR and os.path.isdir(APP_CONFIG_DIR):
    print(f"DXSP Config: Found TT_CONFIG_DIR: {APP_CONFIG_DIR}")
    # Use the specific name tt expects for its default settings
    talky_settings_path = os.path.join(APP_CONFIG_DIR, "tt", "talky_settings.toml")
    user_settings_path = os.path.join(APP_CONFIG_DIR, "settings.toml")
    secrets_path = os.path.join(APP_CONFIG_DIR, ".secrets.toml")
    op_path = os.path.join(APP_CONFIG_DIR, ".op.toml") # If this lib also reads this
else:
    print(
        f"DXSP Config: TT_CONFIG_DIR not set or invalid "
        f"('{APP_CONFIG_DIR}'). Relying on library defaults."
    )

# Build the settings_files list dynamically
# Order: Library Default < TT Default < User Settings < User Secrets
settings_files = []
if os.path.exists(DEFAULT_SETTINGS_PATH):
    settings_files.append(DEFAULT_SETTINGS_PATH)
else:
    print(
        f"DXSP Config: Warning - Library default not found "
        f"at {DEFAULT_SETTINGS_PATH}"
    )

if talky_settings_path and os.path.exists(talky_settings_path):
    settings_files.append(talky_settings_path)
if user_settings_path and os.path.exists(user_settings_path):
    settings_files.append(user_settings_path)
if secrets_path and os.path.exists(secrets_path):
    settings_files.append(secrets_path)
if op_path and os.path.exists(op_path):
    settings_files.append(op_path)

print(f"DXSP Config: Loading settings from: {settings_files}")
# --- End Modification ---

# Load the settings using the constructed list
settings = Dynaconf(
    envvar_prefix="TT",
    root_path=os.path.dirname(ROOT),
    settings_files=settings_files, # Use the dynamically built list
    load_dotenv=True,
    merge_enabled=True,
    environments=True,
    default_env="default",
)
