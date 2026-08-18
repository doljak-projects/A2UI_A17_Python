---
issue: 75
title: "[Front] -GOOGLE-A2UI- Define a custom weather widget component with Zod schema + binding()"
branch: feat/a2ui-custom-catalog-75-77-humidity-gauge
status: closed
last_updated: 08-18-2026
---

# Issue #75 — Define a custom weather widget component with Zod schema + binding()

## Objective
Até aqui o projeto só usou o `BasicCatalog` padrão do SDK A2UI. Esta issue define o primeiro componente customizado do projeto — `HumidityGauge`, um indicador visual de umidade — com schema Zod e binding ao data model, seguindo o padrão de catálogos customizados do protocolo A2UI da Google.

## Scope
- `components/humidity-gauge/humidity-gauge.component.ts` (novo): `HumidityGaugeComponent extends CatalogComponent<typeof humidityGaugeApi>`
- `humidityGaugeSchema` (Zod, `DynamicNumberSchema` pro campo `humidity`, `.strict()`)
- `humidityGaugeApi` (`ComponentApi`) e `humidityGaugeEntry` (`AngularComponentImplementation`) — a "entrada" pronta pra registrar num catálogo
- Reference: `docs/tutorial_A2UI/05-custom-catalogs-in-a2ui.md` (Passo 1)

## Decisões de implementação
- **`extends CatalogComponent<typeof humidityGaugeApi>`** em vez de implementar a interface do zero — o SDK (`@a2ui/angular/v0_9`) já expõe essa classe base cuidando do binding de `props()` a partir do schema declarado em `humidityGaugeApi`, evitando reimplementar a leitura de `{ path }` manualmente.
- **`DynamicNumberSchema`** (do SDK, `@a2ui/web_core/v0_9`) em vez de `z.number()` puro — aceita tanto um valor concreto quanto um binding (`{ path: '...' }`), igual ao padrão `BoundProperty<T>` documentado no artigo original de catálogos customizados.
- **Nível de umidade (`baixa`/`moderada`/`alta`) derivado via `computed()`**, não armazenado — segue o padrão de signals já usado em outros componentes do catálogo básico (ex: `Text`), evitando estado duplicado.

## Status
> Atualizado em: 08-18-2026

- [x] `HumidityGaugeComponent` implementado, com schema Zod e binding funcional.
- [x] **Validação funcional:** `ng build` limpo. `ng test`: 47/50 verdes (3 falhas pré-existentes, sem relação). Validado integrado ao catálogo customizado na issue #76 e ao card real na #77, no mesmo PR.

## Notes
- Implementado originalmente por sessão do Cursor (não commitado); esta issue documenta a versão reorganizada em branch própria, encadeada sobre a Parte 4 (issues #72-74).
