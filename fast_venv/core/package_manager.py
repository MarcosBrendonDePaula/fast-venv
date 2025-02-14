# fast_venv/core/package_manager.py
import json
import os
from typing import Dict, List
from ..config import FAVORITE_PACKAGES_FILE

class PackageManager:
    def __init__(self):
        self.favorite_packages = self.load_favorite_packages()

    def load_favorite_packages(self) -> Dict[str, int]:
        """Carrega pacotes favoritos do arquivo."""
        if os.path.exists(FAVORITE_PACKAGES_FILE):
            try:
                with open(FAVORITE_PACKAGES_FILE, 'r') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def save_favorite_packages(self):
        """Salva pacotes favoritos no arquivo."""
        with open(FAVORITE_PACKAGES_FILE, 'w') as f:
            json.dump(self.favorite_packages, f, indent=4)

    def add_package_usage(self, package: str):
        """Incrementa o contador de uso de um pacote."""
        self.favorite_packages[package] = self.favorite_packages.get(package, 0) + 1
        self.save_favorite_packages()

    def get_popular_packages(self, limit: int = 5) -> List[str]:
        """Retorna os pacotes mais populares."""
        return sorted(self.favorite_packages.items(), 
                     key=lambda x: x[1], 
                     reverse=True)[:limit]

    def clear_package_history(self):
        """Limpa o histórico de pacotes."""
        self.favorite_packages = {}
        self.save_favorite_packages()