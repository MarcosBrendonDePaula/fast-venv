# fast_venv/ui/prompts.py
from typing import List
from rich.table import Table
from rich.prompt import Prompt, Confirm
from ..core.package_manager import PackageManager
from .console import console

def select_packages(package_manager: PackageManager) -> List[str]:
    """Interface para seleção de pacotes."""
    packages = []
    
    # Mostrar pacotes populares
    popular = package_manager.get_popular_packages()
    if popular:
        table = Table(title="Pacotes Populares")
        table.add_column("Pacote", style="cyan")
        table.add_column("Usos", justify="right", style="green")
        
        for package, count in popular:
            table.add_row(package, str(count))
        
        console.print(table)
        
        # Perguntar se quer instalar algum dos populares
        for package, _ in popular:
            if Confirm.ask(f"Deseja instalar {package}?"):
                packages.append(package)
    
    # Adicionar pacotes manualmente
    while Confirm.ask("Deseja adicionar mais pacotes?"):
        package = Prompt.ask("Nome do pacote")
        if package:
            packages.append(package)
    
    return packages