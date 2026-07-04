// app.config.ts
import { provideRouter, withHashLocation } from '@angular/router';
import { provideHttpClient, withInterceptors } from '@angular/common/http';
import { routes } from './app.routes';
import { authInterceptor } from './interceptors/auth.interceptor';
import { ApplicationConfig, provideZoneChangeDetection } from '@angular/core'; // <-- Add provideZoneChangeDetection here

export const appConfig: ApplicationConfig = {
  providers: [
    provideZoneChangeDetection({ eventCoalescing: true }), // <-- ADD THIS LINE
    provideRouter(routes,),
    provideHttpClient(withInterceptors([authInterceptor]))
  ]
};
