# Guia de uso 

Estas ferramentas para preparação de *contests* são inspiradas na suíte de ferramentas `ejtools`, elaborada pelo Prof. Edson Alves (UnB/FGA), mas elas seguem uma abordagem diferente, uma vez que são baseadas na biblioteca `testlib`, utilizada na preparação de problemas do `Codeforces` e desenvolvida por Mike Mirzayanov.

Atualmente, esta coleção de ferramentas suporta a exportação de problemas para os seguintes sistemas:

- BOCA
- Polygon
- SQTPM

## Pré-requisitos

Para rodar as ferramentas é necessário ter instalado de antemão:
* `python` >= 3.8: as principais ferramentas estão escritas nesta linguagem;
* `pdflatex`: para geração de PDFs a partir de arquivos .tex;
* `pdfjam`: para fazer a união de arquivos PDFs,  geralmente disponível junto com o ambiente LaTeX;
* `make`, para compilação dos fontes e instalação dos executáveis a partir dos makefiles gerados;
* `g++` >= 4.8: para compilação dos fontes.
* `zip`: para empacotamento no formato BOCA.

## Problemas

A ferramenta oferece suporte para a criação e validação de três categorias distintas de problemas, os quais são problemas comuns, problemas com grader e problemas interativos. Para definir o tipo do problema, basta alterar os campos `grader` e `interactive` no `problem.json`, ou inicializar o problema com o tipo desejado.

### Problemas Comuns

Esta categoria abrange problemas tradicionais que não exigem interações complexas ou avaliações personalizadas. Os participantes são solicitados a fornecer soluções que resolvam desafios específicos. 

### Problemas com Grader

Esta categoria engloba problemas que demandam uma avaliação mais personalizada das soluções dos participantes, onde os competidores precisam criar funções específicas ao invés do código completo. Ao criar um problema com grader, a ferramenta gera automaticamente os arquivos `grader.cpp` e `grader.h` na pasta *src* do problema. Para problemas em Python, é necessário criar o arquivo `main.py`, que deve importar o arquivo `solution` como módulo, mesmo que as soluções não possuam esse nome.

### Problemas Interativos

Nesta categoria, os problemas envolvem interações dinâmicas entre os participantes e o sistema. Ao criar problemas interativos, a plataforma gera automaticamente os arquivos `interactor.cpp` e `interactor.tex`. Problemas interativos são aqueles em que o sistema e o usuário trocam informações repetidamente, criando um ambiente de desafio mais dinâmico e imersivo.

Essa abordagem é empregada quando os problemas requerem um nível mais profundo de interação, como simulações, jogos ou situações em que as respostas dos participantes afetam diretamente o desenrolar do problema.

A ferramenta aceita apenas problemas interativos em C++.

## Preparação dos problemas

A preparação de um problema segue cinco etapas, que não precisam ser realizadas necessariamente na ordem descrita. Elas consistem em:

- Configuração do arquivo `problem.json`.
- Elaboração do enunciado do problema.
- Elaboração da solução esperada para o problema.
- Elaboração dos casos de teste.
- Elaboração do validador dos casos de teste.
- Elaboração do corretor.

Não é necessário realizar todas as etapas para que o problema seja gerado, como a elaboração do validador ou do corretor. Para isso, utilize as flags necessárias na hora de construir o problema.

### Configuração do arquivo JSON

O arquivo `problem.json` criado na inicialização dos problemas contém todos os metadados importantes para a geração do problema e do PDF. Os campos são bem intuitivos e basta preenchê-los manualmente.

### Elaboração do enunciado

A elaboração do enunciado pode ser feita diretamente através dos arquivos LaTex localizados na pasta *statement* do problema. 

### Elaboração das soluções esperadas

Todo problema deve possuir uma solução principal, que deve ser codificada e colocada na pasta *src*, em conjunto com outras possíveis soluções. Após isso, os campos referentes aos tipos de soluções devem ser preenchidos no arquivo `problem.json`.

### Elaboração dos casos de teste

Para gerar os casos de teste, é necessário codificar um arquivo gerador e adicionar os argumentos necessários para a geração dos casos de teste no arquivo `src/script.sh`, como visto a seguir:

```bash
multigenerator
generator 100 123
generator 100 987
```

Nesse exemplo, `multigenerator` é o nome de um gerador de múltiplos casos de teste e `generator` é o nome de um gerador único. É possível utilizar quantos comandos *generator* forem necessários, cada um com seus próprios argumentos Além disso, é possível utilizar a `testlib` para codificar o gerador.

### Elaboração do validador dos casos de teste

Para termos certeza de que não há nenhuma entrada que exceda os limites do problema ou que violem alguma propriedade do mesmo, é viável codificar o arquivo `src/validator.cpp`. É possível utilizar a `testlib` para codificar o validador. Se o problema não possuir um validador, será necessário utilizar a flag `-nv` na hora de construir o problema.

### Elaboração do corretor

Para elaborar o corretor, é necessário codificar o arquivo `src/checker.cpp`. É possível criar corretores especiais de problemas utilizando a `testlib`. Se o problema não possuir um corretor, será necessário utilizar a flag `-nc` na hora de construir o problema.

### Biblioteca Testlib

A `testlib` facilita o processo de elaboração de corretores especiais e a geração e validação de casos de testes. Sua documentação pode ser facilmente encontrada em seu [repositório](https://github.com/MikeMirzayanov/testlib). 

Além da documentação básica, há uma série de exemplos explicando as facilidades da `testlib` para geração de casos de teste, validação de problemas e elaboração dos corretores. Para esses arquivos, existem modelos simples que já estão disponíveis no repósitorio.