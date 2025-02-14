# fvenv - Gerenciador Rápido de Ambientes Virtuais Python

`fvenv` é uma ferramenta de linha de comando que simplifica a criação e gerenciamento de ambientes virtuais Python. Ele oferece uma interface interativa amigável e também suporta operações via linha de comando.

## Características

- 🚀 Detecção automática de instalações Python
- 📦 Gerenciamento de pacotes favoritos
- 💾 Cache de instalações para performance
- 🎨 Interface colorida e intuitiva
- ⚡ Modo rápido via linha de comando

## Instalação

```bash
pip install fvenv
```

## Uso

### Modo Interativo

Para iniciar o modo interativo com menu:

```bash
fvenv
```

### Modo Linha de Comando

```bash
# Criar ambiente virtual com Python mais recente
fvenv create meu_env

# Criar ambiente com Python específico
fvenv create meu_env --python 3.9

# Criar ambiente com pacotes
fvenv create meu_env -p numpy pandas matplotlib

# Listar versões Python disponíveis
fvenv list
```

### Opções do Comando Create

```bash
fvenv create <venv_dir> [options]

Opções:
  --python, -py      Versão específica do Python (ex: 3.9)
  --packages, -p     Pacotes para instalar (ex: -p numpy pandas)
```

## Exemplos

1. Criar ambiente virtual básico:
```bash
fvenv create meu_projeto
```

2. Criar ambiente com Python 3.9 e pacotes:
```bash
fvenv create ml_projeto --python 3.9 -p numpy pandas scikit-learn
```

3. Ver versões Python disponíveis:
```bash
fvenv list
```

## Características Detalhadas

### Cache de Instalações
- Mantém cache das instalações Python encontradas
- Atualização automática a cada 24 horas
- Pode ser atualizado manualmente via menu de configurações

### Gerenciamento de Pacotes
- Rastreia pacotes mais utilizados
- Sugere pacotes populares durante a criação
- Histórico pode ser limpo via menu de configurações

### Requirements.txt
- Gerado automaticamente para cada ambiente
- Inclui versões exatas dos pacotes instalados
- Adiciona metadados sobre a criação do ambiente

### Metadados do Ambiente
- Armazena informações sobre a criação do ambiente
- Inclui versão do Python, data de criação e plataforma
- Facilita o rastreamento de ambientes

## Arquivos de Configuração

Os arquivos de configuração são armazenados em `~/.fvenv/`:
- `python_installations_cache.json`: Cache de instalações Python
- `favorite_packages.json`: Histórico de pacotes utilizados

## Requisitos

- Python 3.7+
- Sistema operacional: Windows, Linux ou macOS

## Contribuindo

Contribuições são bem-vindas! Por favor, sinta-se à vontade para enviar pull requests.

## Licença

Este projeto está licenciado sob a MIT License - veja o arquivo LICENSE para detalhes.