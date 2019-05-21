# DS Contest Tools

Ferramentas para preparação de *contests*, por Daniel Saad.


## Introdução

Estas ferramentas para preparação de *contests* são inspiradas na suíte de ferramentas `ejtools`, elaborada pelo Prof. Edson Alves (UnB/FGA), mas elas seguem uma abordagem diferente, uma vez que são baseadas na biblioteca `testlib`, utilizada na preparação de problemas do `Codeforces` e desenvolvida por Mike Mirzayanov.

Atualmente, esta coleção de ferramentas suportam a exportação de problemas para os seguintes sistemas:
* BOCA


## Pré-requisitos

Para rodar as ferramentas é necessário ter instalado de antemão:
* `python3`: as principais ferramentas estão escritas nesta linguagem;
* `pdflatex`: para geração de PDFs a partir de arquivos .tex;
* `pdfjam`: para fazer a união de arquivos PDFs,  geralmente disponível junto com o ambiente LaTeX;
* `cmake`, para gerar makefiles;
* `make`, para compilação dos fontes e instalação dos executáveis a partir dos makefiles gerados;
* `g++` >= 4.8: para compilação dos fontes.
* `zip`: para empacotamento no formato BOCA.


## Estrutura do projeto

A estrutura de pastas do projeto é a seguinte:

* `build.py`: script que inicializa, constrói e importa problemas para diferentes tipos de sistemas de juiz.
* `checker.py`: script para
* `/arquivos`: contém os modelos a serem utilizados na preparação dos problemas.
* `/submissoes`: contém as submissões para correção manual.
* `/Problemas`: contém os problemas elaborados para o *contest*.
* `/boca`: contém os arquivos .zip dos problemas no formato BOCA, após a exportação.

## Inicialização de um Problema

Para inicializar um problema novo, utilize:
```sh
python3 build.py init <ID>
```

Em que `<ID>` é o ID do problema a ser inicializado.

## Preparação de problemas

A preparação de um problema segue cinco etapas, que não precisam ser feitas em ordem. Elas consistem de:
* Configuração do arquivo `problem.json`;
* Elaboração do enunciado;
* Elaboração da solução esperada;
* Elaboração dos casos de teste;
* Elaboração do validador dos casos de teste;
* Elaboração do corretor.


### Configuração do arquivo JSON

O arquivo `problem.json` criado na inicialização dos problemas contém todos os metadados importantes para geração do problema e PDF.
Os campos são bem intuitivos e basta preenchê-los na mão.

### Elaboração do enunciado

A elaboração do enunciado pode ser feita diretamente através do arquivo `statement.md`, localizado na pasta do problema recém inicializado.
Ele tem suporte a linguagem `LaTeX`.

### Elaboração da solução esperada

O arquivo gabarito, responsável por gerar as saídas esperadas pelo juíz, deve ser codificado no arquivo `src/ac.cpp`.

### Elaboração dos casos de teste

É possível gerar os casos de teste utilizando a `testlib`. Para isso só é preciso codificar a geração de testes no arquivo `src/generator.cpp`.

A `teslib` facilita a geração de casos de testes e sua documentação pode ser facilmente encontrada neste [link](https://github.com/MikeMirzayanov/testlib). Além da documentação básica, há uma série de exemplos explicando as facilidades da `testlib` para geração dos casos de teste.

### Elaboração do validador dos casos de teste

É possível validar os casos de teste utilizando a `testlib`. Para isso só é preciso codificar a geração de testes no arquivo `src/validator.cpp`.
Assim, temos certeza que não há nenhuma entrada que exceda os limites do problema ou que violem alguma propriedade do mesmo.

A `teslib` facilita a validação dos casos de testes e sua documentação pode ser facilmente encontrada neste (link).[https://github.com/MikeMirzayanov/testlib]. Além da documentação básica, há uma série de exemplos explicando as facilidades da `testlib` para validação dos casos de teste.

### Elaboração do corretor

É possível gerar corretores especiais de problemas utilizando a `testlib`. Para isso só é preciso codificar a geração de testes no arquivo `src/checker.cpp`.

A `teslib` facilita o processo de elaboração de corretores especiais e sua documentação pode ser facilmente encontrada neste [link](https://github.com/MikeMirzayanov/testlib). Além da documentação básica, há uma série de exemplos explicando as facilidades da `testlib` para elaboração dos corretores. Inclusive, para corretores mais simples, uma série de modelos já estão disponíveis no repositório da `testlib`.

## Construção de um problema
Para construir o PDF associado ao problema bem como criar as entradas e saídas dele execute:
```sh
python3 build.py build <ID>
```
Em que `<ID>` é o ID do problema a ser construído.

A construção envolve:

* Compilação de fontes.
* Geração dos  arquivos de entrada e saída.
* Geração do PDF a partir do arquivo Markdown

Para construir todos os problemas basta utilizar:

```sh
python3 build.py buildall
```

Além de construir todos, ele irá criar o arquivo Maratona/Maratona.pdf, contendo a união de todos os problemas.

## Conversão para o formato do BOCA

Para converter um problema para o formato do BOCA, basta executar:
```sh
python3 build.py pack2boca <ID>
```
Onde `<ID>` é o ID do problema (A,B,C,...) a ser convertido

O arquivo BOCA zipado será criado na pasta `boca` que fica na raiz do projeto.

Para converter todos os problemas para o formato BOCA:

```sh
python3 build.py packall2boca
```

## Correção manual de uma submissão

É possível utilizar o script `checker.py` para verificar se uma solução está correta.
Para isto, coloque o código a ser checado na pasta `submissoes` e utilize:

```sh
python3 checker.py <fonte> <ID>
```

Em que `<fonte>` corresponde ao nome do arquivo fonte (com extensão) e `<ID>` corresponde ao ID do problema a ser checado.

Internamente este script compila os fontes (se necessário), gera os arquivos resposta e finalmente utiliza o `checker`
de cada problema para verificar se a solução está correta. 

