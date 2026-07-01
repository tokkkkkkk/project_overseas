// app.component.ts
import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { NavbarComponent } from './components/navbar/navbar.component';
import { AuthService } from './services/auth.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, NavbarComponent],
  template: `
    @if (auth.isLoggedIn()) {
      <app-navbar />
    }
    <main [class.with-sidebar]="auth.isLoggedIn()">
      <router-outlet />
    </main>
  `,
  styles: [`
    main { min-height: 100vh; background: #f5f6fa; }
    main.with-sidebar { 
    margin-left: 220px; 
    padding: 2rem;
    padding-top: calc(56px + 2rem);
  }
`]
})
export class AppComponent {
  constructor(public auth: AuthService) {}
}
