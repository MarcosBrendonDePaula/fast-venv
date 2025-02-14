# Estrutura corrigida

# fast_venv/ui/menus.py
import os
import webbrowser
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table
from .console import console
from ..config import CACHE_FILE, FAVORITE_PACKAGES_FILE

def show_menu() -> str:
    """Mostra o menu principal."""
    console.print(Panel.fit(
        "[bold cyan]Python Virtual Environment Manager[/bold cyan]\n",
        title="Bem-vindo",
        border_style="blue"
    ))
    
    options = [
        "1. Criar novo ambiente virtual",
        "2. Ver pacotes populares",
        "3. Configurações",
        "4. Sair"
    ]
    
    for option in options:
        console.print(option)
    
    return Prompt.ask(
        "\nEscolha uma opção",
        choices=["1", "2", "3", "4"],
        default="1"
    )

def open_config_file(file_path: str):
    """Abre um arquivo de configuração."""
    try:
        if os.name == "nt":
            os.startfile(file_path)
        else:
            webbrowser.open(f"file://{file_path}")
    except Exception as e:
        console.print(f"[red]Erro ao abrir arquivo: {e}[/red]")

def show_config_menu(manager):
    """Mostra o menu de configurações."""
    console.print(Panel.fit(
        "[bold cyan]Configurações[/bold cyan]\n",
        title="Menu de Configurações",
        border_style="blue"
    ))
    
    options = [
        "1. Abrir arquivo de cache de instalações",
        "2. Abrir arquivo de pacotes favoritos",
        "3. Limpar histórico de pacotes",
        "4. Atualizar cache de instalações Python",
        "5. Voltar"
    ]
    
    for option in options:
        console.print(option)
    
    choice = Prompt.ask(
        "\nEscolha uma opção",
        choices=["1", "2", "3", "4", "5"],
        default="5"
    )

    if choice == "1":
        open_config_file(CACHE_FILE)
    elif choice == "2":
        open_config_file(FAVORITE_PACKAGES_FILE)
    elif choice == "3":
        if Confirm.ask("Tem certeza que deseja limpar o histórico de pacotes?"):
            manager.package_manager.clear_package_history()
            console.print("[green]Histórico de pacotes limpo com sucesso![/green]")
    elif choice == "4":
        manager.find_python_installations()
        console.print("[green]Cache atualizado com sucesso![/green]")