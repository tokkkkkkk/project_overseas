// components/register/register.component.ts
import { Component,ChangeDetectorRef  } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [FormsModule, CommonModule, RouterLink],
  template: `
    <div class="register-wrap">
      <div class="register-card">
        <div class="register-logo">
          <div class="logo-icon">🌍</div>
          <h1 class="register-title">Registrazione</h1>
          <p class="register-sub">Università Ca' Foscari Venezia</p>
        </div>

        @if (errore) {
          <div class="alert-error">{{ errore }}</div>
        }
        @if (successo) {
          <div class="alert-success">{{ successo }}</div>
        }

        <div class="form-row">
          <div class="form-group">
            <label class="form-label">Nome</label>
            <input class="form-control" type="text" [(ngModel)]="nome" placeholder="Mario" />
          </div>
          <div class="form-group">
            <label class="form-label">Cognome</label>
            <input class="form-control" type="text" [(ngModel)]="cognome" placeholder="Rossi" />
          </div>
        </div>

        <div class="form-group">
          <label class="form-label">Username</label>
          <input class="form-control" type="text" [(ngModel)]="username" placeholder="mario.rossi" />
        </div>
      
        <div class="form-group">
          <label class="form-label">Ruolo</label>
          <select class="form-control" [(ngModel)]="ruolo">
            <option value="studente">Studente</option>
            <option value="docente">Docente Referente</option>
            <option value="ufficio">Ufficio Overseas</option>
          </select>
        </div>

        <div class="form-group">
          <label class="form-label">Password</label>
          <input class="form-control" type="password" [(ngModel)]="password" placeholder="••••••••" />
        </div>

        <div class="form-group">
          <label class="form-label">Conferma password</label>
          <input class="form-control" type="password" [(ngModel)]="confermaPassword" (keyup.enter)="registra()" placeholder="••••••••" />
        </div>

        <button class="btn-register" (click)="registra()" [disabled]="loading">
          {{ loading ? 'Registrazione in corso...' : 'Registrati' }}
        </button>

        <p class="login-link">
          Hai già un account? <a routerLink="/login">Accedi</a>
        </p>
      </div>
    </div>
  `,
  styles: [`
    .register-wrap { min-height: 100vh; display: flex; align-items: center; justify-content: center; background: #f0f4f8; padding: 2rem; }
    .register-card { background: #fff; border: 1px solid #e0e6ed; border-radius: 16px; padding: 2.5rem; width: 420px; }
    .register-logo { text-align: center; margin-bottom: 1.5rem; }
    .logo-icon { font-size: 40px; margin-bottom: 8px; }
    .register-title { font-size: 20px; font-weight: 500; color: #1a3a6b; margin: 0; }
    .register-sub { font-size: 13px; color: #7a8090; margin: 4px 0 0; }
    .form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
    .form-group { margin-bottom: 1rem; }
    .form-label { font-size: 13px; color: #5a6070; margin-bottom: 5px; display: block; }
    .form-control { width: 100%; padding: 8px 12px; border: 1px solid #d0d8e0; border-radius: 8px; font-size: 14px; box-sizing: border-box; }
    .form-control:focus { outline: none; border-color: #1a3a6b; box-shadow: 0 0 0 3px rgba(26,58,107,0.1); }
    .btn-register { width: 100%; padding: 10px; background: #1a3a6b; color: #fff; border: none; border-radius: 8px; font-size: 14px; cursor: pointer; margin-top: 0.5rem; }
    .btn-register:hover { background: #2d5bb3; }
    .btn-register:disabled { opacity: 0.6; cursor: not-allowed; }
    .alert-error { background: #fef0f0; border: 1px solid #f5c0c0; color: #a32d2d; padding: 10px 14px; border-radius: 8px; font-size: 13px; margin-bottom: 1rem; }
    .alert-success { background: #eaf3de; border: 1px solid #97c459; color: #27500a; padding: 10px 14px; border-radius: 8px; font-size: 13px; margin-bottom: 1rem; }
    .login-link { text-align: center; font-size: 13px; color: #7a8090; margin-top: 1rem; }
    .login-link a { color: #1a3a6b; font-weight: 500; text-decoration: none; }
    .login-link a:hover { text-decoration: underline; }
  `]
})
export class RegisterComponent {
  nome = '';
  cognome = '';
  username = '';
  password = '';
  ruolo = 'studente';
  confermaPassword = '';
  errore = '';
  successo = '';
  loading = false;

  private apiUrl = 'http://localhost:5000/api';

  constructor(private http: HttpClient, private router: Router, private cdr: ChangeDetectorRef) { }

  registra() {
    this.errore = '';
    this.successo = '';

    if (!this.nome || !this.cognome || !this.username || !this.password) {
      this.errore = 'Compila tutti i campi';
      return;
    }
    if (this.password !== this.confermaPassword) {
      this.errore = 'Le password non coincidono';
      return;
    }
    if (this.password.length < 6) {
      this.errore = 'La password deve avere almeno 6 caratteri';
      return;
    }

    this.loading = true;
    


    this.http.post(`${this.apiUrl}/auth/register`, {
      username: this.username,
      password: this.password,
      nome: this.nome,
      ruolo: this.ruolo,
      cognome: this.cognome,
    }).subscribe({
      next: () => {
        this.successo = 'Registrazione completata! Reindirizzamento al login...';
        this.loading = false;
        setTimeout(() => this.router.navigate(['/login']), 1500);
      },
      error: (err) => {
        this.errore = err.error?.msg ?? 'Errore durante la registrazione';
        this.loading = false;
        this.cdr.detectChanges();
      }
    });
  }
}
