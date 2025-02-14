#!/usr/bin/env python3
import os
import sys
import subprocess
import json
import glob
import time
from typing import List, Dict, Optional
import platform
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.markdown import Markdown

# Configurações
CACHE_FILE = ".python_installations_cache.json"
FAVORITE_PACKAGES_FILE = ".favorite_packages.json"
REQUIREMENTS_FILE = "requirements.txt"
DEFAULT_PACKAGES = ["pip", "wheel", "setuptools"]

console = Console()

class PythonInstallation:
    def __init__(self, version: str, executable: str):
        self.version = version
        self.executable = executable
        self.major_version = int(version.split('.')[0])
        self.minor_version = int(version.split('.')[1])

    def to_dict(self) -> dict:
        return {
            "version": self.version,
            "executable": self.executable
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'PythonInstallation':
        return cls(data["version"], data["executable"])

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

class VenvManager:
    def __init__(self):
        self.installations: List[PythonInstallation] = []
        self.package_manager = PackageManager()
        self.load_installations()

    def load_installations(self):
        """Carrega instalações do cache ou realiza nova busca."""
        cached_data = self._load_cache()
        if cached_data and (time.time() - cached_data.get("last_updated", 0)) < 86400:  # 24 horas
            self.installations = [PythonInstallation.from_dict(inst) for inst in cached_data.get("installations", [])]
        else:
            self.find_python_installations()

    def _load_cache(self) -> Optional[dict]:
        """Carrega o cache de instalações."""
        if os.path.exists(CACHE_FILE):
            try:
                with open(CACHE_FILE, "r") as f:
                    return json.load(f)
            except Exception as e:
                console.print(f"[yellow]Aviso:[/yellow] Erro ao carregar cache: {e}")
        return None

    def _save_cache(self):
        """Salva as instalações no cache."""
        data = {
            "installations": [inst.to_dict() for inst in self.installations],
            "last_updated": time.time()
        }
        try:
            with open(CACHE_FILE, "w") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            console.print(f"[yellow]Aviso:[/yellow] Erro ao salvar cache: {e}")

    def find_python_installations(self):
        """Procura por instalações do Python no sistema."""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Procurando instalações do Python...", total=None)
            
            self.installations = []
            seen_paths = set()

            path_dirs = os.environ.get("PATH", "").split(os.pathsep)
            for directory in path_dirs:
                if not os.path.exists(directory):
                    continue

                pattern = os.path.join(directory, "python*")
                for file_path in glob.glob(pattern):
                    if os.path.isdir(file_path) or file_path in seen_paths:
                        continue
                    
                    if os.access(file_path, os.X_OK):
                        try:
                            result = subprocess.run(
                                [file_path, "--version"],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                text=True,
                                timeout=2
                            )
                            output = result.stdout.strip() or result.stderr.strip()
                            
                            if output.startswith("Python"):
                                version = output.split()[1]
                                seen_paths.add(file_path)
                                inst = PythonInstallation(version, os.path.abspath(file_path))
                                self.installations.append(inst)
                        except Exception:
                            continue

            progress.update(task, completed=True)
            self._save_cache()

    def show_python_versions(self) -> Optional[PythonInstallation]:
        """Mostra menu de seleção de versões do Python."""
        if not self.installations:
            console.print("[red]Nenhuma instalação do Python encontrada![/red]")
            return None

        table = Table(title="Instalações do Python Disponíveis")
        table.add_column("Opção", justify="right", style="cyan")
        table.add_column("Versão", style="green")
        table.add_column("Caminho", style="blue")

        for idx, inst in enumerate(self.installations, start=1):
            table.add_row(str(idx), f"Python {inst.version}", inst.executable)

        console.print(table)

        while True:
            try:
                choice = Prompt.ask(
                    "Selecione o número da versão",
                    choices=[str(i) for i in range(1, len(self.installations) + 1)]
                )
                return self.installations[int(choice) - 1]
            except (ValueError, IndexError):
                console.print("[red]Opção inválida![/red]")

    def create_venv(self, python_inst: PythonInstallation, venv_dir: str, 
                   requirements: Optional[List[str]] = None):
        """Cria e configura um ambiente virtual."""
        with Progress(console=console) as progress:
            task1 = progress.add_task("Criando ambiente virtual...", total=100)
            
            try:
                # Criar o ambiente virtual
                cmd = [python_inst.executable, "-m", "venv", venv_dir]
                subprocess.run(cmd, check=True, capture_output=True)
                progress.update(task1, advance=50)

                # Atualizar pip e instalar pacotes básicos
                pip_exec = self._get_pip_path(venv_dir)
                for package in DEFAULT_PACKAGES:
                    subprocess.run([pip_exec, "install", "--upgrade", package], 
                                 check=True, capture_output=True)

                progress.update(task1, advance=25)

                # Instalar requisitos adicionais
                if requirements:
                    for package in requirements:
                        subprocess.run([pip_exec, "install", package], 
                                     check=True, capture_output=True)
                        self.package_manager.add_package_usage(package)

                progress.update(task1, advance=25)

                # Criar arquivo de metadados
                self._create_metadata(venv_dir, python_inst)

                console.print("[green]✓[/green] Ambiente virtual criado com sucesso!")

            except subprocess.CalledProcessError as e:
                console.print(f"[red]Erro ao criar ambiente virtual: {e}[/red]")
                if os.path.exists(venv_dir):
                    import shutil
                    shutil.rmtree(venv_dir)
                sys.exit(1)

    def _get_pip_path(self, venv_dir: str) -> str:
        """Retorna o caminho do executável pip no ambiente virtual."""
        if os.name == "nt":
            return os.path.join(venv_dir, "Scripts", "pip.exe")
        return os.path.join(venv_dir, "bin", "pip")

    def _create_metadata(self, venv_dir: str, python_inst: PythonInstallation):
        """Cria arquivo de metadados do ambiente."""
        metadata = {
            "created_at": datetime.now().isoformat(),
            "python_version": python_inst.version,
            "python_path": python_inst.executable,
            "platform": platform.platform(),
            "creator": "venv-manager"
        }
        
        metadata_file = os.path.join(venv_dir, ".venv-metadata.json")
        with open(metadata_file, "w") as f:
            json.dump(metadata, f, indent=4)

    def show_activation_instructions(self, venv_dir: str):
        """Mostra instruções de ativação do ambiente virtual."""
        console.print("\n[bold green]Ambiente virtual criado com sucesso![/bold green]")
        
        if os.name == "nt":
            activate_cmd = f"{venv_dir}\\Scripts\\activate.bat"
            console.print(Panel(f"""
Para ativar o ambiente virtual, execute:

[bold cyan]cd {venv_dir}
{activate_cmd}[/bold cyan]

Para desativar, simplesmente digite: [bold cyan]deactivate[/bold cyan]
"""))
        else:
            activate_cmd = f"source {venv_dir}/bin/activate"
            console.print(Panel(f"""
Para ativar o ambiente virtual, execute:

[bold cyan]cd {venv_dir}
{activate_cmd}[/bold cyan]

Para desativar, simplesmente digite: [bold cyan]deactivate[/bold cyan]
"""))

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
        "3. Sair"
    ]
    
    for option in options:
        console.print(option)
    
    return Prompt.ask(
        "\nEscolha uma opção",
        choices=["1", "2", "3"],
        default="1"
    )

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

def main():
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

            # Criar ambiente
            manager.create_venv(python_inst, venv_dir, packages)
            
            # Mostrar instruções de ativação
            manager.show_activation_instructions(venv_dir)

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

        else:  # choice == "3"
            console.print("[green]Até logo![/green]")
            break

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]Operação cancelada pelo usuário.[/yellow]")
        sys.exit(1)