# DS Contest Tools

Ferramentas para preparação de Contest, por Daniel Saad.


## Introdução

Estas ferramentas para preparação de *contests* são inspiradas na suíte de ferramentas `ejtools`, elaborada pelo Prof. Edson Alves (UnB/FGA), mas elas seguem uma abordagem diferente, uma vez que são baseadas na biblioteca `testlib`, utilizada na preparação de problemas do `Codeforces`, desenvolvida por Mike Mirzayanov.

Atualmente, esta coleção de ferramentas suportam a exportação de problemas para os seguintes sistemas:
* BOCA


## Pré-requisitos

Para rodar as ferramentas é necessário ter instalado de antemão:
* `python3`: as principais ferramentas estão escritas nesta linguagem;
* `pdflatex`: para geração de PDFs a partir de arquivos .tex;
* `pdfjam`: para fazer a união de arquivos PDFs,  geralmente disponível junto com o ambiente LaTeX;
* `cmake`, para gerar makefiles;
* `make`, para compilação dos fontes e instalação dos executáveis;
* `g++` >= 4.8: para compilação dos fontes.


## Estrutura do projeto

A estrutura de pastas do projeto é a seguinte:

* `build.py`: script que inicializa, constrói e importa problemas para diferentes tipos de sistemas de juiz.
* `checker.py`: script para
* `/arquivos`: contém os modelos a serem utilizados na preparação dos problemas.
* `/submissoes`: contém as submissões para correção manual.
* `/Problemas`: contém os problemas elaborados para o contest.
* `/boca`: contém os arquivos .zip dos problemas no formato BOCA, após a exportação.

## Inicialização de um Problema

Para inicializar um problema novo, utilize:
```sh
python3 build.py init <ID>
```

Onde `<ID>` é o ID do problema (A,B,C,...) a ser inicializado.

## Preparação de problemas

A preparação de um problema segue cinco etapas, que não precisam ser feitas em ordem. Elas consistem de:
* Elaboração do enunciado;
* Elaboração da solução esperada;
* Elaboração dos casos de teste;
* Elaboração do validador dos casos de teste;
* Elaboração do corretor.

### Elaboração do enunciado

A elaboração do enunciado pode ser feita diretamente através 

### Elaboração da solução esperada

### Elaboração dos casos de teste

### Elaboração do validador dos casos de teste

### Elaboração do corretor

## Construção de um problema
Para construir o pdf associado ao problema bem como criar as entradas e saídas do mesmo execute:
```sh
python3 build.py build <ID>
```
Onde `<ID>` é o ID do problema (A,B,C,...) a ser construído.

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

O arquivo BOCA zipado será criado na pasta boca que fica na raiz do projeto.

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

