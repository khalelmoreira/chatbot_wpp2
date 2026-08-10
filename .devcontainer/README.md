# Dev container — chatbot_wpp2

## Onde colocar
Copie a pasta `.devcontainer/` inteira pra raiz do seu repositório, ao lado de `app.py`.

## Engine

Usa Docker diretamente (nada de Podman aqui). Nada no Dockerfile ou no
devcontainer.json é específico de engine — segue o spec padrão de devcontainers
— então se um dia precisar rodar em Podman de novo, basta apontar a extensão
pro socket dele (`dev.containers.dockerPath` no settings.json, ou o pacote
`podman-docker`), sem tocar nesses arquivos.

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

- Claude Code só enxerga o que está montado como workspace (seu repo) — o resto
  do seu filesystem (`~/Documentos`, `~/.ssh`, etc.) simplesmente não existe
  dentro do container.
- Login e settings persistem entre rebuilds (volume nomeado `claude-code-config-*`).
- Dá pra rodar com `claude --dangerously-skip-permissions` sem ficar confirmando
  cada ação, porque o pior caso de dano fica contido no container/repo (que está
  sob git, então reversível).

## O que isso NÃO te dá (seja realista sobre isso)

- Não monta `~/.ssh` nem credenciais de nuvem — se precisar de git push
  autenticado, use um token de longa duração escopado ao repo, não sua chave
  SSH pessoal.
- Não tem firewall de egress configurado aqui (o container tem acesso de rede
  normal). Se quiser travar isso também, o repo de referência oficial
  (`anthropics/claude-code/.devcontainer`) tem um `init-firewall.sh` que
  bloqueia tudo exceto os domínios que o Claude Code precisa — posso adaptar
  pra esse setup se quiser esse nível extra depois.
