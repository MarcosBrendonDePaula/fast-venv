# fast_venv/config.py
import os

# Configurações
CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".fvenv")
CACHE_FILE = os.path.join(CONFIG_DIR, "python_installations_cache.json")
FAVORITE_PACKAGES_FILE = os.path.join(CONFIG_DIR, "favorite_packages.json")
DEFAULT_PACKAGES = ["pip", "wheel", "setuptools"]

# Criar diretório de configuração se não existir
os.makedirs(CONFIG_DIR, exist_ok=True)