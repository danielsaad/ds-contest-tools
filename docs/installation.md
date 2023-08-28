
# Utilizando o `pip`

Para instalar a ferramenta pelo pip, basta executar o comando abaixo:

```bash
pip install ds-contest-tools
```

# Utilizando o repositório clonado

Para utilizar a ferramenta a partir dos arquivos do repositório, siga os passos abaixo:

- Clone o repositório para o seu diretório local:

```bash
git clone https://github.com/danielsaad/ds-contest-tools.git
```

- Navegue até a pasta raiz do repositório clonado:

```bash
cd ds-contest-tools
```

- Utilize o comando `python3 run.py` seguido dos parâmetros e opções desejados para executar a ferramenta. Por exemplo:

```bash
python3 run.py build -all example
```


# Utilizando o código-fonte

Para instalar a ferramenta a partir do código-fonte, siga os passos abaixo:

1. Instale os pré-requisitos da ferramenta e execute o comando abaixo para instalar os módulos necessários:

```bash
pip install setuptools wheel
```

2. Clone o repositório:

```bash
git clone https://github.com/danielsaad/ds-contest-tools.git
```

3. Na pasta raiz do repositório, execute o comando abaixo para criar o pacote da ferramenta:

```bash
python -m build
```

4. Instale o pacote gerado:

```bash
pip install dist/<nome_do_pacote>.whl
```
