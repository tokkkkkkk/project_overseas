// app.routes.ts
import { Routes } from '@angular/router';
import { authGuard, studenteGuard, docenteGuard, ufficioGuard } from './guards/auth.guard';

export const routes: Routes = [
  // Redirect radice al login
  { path: '', redirectTo: '/login', pathMatch: 'full' },

  // Login (pubblica)
  {
    path: 'login',
    loadComponent: () => import('./components/login/login.component').then(m => m.LoginComponent)
  },

  // Registrazione (pubblica)
  {
    path: 'register',
    loadComponent: () => import('./components/register/register.component').then(m => m.RegisterComponent)
  },

  // --- STUDENTE ---
  {
    path: 'studente',
    canActivate: [authGuard, studenteGuard],
    children: [
      { path: '', redirectTo: 'dashboard', pathMatch: 'full' },
      {
        path: 'dashboard',
        loadComponent: () => import('./components/studente/dashboard/dashboard.component').then(m => m.StudenteDashboardComponent)
      },
      {
        path: 'nuova-pratica',
        loadComponent: () => import('./components/studente/nuova-pratica/nuova-pratica.component').then(m => m.NuovaPraticaComponent)
      },
      {
        path: 'pratica/:id',
        loadComponent: () => import('./components/studente/dettaglio-pratica/dettaglio-pratica.component').then(m => m.DettaglioPraticaComponent)
      }
    ]
  },

  // --- DOCENTE ---
  {
    path: 'docente',
    canActivate: [authGuard, docenteGuard],
    children: [
      { path: '', redirectTo: 'dashboard', pathMatch: 'full' },
      {
        path: 'dashboard',
        loadComponent: () => import('./components/docente/dashboard/dashboard.component').then(m => m.DocenteDashboardComponent)
      },
      {
        path: 'valuta-la/:id',
        loadComponent: () => import('./components/docente/valuta-la/valuta-la.component').then(m => m.ValutaLaComponent)
      },
      {
        path: 'riconosci-esami/:id',
        loadComponent: () => import('./components/docente/riconosci-esami/riconosci-esami.component').then(m => m.RiconosciEsamiComponent)
      }
    ]
  },

  // --- UFFICIO ---
  {
    path: 'ufficio',
    canActivate: [authGuard, ufficioGuard],
    children: [
      { path: '', redirectTo: 'dashboard', pathMatch: 'full' },
      {
        path: 'dashboard',
        loadComponent: () => import('./components/ufficio/dashboard/dashboard.component').then(m => m.UfficioDashboardComponent)
      },
      {
        path: 'pratica/:id',
        loadComponent: () => import('./components/ufficio/dettaglio-pratica/dettaglio-pratica.component').then(m => m.UfficioDettaglioPraticaComponent)
      },
      {
        path: 'istituti',
        loadComponent: () => import('./components/ufficio/istituti/istituti.component').then(m => m.IstitutiComponent)
      }
    ]
  },

  // Fallback
  { path: '**', redirectTo: '/login' }
];