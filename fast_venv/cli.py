# fast_venv/cli.py
import argparse
import sys
from typing import List, Optional
from .core.venv_manager import VenvManager
from .ui.console import console

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Gerenciador rápido de ambientes virtuais Python",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  # Criar venv com Python mais recente
  fvenv create meu_env
  
  # Criar venv com Python específico
  fvenv create meu_env --python 3.9
  
  # Criar venv com pacotes
  fvenv create meu_env -p numpy pandas matplotlib
  
  # Listar versões Python disponíveis
  fvenv list
"""
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Comandos disponíveis')
    
    # Comando create
    create_parser = subparsers.add_parser('create', help='Criar novo ambiente virtual')
    create_parser.add_argument('venv_dir', help='Nome/diretório do ambiente virtual')
    create_parser.add_argument('--python', '-py', 
                              help='Versão específica do Python (ex: 3.9)')
    create_parser.add_argument('--packages', '-p', nargs='+',
                              help='Pacotes para instalar')
    
    # Comando list
    list_parser = subparsers.add_parser('list', help='Listar versões Python disponíveis')
    
    return parser.parse_args()

def find_python_version(manager: VenvManager, version: str) -> Optional[str]:
    """Encontra instalação do Python que corresponde à versão especificada."""
    for inst in manager.installations:
        if inst.version.startswith(version):
            return inst
    return None

def cli_create_venv(manager: VenvManager, venv_dir: str, 
                   python_version: Optional[str] = None,
                   packages: Optional[List[str]] = None):
    """Cria ambiente virtual via CLI."""
    try:
        # Selecionar versão do Python
        if python_version:
            python_inst = find_python_version(manager, python_version)
            if not python_inst:
                console.print(f"[red]Versão Python {python_version} não encontrada![/red]")
                available = "\n".join(f"- Python {inst.version}" 
                                    for inst in manager.installations)
                console.print(f"\nVersões disponíveis:\n{available}")
                sys.exit(1)
        else:
            # Usar a versão mais recente
            python_inst = sorted(manager.installations, 
                               key=lambda x: (x.major_version, x.minor_version),
                               reverse=True)[0]
        
        # Criar ambiente
        console.print(f"[green]Usando Python {python_inst.version}[/green]")
        manager.create_venv(python_inst, venv_dir, packages)
        
        # Mostrar instruções de ativação
        manager.show_activation_instructions(venv_dir)
        
    except Exception as e:
        console.print(f"[red]Erro ao criar ambiente virtual: {e}[/red]")
        sys.exit(1)

def cli_list_versions(manager: VenvManager):
    """Lista versões Python disponíveis."""
    if not manager.installations:
        console.print("[red]Nenhuma instalação do Python encontrada![/red]")
        sys.exit(1)
        
    console.print("\n[bold]Versões Python disponíveis:[/bold]")
    for inst in sorted(manager.installations, 
                      key=lambda x: (x.major_version, x.minor_version),
                      reverse=True):
        console.print(f"Python {inst.version} - {inst.executable}")

def main_cli():
    """Função principal para interface de linha de comando."""
    args = parse_args()
    manager = VenvManager()
    
    if args.command == 'create':
        cli_create_venv(manager, args.venv_dir, args.python, args.packages)
    elif args.command == 'list':
        cli_list_versions(manager)
    else:
        console.print("[red]Comando inválido! Use --help para ver os comandos disponíveis.[/red]")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main_cli()
    except KeyboardInterrupt:
        console.print("\n[yellow]Operação cancelada pelo usuário.[/yellow]")
        sys.exit(1)