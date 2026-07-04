// interceptors/auth.interceptor.ts
import { HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core'; 
import { catchError, throwError } from 'rxjs';
import { AuthService } from '../services/auth.service';

// Aggiunge automaticamente il JWT token ad ogni richiesta HTTP
export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const authService = inject(AuthService);
  const token = authService.getToken();

  const reqConToken = token
    ? req.clone({ headers: req.headers.set('Authorization', `Bearer ${token}`) })
    : req;

  return next(reqConToken).pipe(
    catchError((err) => {
      if (err.status === 401) {
        authService.logout(); // pulisce token + reindirizza a /login
      }
      return throwError(() => err);
    })
  );
};
