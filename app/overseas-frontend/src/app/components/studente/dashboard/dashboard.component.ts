// components/studente/dashboard/dashboard.component.ts
import { Component, OnInit } from '@angular/core';
import { RouterLink } from '@angular/router';
import { CommonModule } from '@angular/common';
import { PraticaService } from '../../../services/pratica.service';
import { PraticaMobilita } from '../../../models/models';

@Component({
  selector: 'app-studente-dashboard',
  standalone: true,
  imports: [RouterLink, CommonModule],
  template: `
    <div class="page-header">
      <div>
        <h1 class="page-title">Le mie pratiche</h1>
        <p class="page-sub">Panoramica delle tue mobilità Overseas</p>
      </div>
      <a routerLink="/studente/nuova-pratica" class="btn btn-primary">+ Nuova pratica</a>
    </div>

    <!-- Metriche -->
    <div class="cards-grid">
      <div class="metric-card">
        <div class="metric-label">Totale pratiche</div>
        <div class="metric-value blue">{{ pratiche.length }}</div>
      </div>
      <div class="metric-card">
        <div class="metric-label">In corso</div>
        <div class="metric-value blue">{{ contaStato('mobilita_in_corso') }}</div>
      </div>
      <div class="metric-card">
        <div class="metric-label">In approvazione</div>
        <div class="metric-value amber">{{ contaStato('in_attesa_approvazione_la') }}</div>
      </div>
      <div class="metric-card">
        <div class="metric-label">Chiuse</div>
        <div class="metric-value green">{{ contaStato('chiusa') }}</div>
      </div>
    </div>

    <!-- Tabella pratiche -->
    <div class="card">
      <div class="card-title">Pratiche di mobilità</div>

      @if (loading) {
        <p class="text-muted">Caricamento...</p>
      } @else if (pratiche.length === 0) {
        <p class="text-muted">Non hai ancora nessuna pratica. Creane una!</p>
      } @else {
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Anno Acc.</th><th>Istituto</th><th>Paese</th><th>Periodo</th><th>Stato</th><th>Azioni</th>
              </tr>
            </thead>
            <tbody>
              @for (pratica of pratiche; track pratica.id) {
                <tr>
                  <td>{{ pratica.anno_accademico }}</td>
                  <td>{{ pratica.istituto.nome }}</td>
                  <td>{{ pratica.istituto.paese }}</td>
                  <td>{{ pratica.periodo }}</td>
                  <td><span [class]="'badge ' + getBadgeClass(pratica.stato)">{{ getStatoLabel(pratica.stato) }}</span></td>
                  <td>
                    <a [routerLink]="['/studente/pratica', pratica.id]" class="btn btn-sm">Dettaglio</a>
                  </td>
                </tr>
              }
            </tbody>
          </table>
        </div>
      }
    </div>
  `,
  styles: []
})
export class StudenteDashboardComponent implements OnInit {
  pratiche: PraticaMobilita[] = [];
  loading = true;

  constructor(private praticaService: PraticaService) {}

  ngOnInit() {
    this.praticaService.getMiePratiche().subscribe({
     next: (data: PraticaMobilita[]) => { this.pratiche = data; this.loading = false; },
      error: () => { this.loading = false; }
    });
  }

  contaStato(stato: string): number {
    return this.pratiche.filter(p => p.stato === stato).length;
  }

  getBadgeClass(stato: string): string {
    const map: Record<string, string> = {
      'creata': 'badge-created',
      'in_attesa_approvazione_la': 'badge-waiting',
      'pre_partenza_completata': 'badge-approved',
      'mobilita_in_corso': 'badge-progress',
      'in_riconoscimento_esami': 'badge-waiting',
      'chiusa': 'badge-closed'
    };
    return map[stato] ?? 'badge-created';
  }

  getStatoLabel(stato: string): string {
    const map: Record<string, string> = {
      'creata': 'Creata',
      'in_attesa_approvazione_la': 'Attesa approvazione LA',
      'pre_partenza_completata': 'Pre-partenza completata',
      'mobilita_in_corso': 'Mobilità in corso',
      'in_riconoscimento_esami': 'In riconoscimento esami',
      'chiusa': 'Chiusa'
    };
    return map[stato] ?? stato;
  }
}
