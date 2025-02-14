# fast_venv/core/venv_manager.py
import os
import subprocess
import json
import glob
import time
import shutil
from typing import List, Optional
import platform
from datetime import datetime
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt

from ..config import CACHE_FILE, DEFAULT_PACKAGES
from ..ui.console import console
from .python_installation import PythonInstallation
from .package_manager import PackageManager

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
                with open(CACHE_FILE, 'r') as f:
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
            with open(CACHE_FILE, 'w') as f:
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
                cmd = [python_inst.executable, "-m", "venv", "--upgrade-deps", venv_dir]
                subprocess.run(cmd, check=True, capture_output=True)
                progress.update(task1, advance=60)

                # Verificar se o pip está funcionando
                pip_exec = self._get_pip_path(venv_dir)
                try:
                    subprocess.run([pip_exec, "--version"], 
                                 check=True, capture_output=True)
                except subprocess.CalledProcessError:
                    if os.name == "nt":
                        # No Windows, tente usar python -m pip
                        pip_exec = [os.path.join(venv_dir, "Scripts", "python.exe"), "-m", "pip"]
                    else:
                        pip_exec = [os.path.join(venv_dir, "bin", "python"), "-m", "pip"]

                installed_packages = []

                # Instalar requisitos adicionais
                if requirements:
                    for package in requirements:
                        try:
                            if isinstance(pip_exec, list):
                                subprocess.run([*pip_exec, "install", package], 
                                            check=True, capture_output=True)
                            else:
                                subprocess.run([pip_exec, "install", package], 
                                            check=True, capture_output=True)
                            installed_packages.append(package)
                            self.package_manager.add_package_usage(package)
                        except subprocess.CalledProcessError as e:
                            console.print(f"[yellow]Aviso:[/yellow] Erro ao instalar {package}: {e}")
                            continue

                progress.update(task1, advance=20)

                # Criar requirements.txt
                self._create_requirements(venv_dir, installed_packages)

                # Criar arquivo de metadados
                self._create_metadata(venv_dir, python_inst)

                progress.update(task1, advance=20)

                console.print("[green]✓[/green] Ambiente virtual criado com sucesso!")

            except subprocess.CalledProcessError as e:
                console.print(f"[red]Erro ao criar ambiente virtual: {e}[/red]")
                if os.path.exists(venv_dir):
                    shutil.rmtree(venv_dir)
                raise

    def _get_pip_path(self, venv_dir: str) -> str:
        """Retorna o caminho do executável pip no ambiente virtual."""
        if os.name == "nt":
            return os.path.join(venv_dir, "Scripts", "pip.exe")
        return os.path.join(venv_dir, "bin", "pip")

    def _create_requirements(self, venv_dir: str, packages: List[str]):
        """Cria o arquivo requirements.txt."""
        requirements_file = os.path.join(venv_dir, "requirements.txt")
        
        try:
            # Pegar as versões exatas dos pacotes instalados
            pip_exec = self._get_pip_path(venv_dir)
            if isinstance(pip_exec, list):
                result = subprocess.run([*pip_exec, "freeze"], 
                                     capture_output=True, text=True, check=True)
            else:
                result = subprocess.run([pip_exec, "freeze"], 
                                     capture_output=True, text=True, check=True)
            
            # Filtrar apenas os pacotes que foram instalados explicitamente
            installed = result.stdout.strip().split('\n')
            package_map = {p.split('==')[0].lower(): p for p in installed}
            
            requirements = []
            for package in packages:
                if package.lower() in package_map:
                    requirements.append(package_map[package.lower()])
                else:
                    requirements.append(package)

            # Escrever o arquivo requirements.txt
            with open(requirements_file, 'w') as f:
                f.write("# Pacotes instalados durante a criação do ambiente virtual\n")
                f.write("# Criado por fast-venv em " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n\n")
                f.write('\n'.join(sorted(requirements)))
                
            console.print(f"[green]✓[/green] Arquivo requirements.txt criado em {requirements_file}")
            
        except Exception as e:
            console.print(f"[yellow]Aviso:[/yellow] Erro ao criar requirements.txt: {e}")

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