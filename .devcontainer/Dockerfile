FROM python:3.14-slim-bookworm

# Ferramentas de sistema necessárias pro projeto (git, sqlite3 CLI, build tools
# pra dependências Python que compilam C, curl pra debug de rede)
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    sqlite3 \
    build-essential \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Usuário não-root — obrigatório pra poder rodar
# `claude --dangerously-skip-permissions` (a CLI recusa rodar como root)
ARG USERNAME=dev
RUN useradd --create-home --shell /bin/bash ${USERNAME}
USER ${USERNAME}
WORKDIR /workspace

# requirements.txt é copiado e instalado no postCreateCommand (ver devcontainer.json),
# não aqui, pra não precisar rebuildar a imagem toda vez que uma dependência muda
