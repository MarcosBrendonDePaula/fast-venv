# fast_venv/main.py
import os
import sys
from rich.table import Table
from rich.prompt import Prompt

# Adiciona o diretório pai ao path para permitir importações relativas
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fast_venv.core.venv_manager import VenvManager
from fast_venv.ui.console import console
from fast_venv.ui.menus import show_menu, show_config_menu
from fast_venv.ui.prompts import select_packages
from fast_venv.cli import main_cli

def main_interactive():
    """Função principal para interface interativa."""
    manager = VenvManager()
    
    while True:
        choice = show_menu()
        
        if choice == "1":
            # Selecionar versão do Python
            python_inst = manager.show_python_versions()
            if not python_inst:
                continue

            # Nome do ambiente
            venv_dir = Prompt.ask("Nome/diretório para o ambiente virtual")
            if os.path.exists(venv_dir):
                console.print("[red]Diretório já existe. Escolha outro nome.[/red]")
                continue

            # Selecionar pacotes
            packages = select_packages(manager.package_manager)

            try:
                # Criar ambiente
                manager.create_venv(python_inst, venv_dir, packages)
                
                # Mostrar instruções de ativação
                manager.show_activation_instructions(venv_dir)
            except Exception as e:
                console.print(f"[red]Erro ao criar ambiente virtual: {e}[/red]")

        elif choice == "2":
            # Mostrar pacotes populares
            popular = manager.package_manager.get_popular_packages()
            if not popular:
                console.print("[yellow]Ainda não há pacotes instalados.[/yellow]")
                continue
                
            table = Table(title="Pacotes Mais Populares")
            table.add_column("Pacote", style="cyan")
            table.add_column("Usos", justify="right", style="green")
            
            for package, count in popular:
                table.add_row(package, str(count))
            
            console.print(table)
            Prompt.ask("\nPressione Enter para continuar")

        elif choice == "3":
            # Menu de configurações
            show_config_menu(manager)

        else:  # choice == "4"
            console.print("[green]Até logo![/green]")
            break

def main():
    """Função principal que gerencia tanto o modo CLI quanto o interativo."""
    try:
        # Verificar se há argumentos de linha de comando
        if len(sys.argv) > 1:
            main_cli()
        else:
            main_interactive()
    except KeyboardInterrupt:
        console.print("\n[yellow]Operação cancelada pelo usuário.[/yellow]")
        sys.exit(1)

if __name__ == "__main__":
    main()