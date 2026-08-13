FROM python:3.14-slim-bookworm

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    sqlite3 \
    build-essential \
    ca-certificates \
    sudo \
    && rm -rf /var/lib/apt/lists/*

ARG USERNAME=dev
RUN useradd --create-home --shell /bin/bash ${USERNAME} \
    && echo "${USERNAME} ALL=(root) NOPASSWD: /usr/bin/chown -R ${USERNAME}\:${USERNAME} *" \
       > /etc/sudoers.d/${USERNAME} \
    && chmod 0440 /etc/sudoers.d/${USERNAME}

USER ${USERNAME}
WORKDIR /tmp
RUN curl -fsSL https://claude.ai/install.sh | bash
ENV PATH="/home/${USERNAME}/.local/bin:${PATH}"

WORKDIR /workspace