import type { A2uiMessage } from '@a2ui/web_core/v0_9';

export interface SimpleCardData {
  title: string;
  subtitle: string;
}

/**
 * Monta o ciclo mínimo de mensagens A2UI (createSurface -> updateComponents ->
 * updateDataModel) para um card estático com título e subtítulo, ligados ao
 * data model via `{ path }` em vez de valor embutido no componente.
 */
export function createSimpleCard(
  surfaceId: string,
  catalogId: string,
  data: SimpleCardData,
): A2uiMessage[] {
  return [
    {
      version: 'v0.9',
      createSurface: { surfaceId, catalogId },
    },
    {
      version: 'v0.9',
      updateComponents: {
        surfaceId,
        components: [
          // `<a2ui-v09-surface>` renderiza por convenção o componente de id
          // 'root' (default de `SurfaceComponent.componentKey`), não infere
          // a raiz pela árvore de referências.
          { id: 'root', component: 'Card', child: 'card-column' },
          {
            id: 'card-column',
            component: 'Column',
            children: ['card-title', 'card-subtitle'],
          },
          {
            id: 'card-title',
            component: 'Text',
            variant: 'h3',
            text: { path: '/title' },
          },
          {
            id: 'card-subtitle',
            component: 'Text',
            variant: 'body',
            text: { path: '/subtitle' },
          },
        ],
      },
    },
    {
      version: 'v0.9',
      updateDataModel: { surfaceId, value: data },
    },
  ];
}
