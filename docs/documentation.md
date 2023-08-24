# Documentação da ferramenta

Essa documentação tem como objetivo apresentar como a ferramenta foi pensada e estruturada, além de explicar sobre o funcionamento dos módulos, arquivos e comandos da ferramenta.

## Estrutura da ferramenta

A estrutura de arquivos da ferramenta foi escolhida com o objetivo de empacotar a ferramenta e criar uma CLI a partir dela, além de possibilitar a criação de uma página de documentação a partir do *Mkdocs*. Dessa forma, a organização de pastas se tornou a seguinte:

- `LICENSE`: Arquivo de licença da ferramenta.
- `README.md`: Arquivo de introdução da ferramenta.
- `pyproject.toml`: Arquivo de configuração que define o conteúdo, metadados e dependências do pacote da ferramenta. Optou-se por utilizar o `pyproject.toml` em vez do `setup.py`, seguindo os novos padrões definidos na [PEP 621](https://packaging.python.org/en/latest/specifications/declaring-project-metadata/#declaring-project-metadata).
- `MANIFEST.in`: Arquivo de configuração que especifica quais arquivos e diretórios devem ser incluídos durante o empacotamento da ferramenta.
- `ds_contest_tools/`: Diretório que contém o código fonte e os arquivos da ferramenta.
- `run.py`: Arquivo de inicialização da CLI sem a necessidade de instalar o pacote.
- `legacy_converter.py`: Arquivo responsável pela conversão de problemas legados para o novo formato de problemas da ferramenta.
- `docs/`: Diretório contendo os arquivos da documentação da ferramenta.
- `mkdocs.yml`: Arquivo de configuração da página do projeto.

## Estrutura dos problemas

A estrutura de arquivos dos problemas foi projetada visando facilitar configuração dos problemas e o uso da ferramenta. Ao inicializar um problema, os seguintes arquivos e pastas são criados:

- `problem.json`: Arquivo que contém informações do problema, como nome, descrição, limites de tempo e memória, entre outros.
- `src/`: Pasta que contém as soluções, geradores, validadores, interatores (se aplicável) e verificadores do problema.
  - As soluções devem ser definidas no arquivo `problem.json` para que a ferramenta possa reconhecê-las. Isso permite dividir as soluções em categorias específicas.
  - Os validadores, interatores e checkers devem seguir nomes padrão para que a ferramenta possa identificá-los corretamente, dispensando a necessidade de especificá-los no arquivo `problem.json`.
  - A linha de comando para executar o(s) gerador(es) deve ser incluída no arquivo `script.sh`, que será executado pela ferramenta. A ferramenta aceita multigeradores e geradores únicos.
- `statement/`: Pasta que deve conter o enunciado do problema. Está dividida em vários arquivos para facilitar a edição do enunciado.
  - Arquivos de imagem que forem utilizados no enunciado devem ser colocados na pasta raiz do problema.
- `Makefile`: Arquivo contendo comandos para compilar e executar os binários do problema. Não é necessário rodar o Makefile para utilizar a ferramenta.
- `maratona.cls`: Arquivo que contém a classe LaTeX para gerar o PDF do problema.

## Estrutura dos módulos

A estrutura dos módulos foi projetada visando facilitar a criação de novos módulos. Nessa estrutura, os arquivos presentes no diretório da pasta `ds_contest_tools` são responsáveis pelo processamento dos comandos. Já os arquivos localizados na pasta `parsers`, submódulo de `ds_contest_tools`, configuram os comandos da ferramenta.

Essa organização permite adicionar novos comandos e módulos  na ferramenta sem a necessidade de alterar os arquivos existentes. Caso seja necessário realizar alguma modificação, é possível fazê-lo de forma isolada, sem afetar outros arquivos.

Além disso, as pastas `Maratona` e `files`, dentro de `ds_contest_tools`, contêm arquivos auxiliares da ferramenta, como a classe LaTeX para a geração do PDF do problema e a estrutura de pastas dos problemas a ser copiada quando um problema é iniciado.

## Estrutura dos parsers

Os arquivos de parser são organizados em duas funções principais: `add_parser` e `process_command`. A função `add_parser` define os argumentos a serem utilizados pelo parser para um determinado comando, enquanto a função `process_command` processa os argumentos e chama as funções correspondentes do módulo `ds_contest_tools`.

Além disso, existe um arquivo chamado `common.py` que contém funções comuns a todos os parsers. Essas funções incluem a função responsável por instanciar os caminhos necessários e a função que verifica se as dependências estão devidamente instaladas.

## Módulos de processamento

### `boca.py`

Este módulo contém as funções responsáveis pela conversão do problema para o formato BOCA, incluindo a criação e compactação do pacote BOCA. É possível modificar o arquivo `problem.json` para configurar o pacote BOCA.

### `checker.py`

<!-- TODO - Adicionar mais informações sobre o checker. -->
Este módulo é responsável pela execução das soluções e pela verificação das respostas esperadas para as soluções elaboradas.

### `config.py`

Este módulo contém as funções e constantes necessárias para a configuração de certos parâmetros da ferramenta, como a definição das informações gerais do PDF.

### `contest.py`

Este módulo engloba as funções responsáveis pela geração de maratonas a partir de um conjunto de problemas. Ele permite a criação de PDFs da maratona, pacotes BOCA e arquivos de entrada e saída do conjunto de problemas.

### `ds_contest_tools.py`

Este módulo reúne os parsers responsáveis pela criação dos comandos da ferramenta e pela execução das funções correspondentes a cada comando, criando a CLI da ferramenta.

### `fileutils.py`

Este módulo contém funções relacionadas à manipulação de arquivos utilizados pela ferramenta, como cópia de diretórios e nomeação de arquivos.

### `htmlutils.py`

Este módulo é responsável por gerar um relatório visual a partir das informações geradas pelo módulo *checker.py*. 

### `jsonutils.py`

Este módulo contém funções para a leitura e escrita de arquivos JSON.

### `latexutils.py`

Este módulo engloba funções responsáveis pela criação dos arquivos LaTeX necessários para a geração de PDFs, como arquivos de tutorial e de enunciado.

### `logger.py`

Este módulo contém as funções relacionadas ao registro de logs da ferramenta, como a criação dos arquivos e escrita dos logs. 

### `metadata.py`

Este módulo contém classes que facilitam o uso de metadados da ferramenta, permitindo uma melhor recuperação de informações a serem utilizadas em vários módulos. Essas classes proporcionam uma forma organizada e eficiente de lidar com os metadados, simplificando o acesso e manipulação das informações relevantes em diferentes partes do código.

### `pdfutils.py`

Este módulo engloba funções relacionadas à manipulação de arquivos PDF a partir dos arquivos LaTeX gerados pelo módulo `latexutils.py`.

### `polygon_connection.py`

Este módulo é responsável por estabelecer a conexão entre a ferramenta e o Polygon. Contém funções relacionadas à comunicação com o Polygon, incluindo a obtenção de informações necessárias, o download de pacotes e a autenticação dos parâmetros das requisições.

### `polygon_converter.py`

Este módulo contém as funções responsáveis por converter um problema do Polygon para o formato da ferramenta. Dessa forma, ele é responsável por buscar os pacotes corretos de um problema e converter os arquivos em um problema da ferramenta.

### `polygon_submitter.py`

Este módulo contém as funções responsáveis por enviar um problema da ferramenta para o Polygon. Dessa forma, ele gera a lista de requisições a serem enviadas para o Polygon e todas as funcionalidades relacionadas a essa envio.

### `sqtpm.py`

Este módulo contém as funções de conversão de problemas para o formato SQTPM, incluindo a criação do pacote SQTPM.

### `toolchain.py`

Este módulo contém as funções responsáveis por inicializar e construir um problema, incluindo a compilação dos binários e a geração e validação dos arquivos de entrada e saída.

### `utils.py`

Este módulo contém funções auxiliares para a criação de problemas, como a verificação de arquivos e a conversão de objetos.