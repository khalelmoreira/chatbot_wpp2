# Dev container — chatbot_wpp2

## Onde colocar
Copie a pasta `.devcontainer/` inteira pra raiz do seu repositório, ao lado de `app.py`.

## Engine

Docker diretamente (nada de Podman aqui). Dockerfile e devcontainer.json seguem
o spec padrão, sem nada específico de engine — pra trocar pra Podman, só
apontar a extensão pro socket dele (`dev.containers.dockerPath` ou pacote
`podman-docker`), sem editar esses arquivos.

## Rodando

1. Abra a pasta do projeto no VS Code.
2. `Ctrl+Shift+P` → **Dev Containers: Reopen in Container**.
3. Espere o build (primeira vez demora mais, baixa a imagem base + instala o
   Claude Code).
4. Abra um terminal *dentro* do container (já abre lá por padrão) e rode:
   ```bash
   claude
   ```
5. Segue o prompt de login (abre navegador no host, autentica, volta pro terminal).

## O que isso te dá

- Claude Code só enxerga o workspace (seu repo) — resto do filesystem
  (`~/Documentos`, `~/.ssh`, etc.) não existe dentro do container.
- Login e settings persistem entre rebuilds (volume `claude-code-config-*`).
- Dá pra rodar com `claude --dangerously-skip-permissions` — pior caso fica
  contido no container/repo, reversível via git.

## O que isso NÃO te dá

- Não monta `~/.ssh` nem credenciais de nuvem — pra git push autenticado, use
  um token de longa duração escopado ao repo.
- Sem firewall de egress (acesso de rede normal). Pra travar isso, ver
  `init-firewall.sh` no repo de referência (`anthropics/claude-code/.devcontainer`).
