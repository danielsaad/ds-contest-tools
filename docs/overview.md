Estas ferramentas para preparação de *contests* são inspiradas na suíte de ferramentas `ejtools`, elaborada pelo Prof. Edson Alves (UnB/FGA), mas elas seguem uma abordagem diferente, uma vez que são baseadas na biblioteca `testlib`, utilizada na preparação de problemas do `Codeforces` e desenvolvida por Mike Mirzayanov.

Atualmente, esta coleção de ferramentas suporta a exportação de problemas para os seguintes sistemas:
* BOCA
* Polygon
* SQTPM

## Preparação dos problemas

A preparação de um problema segue cinco etapas, que não precisam ser realizadas necessariamente na ordem descrita. Elas consistem em:
* Configuração do arquivo `problem.json`;
* Elaboração do enunciado do problema;
* Elaboração da solução esperada para o problema;
* Elaboração dos casos de teste;
* Elaboração do validador dos casos de teste;
* Elaboração do corretor.

### Configuração do arquivo JSON

O arquivo `problem.json` criado na inicialização dos problemas contém todos os metadados importantes para a geração do problema e do PDF. Os campos são bem intuitivos e basta preenchê-los manualmente.

### Elaboração do enunciado

A elaboração do enunciado pode ser feita diretamente através dos arquivos LaTex localizados na pasta *statement* do problema. 

### Elaboração das soluções esperadas

Todo problema deve possuir uma solução principal, que deve ser codificada e colocada na pasta *src*, em conjunto com outras possíveis soluções. Após isso, os campos referentes aos tipos de soluções devem ser preenchidos no arquivo `problem.json`.

### Elaboração dos casos de teste

Para gerar os casos de teste, é necessário codificar um arquivo gerador e adicionar os argumentos necessários para a geração no arquivo `src/script.sh`, como visto a seguir:

```bash
multigenerator
generator 100 123
generator 100 987
```

Nesse exemplo, `multigenerator` é o nome de um gerador de múltiplos casos de teste e `generator` é o nome de um gerador único. É possível utilizar quantos comandos *generator* forem necessários, cada um com seus próprios argumentos.

Além disso, é possível utilizar a `testlib` para codificar o gerador.

### Elaboração do validador dos casos de teste

Para termos certeza de que não há nenhuma entrada que exceda os limites do problema ou que violem alguma propriedade do mesmo, é necessário codificar o arquivo `src/validator.cpp`. É possível utilizar a `testlib` para codificar o validador.

### Elaboração do corretor

Para elaborar o corretor, é necessário codificar o arquivo `src/checker.cpp`. É possível criar corretores especiais de problemas utilizando a `testlib`.

### Biblioteca Testlib

A `testlib` facilita o processo de elaboração de corretores especiais e a geração e validação de casos de testes. Sua documentação pode ser facilmente encontrada em seu [repositório](https://github.com/MikeMirzayanov/testlib). 

Além da documentação básica, há uma série de exemplos explicando as facilidades da `testlib` para geração de casos de teste, validação de problemas e elaboração dos corretores. Para esses arquivos, existem modelos simples que já estão disponíveis no repósitorio.