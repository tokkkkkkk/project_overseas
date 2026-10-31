import { RenderMode, ServerRoute } from '@angular/ssr';

export const serverRoutes: ServerRoute[] = [
  {
    path: 'studente/pratica/:id',
    renderMode: RenderMode.Client
  },
  {
    path: 'docente/valuta-la/:id',
    renderMode: RenderMode.Client
  },
  {
    path: 'docente/riconosci-esami/:id',
    renderMode: RenderMode.Client
  },
  {
    path: 'ufficio/pratica/:id',
    renderMode: RenderMode.Client
  },
  {
    path: '**',
    renderMode: RenderMode.Prerender
  }
];
