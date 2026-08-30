# Processo de Lançamento (Release Process)

Este documento descreve como funciona o fluxo de publicação de novas versões do pacote `ds-contest-tools`.

O processo de lançamento de uma nova versão da aplicação é automatizado usando o `setuptools_scm` para o versionamento dinâmico baseado em Tags do Git, aliado ao GitHub Actions para a Integração e Entrega Contínuas (CI/CD).

**A validação de novas versões ocorre conferindo o título do Pull Request e o arquivo `CHANGELOG.md`.** Você não precisa (e não deve) alterar a versão manualmente em arquivos `.py` ou no `pyproject.toml`.

---

## 🚀 Como lançar uma nova versão

Para publicar uma nova versão oficial (ex: `1.2.0`), siga estes passos:

### Passo 1: Atualizar o CHANGELOG.md

Crie uma nova branch a partir da `master` (ex: `release/v1.2.0`).
Abra o arquivo `CHANGELOG.md` e copie o template disponível nos comentários HTML do próprio arquivo.
Cole logo após o bloco de comentário e preencha com as alterações da versão.

**Exemplo:**
```markdown
## [1.2.0] - 2026-08-29

### Adicionado
- Nova funcionalidade incrível.

### Corrigido
- Correção do bug na geração de PDFs.
```

### Passo 2: Abrir um Pull Request

Faça o commit dessa alteração (ex: `git commit -m "chore: release v1.2.0"`) e abra um Pull Request para a branch `master`.

> **IMPORTANTE:** O **Título** do Pull Request deve ser obrigatoriamente no formato: `Release vX.Y.Z` (ex: `Release v1.2.0`).

### Passo 3: Validação Automática (CI)

Neste momento, a nossa esteira (GitHub Actions) entrará em ação:

1. A esteira extrairá a versão (`1.2.0`) do título do seu PR.
2. A esteira fará uma verificação cruzada para garantir que o cabeçalho `## [1.2.0]` existe de fato dentro do `CHANGELOG.md`.
3. Será feito um build de testes (`dry-run`) para garantir que os pacotes compilam corretamente.
4. Se o título estiver errado ou o CHANGELOG não estiver preenchido, a esteira bloqueará o merge.

### Passo 4: Aprovação e Merge

Um mantenedor autorizado (Code Owner) deve revisar e aprovar o Pull Request.
Após a aprovação oficial, faça o **Merge** do Pull Request na branch `master`.

### Passo 5: A automação faz o resto! (CD)

Assim que o merge for concluído, duas esteiras são disparadas em sequência:

1. **Criação da Tag:** A esteira `tag-release` detecta que um PR com título `Release vX.Y.Z` foi mergeado e cria automaticamente a tag `v1.2.0` no repositório.

2. **Build e Deploy:** A criação da tag dispara a esteira `publish-pypi`, que:
   - Gera os artefatos (`.whl` e `.tar.gz`) usando o `setuptools_scm` com a versão da tag.
   - Valida os artefatos com `twine check`.
   - Publica automaticamente no **TestPyPI** e no **PyPI** oficial (via Trusted Publishing OIDC).

Pronto! Em alguns minutos a nova versão estará disponível para todo o mundo via `pip install ds-contest-tools`.

---

## ⚠️ Regras Importantes

* O formato da versão no CHANGELOG deve ser estritamente `[X.Y.Z]`.
* O título do Pull Request de release deve ser estritamente `Release vX.Y.Z`.
* As aprovações de Pull Request na `master` são restritas aos responsáveis configurados no `CODEOWNERS`.
* **Não crie tags manualmente.** A esteira `tag-release` é responsável por isso após o merge.
