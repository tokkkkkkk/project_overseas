// components/navbar/navbar.component.ts
import { Component, computed } from '@angular/core';
import { RouterLink, RouterLinkActive } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-navbar',
  standalone: true,
  imports: [RouterLink, RouterLinkActive, CommonModule],
  template: `
    <!-- Top bar -->
    <header class="topbar">
      <div class="topbar-brand">
        <span class="brand-icon">🌍</span>
        Overseas — Ca' Foscari
      </div>
      <div class="topbar-right">
        <span class="user-name">{{ auth.utenteCorrente()?.nome }} {{ auth.utenteCorrente()?.cognome }}</span>
        <span class="user-role">{{ ruoloLabel() }}</span>
        <button class="btn-logout" (click)="auth.logout()">Esci</button>
      </div>
    </header>

    <!-- Sidebar -->
    <nav class="sidebar">
      <div class="nav-section">
        <div class="nav-section-title">Menu</div>

        @if (auth.getRuolo() === 'studente') {
          <a class="nav-item" routerLink="/studente/dashboard" routerLinkActive="active">
            📋 Dashboard
          </a>
          <a class="nav-item" routerLink="/studente/nuova-pratica" routerLinkActive="active">
            ➕ Nuova pratica
          </a>
        }

        @if (auth.getRuolo() === 'docente') {
          <a class="nav-item" routerLink="/docente/dashboard" routerLinkActive="active">
            📋 Dashboard
          </a>
        }

        @if (auth.getRuolo() === 'ufficio') {
          <a class="nav-item" routerLink="/ufficio/dashboard" routerLinkActive="active">
            📋 Dashboard
          </a>
          <a class="nav-item" routerLink="/ufficio/istituti" routerLinkActive="active">
            🏛️ Istituti partner
          </a>
        }
      </div>
    </nav>
  `,
  styles: [`
    .topbar {
      position: fixed; top: 0; left: 0; right: 0; height: 56px;
      background: #1a3a6b; display: flex; align-items: center;
      justify-content: space-between; padding: 0 1.5rem; z-index: 100;
    }
    .topbar-brand { color: #fff; font-size: 16px; font-weight: 500; display: flex; align-items: center; gap: 8px; }
    .brand-icon { font-size: 20px; }
    .topbar-right { display: flex; align-items: center; gap: 12px; }
    .user-name { color: #ccd9f0; font-size: 13px; }
    .user-role { background: #2d5bb3; color: #aec6f0; font-size: 11px; padding: 2px 8px; border-radius: 10px; }
    .btn-logout { background: transparent; border: 1px solid #4a7bc4; color: #aec6f0; padding: 4px 12px; border-radius: 6px; cursor: pointer; font-size: 12px; }
    .btn-logout:hover { background: #2d5bb3; }
    .sidebar {
      position: fixed; top: 56px; left: 0; bottom: 0; width: 220px;
      background: #fff; border-right: 1px solid #e8ecf0; padding: 1.5rem 0; overflow-y: auto;
    }
    .nav-section { padding: 0 1rem; }
    .nav-section-title { font-size: 11px; color: #9aa0b0; text-transform: uppercase; letter-spacing: 0.08em; padding: 0 0.5rem; margin-bottom: 6px; }
    .nav-item {
      display: flex; align-items: center; gap: 8px; padding: 8px 12px;
      border-radius: 8px; cursor: pointer; color: #5a6070; font-size: 13px;
      text-decoration: none; margin-bottom: 2px; transition: background 0.15s;
    }
    .nav-item:hover { background: #f0f4f8; color: #1a3a6b; }
    .nav-item.active { background: #e8eef8; color: #1a3a6b; font-weight: 500; }
  `]
})
export class NavbarComponent {
  constructor(public auth: AuthService) {}

  ruoloLabel = computed(() => {
    const r = this.auth.getRuolo();
    if (r === 'studente') return 'Studente';
    if (r === 'docente') return 'Docente referente';
    if (r === 'ufficio') return 'Ufficio Overseas';
    return '';
  });
}
