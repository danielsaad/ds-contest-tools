# Diretrizes para Pull Requests (PRs)

Este documento estabelece as diretrizes para a abertura e aprovação de Pull Requests no projeto `ds-contest-tools`. Ele serve para orientar contribuidores sobre como estruturar suas contribuições, especialmente aquelas que **não envolvem a publicação de uma nova versão**.

Para o fluxo específico de lançamento de versões, consulte o [Processo de Lançamento](release-process.md).

---

## 1. Padrão de Nomenclatura (Conventional Commits)

Recomendamos fortemente o uso de **Conventional Commits** para os títulos dos seus Pull Requests. Isso ajuda a nossa esteira de CI/CD a entender automaticamente o propósito da sua alteração e padroniza o histórico do projeto.

### Prefixos Comuns:

| Prefixo | Descrição | Exemplo de Título |
| :--- | :--- | :--- |
| **`feat:`** | Nova funcionalidade para o usuário | `feat: adicionar suporte ao formato atcoder` |
| **`fix:`** | Correção de bug no código | `fix: corrigir timeout na geração de PDFs` |
| **`docs:`** | Alterações exclusivas em documentação | `docs: atualizar guia de instalação no README` |
| **`chore:`** | Tarefas de manutenção, dependências ou CI/CD | `chore: atualizar versão das actions do GitHub` |
| **`refactor:`** | Mudança interna sem alterar comportamento | `refactor: extrair formatador LaTeX para módulo puro` |
| **`test:`** | Adição ou correção de testes automatizados | `test: adicionar casos de teste para checker` |

### PRs de Release

Se o seu PR tem o objetivo de gerar uma nova versão no PyPI, o título deve ser no formato `Release vX.Y.Z` (ou equivalente aceito pela esteira). A automação reconhecerá isso e exigirá a atualização correspondente no `CHANGELOG.md`.

---

## 2. Pull Requests que NÃO alteram versão

A grande maioria dos Pull Requests no dia a dia (como documentação, correções ou ajustes em CI/CD) não altera a versão da aplicação.

Ao abrir PRs desse tipo, não é necessário atualizar o `CHANGELOG.md`, e a esteira de CI/CD seguirá regras específicas para otimizar a execução.

### 2.1. Alterações apenas na Documentação e na Configuração

Se o seu PR alterar **apenas** arquivos dos seguintes caminhos:

* Pasta `docs/`
* Arquivo `README.md`
* Arquivos ignorados (`.gitignore`)
* Configurações administrativas (`.github/CODEOWNERS`)

> [!TIP]
> **Execução Otimizada:** A esteira de CI/CD está configurada com a regra `paths-ignore`. Mudanças que afetam exclusivamente documentação ou arquivos administrativos não disparam testes nem builds desnecessários, permitindo um merge muito mais ágil.

### 2.2. Alterações de CI/CD ou Código sem Release

Se você estiver alterando a esteira de CI/CD (arquivos `.github/workflows/`) ou fazendo `refactor` no código base, a esteira de CI **será executada** para garantir que você não quebrou o build do pacote.

No entanto, como o título do seu PR não será um título de Release (ex: você usará `chore: ajustar workflow`), o sistema:

1. Fará os testes de build com sucesso.
2. Reconhecerá que não é uma Release ("*Não é um PR de release. Validação de versão ignorada.*").
3. **Não exigirá** atualizações no arquivo `CHANGELOG.md`.
4. Ficará verde e permitirá o merge sem bloqueios.

---

## 3. Revisão e Aprovação (Code Owners)

Independente do tipo de Pull Request (mesmo para pequenas alterações no `README.md`), **nenhum código vai para a `master` sem revisão**.

1. Ao abrir o PR, o GitHub solicitará automaticamente a revisão dos responsáveis mapeados no arquivo `CODEOWNERS`.
2. O merge estará **bloqueado** até que pelo menos um `Code Owner` aprove a alteração.
3. Certifique-se de que a sua branch está sempre atualizada com a `master` para evitar conflitos na hora do merge.
