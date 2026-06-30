// components/login/login.component.ts
import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [FormsModule, CommonModule, RouterLink],
  template: `
<<<<<<< HEAD
  @if (checking) {
  <div class="login-wrap">
    <p style="color:#7a8090;font-size:13px">Caricamento...</p>
  </div>
} @else {
  <div class="login-wrap">
    <!-- tutto il resto del form invariato -->
  </div>
}
=======
>>>>>>> c3cd31bdbf6c12b3d280b09d33536c8539992b87
    <div class="login-wrap">
      <div class="login-card">
        <div class="login-logo">
          <div class="logo-icon">🌍</div>
          <h1 class="login-title">Portale Overseas</h1>
          <p class="login-sub">Università Ca' Foscari Venezia</p>
        </div>

        @if (errore) {
          <div class="alert-error">{{ errore }}</div>
        }

        <div class="form-group">
          <label class="form-label">Username</label>
          <input class="form-control" type="text" [(ngModel)]="username" placeholder="mario.rossi" />
        </div>
        <div class="form-group">
          <label class="form-label">Password</label>
          <input class="form-control" type="password" [(ngModel)]="password" (keyup.enter)="login()" placeholder="••••••••" />
        </div>
        <button class="btn-login" (click)="login()" [disabled]="loading">
          {{ loading ? 'Accesso in corso...' : 'Accedi' }}
        </button>

        <p class="register-link">
          Non hai un account? <a routerLink="/register">Registrati</a>
        </p>
      </div>
    </div>
  `,
  styles: [`
    .login-wrap { min-height: 100vh; display: flex; align-items: center; justify-content: center; background: #f0f4f8; }
    .login-card { background: #fff; border: 1px solid #e0e6ed; border-radius: 16px; padding: 2.5rem; width: 380px; }
    .login-logo { text-align: center; margin-bottom: 2rem; }
    .logo-icon { font-size: 40px; margin-bottom: 8px; }
    .login-title { font-size: 20px; font-weight: 500; color: #1a3a6b; margin: 0; }
    .login-sub { font-size: 13px; color: #7a8090; margin: 4px 0 0; }
    .form-group { margin-bottom: 1rem; }
    .form-label { font-size: 13px; color: #5a6070; margin-bottom: 5px; display: block; }
    .form-control { width: 100%; padding: 8px 12px; border: 1px solid #d0d8e0; border-radius: 8px; font-size: 14px; box-sizing: border-box; }
    .form-control:focus { outline: none; border-color: #1a3a6b; box-shadow: 0 0 0 3px rgba(26,58,107,0.1); }
    .btn-login { width: 100%; padding: 10px; background: #1a3a6b; color: #fff; border: none; border-radius: 8px; font-size: 14px; cursor: pointer; margin-top: 0.5rem; }
    .btn-login:hover { background: #2d5bb3; }
    .btn-login:disabled { opacity: 0.6; cursor: not-allowed; }
    .alert-error { background: #fef0f0; border: 1px solid #f5c0c0; color: #a32d2d; padding: 10px 14px; border-radius: 8px; font-size: 13px; margin-bottom: 1rem; }
    .register-link { text-align: center; font-size: 13px; color: #7a8090; margin-top: 1rem; }
    .register-link a { color: #1a3a6b; font-weight: 500; text-decoration: none; }
    .register-link a:hover { text-decoration: underline; }
  `]
})
export class LoginComponent {
  username = '';
  password = '';
  errore = '';
  loading = false;
<<<<<<< HEAD
 checking = true; // nuovo

  constructor(private auth: AuthService, private router: Router) {
    if (this.auth.isLoggedIn()) {
      const ruolo = this.auth.getRuolo();
      if (ruolo === 'studente') this.router.navigate(['/studente/dashboard']);
      else if (ruolo === 'docente') this.router.navigate(['/docente/dashboard']);
      else if (ruolo === 'ufficio') this.router.navigate(['/ufficio/dashboard']);
    } else {
      this.checking = false; // mostra il form solo se non loggato
    }
  }
=======

  constructor(private auth: AuthService, private router: Router) {}
>>>>>>> c3cd31bdbf6c12b3d280b09d33536c8539992b87

  login() {
    if (!this.username || !this.password) {
      this.errore = 'Inserisci username e password';
      return;
    }
    this.loading = true;
    this.errore = '';

    this.auth.login(this.username, this.password).subscribe({
      next: (res) => {
        // Reindirizza alla dashboard giusta in base al ruolo
        const ruolo = res.ruolo;
        if (ruolo === 'studente') this.router.navigate(['/studente/dashboard']);
        else if (ruolo === 'docente') this.router.navigate(['/docente/dashboard']);
        else this.router.navigate(['/ufficio/dashboard']);
      },
      error: () => {
        this.errore = 'Username o password errati';
        this.loading = false;
      }
    });
  }
}