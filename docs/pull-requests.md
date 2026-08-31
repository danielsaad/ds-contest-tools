# Diretrizes para Pull Requests (PRs)

Este documento estabelece as diretrizes para a abertura e aprovação de Pull Requests no projeto `ds-contest-tools`. Ele serve para orientar contribuidores sobre como estruturar suas contribuições, especialmente aquelas que **não envolvem a publicação de uma nova versão**.

Para o fluxo específico de lançamento de versões, consulte o [Processo de Lançamento](release-process.md).

---

## 1. Padrão de Nomenclatura (Conventional Commits)

Recomendamos fortemente o uso de **Conventional Commits** para os títulos dos seus Pull Requests. Isso ajuda a nossa esteira de CI/CD a entender automaticamente o propósito da sua alteração.

### Prefixos Comuns:

* **`docs:`** Alterações exclusivas em documentação (ex: manuais, README.md, docstrings).
  > *Exemplo: `docs: atualizar guia de instalação no README`*
* **`chore:`** Atualizações de tarefas de manutenção, ferramentas, dependências ou esteiras de CI/CD (GitHub Actions).
  > *Exemplo: `chore: atualizar versão da action de lint`*
* **`feat:`** Uma nova funcionalidade para o usuário.
* **`fix:`** Uma correção de bug para o usuário.
* **`refactor:`** Uma mudança de código que não corrige um bug nem adiciona uma funcionalidade.
* **`test:`** Adição ou correção de testes automatizados.

### PRs de Release

Se o seu PR tem o objetivo de gerar uma nova versão no PyPI, o título deve ser estritamente no formato `Release vX.Y.Z` (ou equivalente). A automação reconhecerá isso e exigirá a atualização do `CHANGELOG.md`.

---

## 2. Pull Requests que NÃO alteram versão

A grande maioria dos Pull Requests no dia a dia (como documentação, correções ou ajustes em CI/CD) não altera a versão da aplicação. 

Ao abrir PRs desse tipo, o comportamento da nossa esteira é altamente otimizado:

### 2.1. Alterações exclusivas de Documentação e Configuração

Se o seu PR alterar **apenas** arquivos dos seguintes caminhos:

* Pasta `docs/`
* Arquivo `README.md`
* Arquivos ignorados (`.gitignore`)
* Configurações administrativas (`.github/CODEOWNERS`)

**A esteira de CI/CD não será executada**.
A esteira de CI/CD está configurada com a regra `paths-ignore` no nosso workflow de CI. Isso significa que mudanças em textos e configurações que não afetam o código Python não desperdiçam recursos executando testes e builds desnecessários. O merge será muito mais rápido!

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
