// guards/auth.guard.ts
import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { AuthService } from '../services/auth.service';

// Blocca l'accesso se non loggato
export const authGuard: CanActivateFn = () => {
  const auth = inject(AuthService);
  const router = inject(Router);
  if (auth.isLoggedIn()) return true;
  return router.createUrlTree(['/login']);
};

// Blocca l'accesso se non sei studente
export const studenteGuard: CanActivateFn = () => {
  const auth = inject(AuthService);
  const router = inject(Router);
  if (auth.getRuolo() === 'studente') return true;
  return router.createUrlTree(['/login']);
};

// Blocca l'accesso se non sei docente
export const docenteGuard: CanActivateFn = () => {
  const auth = inject(AuthService);
  const router = inject(Router);
  if (auth.getRuolo() === 'docente') return true;
  return router.createUrlTree(['/login']);
};

// Blocca l'accesso se non sei ufficio
export const ufficioGuard: CanActivateFn = () => {
  const auth = inject(AuthService);
  const router = inject(Router);
  if (auth.getRuolo() === 'ufficio') return true;
  return router.createUrlTree(['/login']);
};
