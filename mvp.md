# Cronograma de Lançamento MVP — Automação NFS-e

---

## Semanas 1–2 — Fluxo de Prestador (Org API)

### Semana 1 — Retrabalho do existente + integração
- [ ] Revisar e corrigir a máquina de estados do onboarding, aplicando a mesma separação de responsabilidades já usada no fluxo de emissão (extração, validação, persistência como serviços distintos)
- [ ] Corrigir bugs conhecidos de lógica de estado antes de tocar na integração — tratar como tarefas separadas
- [ ] Implementar/revisar autenticação e chamada de criação de prestador na Org API da Notaas
- [ ] Mapear e tratar erros específicos da Org API

### Semana 2 — Merge, prompt e validação end-to-end
- [ ] Corrigir o passo de merge (dados re-digitados vs. cadastro parcial existente)
- [ ] Adaptar/simplificar o prompt de extração para dados de prestador
- [ ] Teste end-to-end: cadastro de um prestador real do zero até virar `Prestador` funcional
- [ ] Testes de borda: prestador parcialmente cadastrado, dados divergentes entre tentativas, regime tributário inválido