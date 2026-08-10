FROM python:3.14-slim-bookworm

# Ferramentas de sistema necessárias pro projeto (git, sqlite3 CLI, build tools
# pra dependências Python que compilam C, curl pra debug de rede, sudo pro
# postCreateCommand poder se autocorrigir se o mount subir com ownership errado)
RUN apt-get update && apt-get install -y --no-install-recommends iptables ipset \
    git \
    curl \
    sqlite3 \
    build-essential \
    ca-certificates \
    sudo \
    && rm -rf /var/lib/apt/lists/*
    
COPY init-firewall.sh /usr/local/bin/init-firewall.sh
RUN chmod +x /usr/local/bin/init-firewall.sh

# Usuário não-root — obrigatório pra poder rodar
# `claude --dangerously-skip-permissions` (a CLI recusa rodar como root).
# sudo sem senha só pra esse usuário, só dentro do container — é o safety net
# de ownership usado no postCreateCommand (ver devcontainer.json).
ARG USERNAME=dev

USER ${USERNAME}
WORKDIR /workspace

# requirements.txt é copiado e instalado no postCreateCommand (ver devcontainer.json),
# não aqui, pra não precisar rebuildar a imagem toda vez que uma dependência muda