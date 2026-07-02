// components/docente/dashboard/dashboard.component.ts
import { Component, OnInit } from '@angular/core';
import { RouterLink } from '@angular/router';
import { CommonModule } from '@angular/common';
import { PraticaService } from '../../../services/pratica.service';
import { PraticaMobilita } from '../../../models/models';

@Component({
  selector: 'app-docente-dashboard',
  standalone: true,
  imports: [RouterLink, CommonModule],
  template: `
    <div class="page-header">
      <div>
        <h1 class="page-title">Pratiche assegnate</h1>
        <p class="page-sub">Pratiche per cui sei docente referente</p>
      </div>
    </div>

    <div class="cards-grid">
      <div class="metric-card"><div class="metric-label">Totale pratiche</div><div class="metric-value blue">{{ pratiche.length }}</div></div>
      <div class="metric-card"><div class="metric-label">LA da valutare</div><div class="metric-value amber">{{ laInAttesa.length }}</div></div>
      <div class="metric-card"><div class="metric-label">Esami da approvare</div><div class="metric-value blue">{{ esamiInAttesa.length }}</div></div>
    </div>

    <!-- LA da valutare -->
    @if (laInAttesa.length > 0) {
      <div class="card">
        <div class="card-title">Learning Agreement da valutare</div>
        <table>
          <thead><tr><th>Studente</th><th>Istituto</th><th>Periodo</th><th>LA caricato il</th><th>Azioni</th></tr></thead>
          <tbody>
            @for (p of laInAttesa; track p.ida) {
              <tr>
                <td>{{ p.studente.nome }} {{ p.studente.cognome }}</td>
                <td>{{ p.istituto.nome }}</td>
                <td>{{ p.periodo }}</td>
                <td>{{ getUltimoLa(p)?.data_caricamento | date:'dd/MM/yyyy' }}</td>
                <td style="display:flex;gap:6px">
                  <a [href]="'/api/files/' + getUltimoLa(p)?.filename" class="btn btn-sm" download>📄 Vedi LA</a>
                  <a [routerLink]="['/docente/valuta-la', p.ida]" class="btn btn-sm btn-success">✓ Valuta</a>
                </td>
              </tr>
            }
          </tbody>
        </table>
      </div>
    }

    <!-- Esami da riconoscere -->
    @if (esamiInAttesa.length > 0) {
      <div class="card">
        <div class="card-title">Esami da riconoscere</div>
        <table>
          <thead><tr><th>Studente</th><th>Istituto</th><th>N° esami</th><th>Azioni</th></tr></thead>
          <tbody>
            @for (p of esamiInAttesa; track p.ida) {
              <tr>
                <td>{{ p.studente.nome }} {{ p.studente.cognome }}</td>
                <td>{{ p.istituto.nome }}</td>
                <td>{{ p.mapping_esami.length }} esami</td>
                <td><a [routerLink]="['/docente/riconosci-esami', p.ida]" class="btn btn-sm btn-success">🎓 Riconosci esami</a></td>
              </tr>
            }
          </tbody>
        </table>
      </div>
    }

    <!-- Tutte le pratiche -->
    <div class="card">
      <div class="card-title">Tutte le pratiche</div>
      <table>
        <thead><tr><th>Studente</th><th>Istituto</th><th>Periodo</th><th>Stato</th></tr></thead>
        <tbody>
          @for (p of pratiche; track p.ida) {
            <tr>
              <td>{{ p.studente.nome }} {{ p.studente.cognome }}</td>
              <td>{{ p.istituto.nome }}</td>
              <td>{{ p.periodo }}</td>
              <td><span [class]="'badge ' + getBadgeClass(p.stato)">{{ getStatoLabel(p.stato) }}</span></td>
            </tr>
          }
        </tbody>
      </table>
    </div>
  `
})
export class DocenteDashboardComponent implements OnInit {
  pratiche: PraticaMobilita[] = [];

  get laInAttesa() { return this.pratiche.filter(p => p.stato === 'in_attesa_approvazione_la'); }
  get esamiInAttesa() { return this.pratiche.filter(p => p.stato === 'in_riconoscimento_esami'); }

  constructor(private praticaService: PraticaService) {}

  ngOnInit() { this.praticaService.getMiePratiche().subscribe(d => this.pratiche = d); }

  getUltimoLa(p: PraticaMobilita) { return p.learning_agreements.at(-1); }

  getBadgeClass(s: string) {
    const m: Record<string,string> = { 'creata':'badge-created','in_attesa_approvazione_la':'badge-waiting','pre_partenza_completata':'badge-approved','mobilita_in_corso':'badge-progress','in_riconoscimento_esami':'badge-waiting','chiusa':'badge-closed' };
    return m[s] ?? 'badge-created';
  }
  getStatoLabel(s: string) {
    const m: Record<string,string> = { 'creata':'Creata','in_attesa_approvazione_la':'Attesa LA','pre_partenza_completata':'Pre-partenza ok','mobilita_in_corso':'In corso','in_riconoscimento_esami':'In riconoscimento','chiusa':'Chiusa' };
    return m[s] ?? s;
  }
}
