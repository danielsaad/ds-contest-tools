# DS Contest Tools

Ferramentas para preparação de *contests*, por Daniel Saad.

Para mais informações sobre os comandos ou sobre a ferramenta, leia a [documentação](https://danielsaad.com/ds-contest-tools).

## Introdução

Estas ferramentas para preparação de *contests* são inspiradas na suíte de ferramentas `ejtools`, elaborada pelo Prof. Edson Alves (UnB/FGA), mas elas seguem uma abordagem diferente, uma vez que são baseadas na biblioteca `testlib`, utilizada na preparação de problemas do `Codeforces` e desenvolvida por Mike Mirzayanov.

Atualmente, esta coleção de ferramentas suportam a exportação de problemas para os seguintes sistemas:

* BOCA
* Polygon
* SQTPM


## Pré-requisitos

Para rodar as ferramentas é necessário ter instalado de antemão:
* `python` >= 3.8: as principais ferramentas estão escritas nesta linguagem;
* `pdflatex`: para geração de PDFs a partir de arquivos .tex;
* `pdfjam`: para fazer a união de arquivos PDFs,  geralmente disponível junto com o ambiente LaTeX;
* `make`, para compilação dos fontes e instalação dos executáveis a partir dos makefiles gerados;
* `g++` >= 4.8: para compilação dos fontes.
* `zip`: para empacotamento no formato BOCA.


## Funcionalidades suportadas

* Criar problemas competitivos localmente.
* Criar maratonas a partir dos problemas criados.
* Exportar problemas para o BOCA, Polygon ou SQTPM.
* Baixar e converter problemas do Polygon para o formato da ferramenta.

## Instalação

Para instalar a ferramenta, basta executar o comando abaixo:

```bash
pip install ds-contest-tools
```

Para outros modos de instalação, consulte a [documentação](https://danielsaad.com/ds-contest-tools).

## Utilização

Para rodar a ferramenta, utilize o comando `ds-contest-tools`.

A ferramenta é utilizada da seguinte forma:

```bash
ds-contest-tools init problem_dir
ds-contest-tools build problem_dir
```

Onde `problem_dir` é o diretório onde o problema será inicializado e compilado. Use o comando `ds-contest-tools --help` para obter mais informações sobre os comandos disponíveis.

Para o primeiro uso ao converter problemas do Polygon, será necessário definir as chaves da API do Polygon. Tais chaves são armazenadas localmente no diretório raiz da ferramenta em um arquivo JSON.
