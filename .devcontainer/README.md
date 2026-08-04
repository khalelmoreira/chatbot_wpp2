# Dev container — chatbot_wpp2

## Onde colocar
Copie a pasta `.devcontainer/` inteira pra raiz do seu repositório, ao lado de `app.py`.

## Usando Podman no Fedora (em vez de Docker)

O Fedora já vem com Podman. O VS Code Dev Containers extension fala com "docker" por
padrão, mas dá pra apontar pro socket do Podman de duas formas:

**Opção A — symlink `docker` -> `podman` (mais simples):**
```bash
sudo dnf install -y podman podman-docker
```
O pacote `podman-docker` cria o comando `docker` como alias de `podman`, então a
extensão nem percebe a diferença.

**Opção B — apontar a extensão direto pro Podman:**
No VS Code, em `settings.json`:
```json
"dev.containers.dockerPath": "podman"
```

Em ambos os casos, o socket do Podman precisa estar ativo:
```bash
systemctl --user enable --now podman.socket
```

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
