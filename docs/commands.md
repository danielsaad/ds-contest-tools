# Comandos

Bem-vindo à página de comandos da ferramenta! Aqui você encontrará informações detalhadas sobre as funcionalidades e recursos dos comandos disponíveis para criar e converter problemas. 

## init

O comando `init` é utilizado para inicializar um problema com os arquivos e diretórios necessários para começar a construção do problema.

Uso: `ds-contest-tools init <problem_dir>`

Opções de inicialização:

- **-i**, **--interactive**: Inicializa um problema interativo. Nesses problemas, os casos de teste utilizados na descrição do problema são definidos por arquivos de entrada/saída com a extensão `.interactive`, caso sejam necessários.
- **-g**, **--grader**: Inicializa um problema com grader.

## build

O comando `build` é utilizado para construir os problemas, ou seja, gerar e validar os casos de teste e verificar as soluções com o *checker*. Por padrão, constrói um problema utilizando apenas a solução principal.

Uso: `ds-contest-tools build <problem_dir>`

Opções de construção:

- **-a, --all**: Constrói o problema utilizando todas as soluções.
- **-s, --specific `<solucao>`**: Constrói o problema utilizando apenas uma solução específica, indicada pelo *solucao*.
- **-p, --pdf**: Gera apenas os PDFs do problema.
- **-i, --io**: Gera apenas os arquivos de entrada/saída do problema.
- **-nv, --no-validator**: Constrói o problema sem validar os casos de teste.
- **-ng, --no-generator**: Ao compilar um problema, os casos de teste são redefinidos no diretório input. Ao usar essa opção, os casos de teste são mantidos, pois o gerador não é chamado. É importante usá-la caso os testes sejam criados manualmente, caso contrário, eles serão apagados.
- **-no, --no-output**: Constrói o problema sem gerar as saídas dos casos de teste.
- **-nc, --no-checker**: Constrói o problema sem utilizar o checker nas soluções.
- **-ngvoc**: Gera apenas os executáveis e os PDFs do problema. É a união entre as opções *-ng*, *-no* e *-nc*.
- **-c, --cpu-count `<qtde-threads>`**: Define a quantidade de *threads* a serem criadas na execução do checker, indicado por *qtde-threads*.

## contest

O comando `contest` é utilizado para gerar um diretório com *n* problemas a serem utilizados em uma maratona. 

Uso: `ds-contest-tools contest <problem_dir [problem_dir...]> <contest_dir>`

Opções:

- **-p, --pdf**: Gera apenas os PDFs da maratona.
- **-i, --io**: Gera apenas os arquivos de entrada/saída dos problemas da maratona.
- **--author**: Adiciona o nome do autor no cabeçalho dos PDFs da maratona.

## convert_to

Converte o problema para um dos seguintes formatos:

- **BOCA**: Converte o problema para o formato BOCA em um arquivo *zippado*.
- **SQTPM**: Converte o problema para o formato SQTPM em um novo diretório.
- **Polygon**: Envia o problema para o Polygon. Várias requisições são feitas para converter o problema. Durante a conversão para o Polygon, as seguintes alterações são feitas no problema online:
    - As informações gerais e textos do enunciado são alterados.
    - Os arquivos de origem, recursos, auxiliares e solução com o mesmo nome dos arquivos a serem enviados serão sobrescritos.
    - Caso haja casos de teste com índices idênticos, esses serão substituídos pelo novo conjunto de casos de teste.
    - Se houver uma requisição de *script* do gerador, o antigo será substituído pelo novo.

Uso: `ds-contest-tools convert_to <format> <problem_dir>`

Opções:

- **-o, --output-dir `<diretorio>`**: Define um diretório de saída para o problema convertido. No caso da conversão para o Polygon, define o ID do problema no arquivo `problem.json` para uso futuro.
- **-m, --manual-tests**: Converte os casos de teste para o Polygon sem utilizar o script gerador.

## convert_from

Converte para o formato da ferramenta o problema com um dos seguintes formatos:

- **Polygon**: Baixa o pacote mais recente e pronto do Linux na pasta do problema e o utiliza para a conversão. Requisições adicionais à API do Polygon são feitas para encontrar o nome dos arquivos fonte e o tipo do problema.

Uso: `ds-contest-tools convert_from <format> <problem_dir> <package_dir>`

Opções:

- **-l, --local `<diretorio>`**: Converte um pacote local do Polygon para o formato da ferramenta. É possível converter pacotes *FULL* e *STANDARD*. Nenhuma requisição é feita, então o usuário precisa especificar se o problema é interativo ou não e alterar o nome dos arquivos de origem para o padrão da ferramenta.

## set_keys

o comando `set_keys` é responsável por definir as chaves da API do Polygon que serão utilizadas para a conversão dos problemas. Essas chaves são necessárias para acessar e interagir com o Polygon, e são armazenadas localmente no repositório da ferramenta.

Uso: `ds-contest-tools set_keys`

## clean

Remove executáveis ​​criados após a construção do problema.

Uso: `ds-contest-tools clean <problem_dir>`
