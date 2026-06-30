// services/auth.service.ts
import { Injectable, signal, PLATFORM_ID, inject } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { tap } from 'rxjs/operators';
import { AuthResponse, Utente } from '../models/models';

@Injectable({ providedIn: 'root' })
export class AuthService {

  // URL base del backend — cambia porta se usi Node.js (3000) o Flask (5000)
  private apiUrl = 'http://localhost:5000/api';

  // Rileva se siamo nel browser (true) o lato server/SSR (false)
  private isBrowser = isPlatformBrowser(inject(PLATFORM_ID));

  // Signal: stato reattivo dell'utente loggato
  utenteCorrente = signal<Utente | null>(null);

  constructor(private http: HttpClient, private router: Router) {
    // All'avvio, ripristina utente dal localStorage se c'è un token
    // Solo se siamo nel browser, altrimenti localStorage non esiste (SSR)
    if (this.isBrowser) {
      const saved = localStorage.getItem('utente');
      if (saved) this.utenteCorrente.set(JSON.parse(saved));
    }
  }

  login(username: string, password: string) {
    return this.http.post<AuthResponse>(`${this.apiUrl}/login`, { username, password }).pipe(
      tap(res => {
        if (this.isBrowser) {
          localStorage.setItem('token', res.token);
          localStorage.setItem('utente', JSON.stringify(res.utente));
        }
        this.utenteCorrente.set(res.utente);
      })
    );
  }

  logout() {
    if (this.isBrowser) {
      localStorage.removeItem('token');
      localStorage.removeItem('utente');
    }
    this.utenteCorrente.set(null);
    this.router.navigate(['/login']);
  }

  getToken(): string | null {
    if (!this.isBrowser) return null;
    return localStorage.getItem('token');
  }

  isLoggedIn(): boolean {
    return !!this.getToken();
  }

  getRuolo(): string | null {
    return this.utenteCorrente()?.ruolo ?? null;
  }
}