from setuptools import setup, find_packages

setup(
    name="fvenv",  # Nome do pacote no pip
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "rich>=10.0.0"
    ],
    entry_points={
        'console_scripts': [
            'fvenv=fast_venv.main:main',  # Comando será 'fvenv'
        ],
    },
    author="Seu Nome",
    author_email="seu.email@exemplo.com",
    description="Um gerenciador de ambientes virtuais Python rápido e fácil",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/seu-usuario/fast-venv",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)