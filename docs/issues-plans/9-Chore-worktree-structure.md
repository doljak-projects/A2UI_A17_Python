---
issue: 9
title: "[Chore] Organize worktree structure and update README"
branch: chore/worktree-structure-9-organize-and-update-readme
status: closed
last_updated: 07-25-2026
---

# Issue #9 — [Chore] Organize worktree structure and update README

## Objective
Establish and document the worktree organization pattern for the project, ensuring all active worktrees follow the naming convention and the README reflects the current workflow and project state.

## Scope
- Verify and rename existing worktrees to match the convention `<numero>-worktree-<tema>`
- Add a "Workflow" section to the README explaining worktree-based development flow
- Document branch naming convention and how to navigate between worktrees
- Update the README "Estado atual" section to reflect active branches

## Status
Feita — worktrees organizados em `wts/` e workflow documentado no README.

## O que foi feito
- Worktrees existentes renomeados/reorganizados para seguir a convenção `<numero>-worktree-<tema>` dentro do diretório `wts/` na raiz do monorepo.
- `.gitignore` da raiz atualizado para ignorar `wts/` (cada worktree é um clone de trabalho local, não versionado).
- `README.md` da raiz: nova seção **Workflow** explicando o fluxo de desenvolvimento com worktrees, convenção de branches (`feat/<numero>-<tema>`, `chore/`, `refactor/`) e como navegar entre worktrees.
- Seção **Estado atual** do README atualizada para refletir as branches ativas na época da issue.

## Como rastrear
- Branch: `chore/worktree-structure-9-organize-and-update-readme`
- Worktree: `9-worktree-worktree-structure` (ou equivalente em `wts/`)
- Arquivos principais: `README.md`, `.gitignore`, `wts/` (diretório de worktrees)

## Notes
- Padrão adotado: `wts/<numero>-worktree-<tema>` — facilita localizar o worktree de cada issue pelo número.
- Branches, commits e PRs continuam sendo feitos manualmente pelo usuário; esta issue só padronizou a estrutura e a documentação.
