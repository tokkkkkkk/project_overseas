// interceptors/auth.interceptor.ts
import { HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { AuthService } from '../services/auth.service';

// Aggiunge automaticamente il JWT token ad ogni richiesta HTTP
export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const authService = inject(AuthService);
  const token = authService.getToken();

  console.log('🌐 Interceptor in azione per:', req.url);
  console.log('🔑 Token trovato:', token ? 'SÌ' : 'NO (Vuoto!)');
  if (token) {
    const reqConToken = req.clone({
      headers: req.headers.set('Authorization', `Bearer ${token}`)
    });
    return next(reqConToken);
  }

  return next(req);
};
