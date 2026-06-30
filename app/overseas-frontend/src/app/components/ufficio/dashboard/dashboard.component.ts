// components/ufficio/dashboard/dashboard.component.ts
import { Component, OnInit } from '@angular/core';
import { RouterLink } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { PraticaService } from '../../../services/pratica.service';
import { PraticaMobilita } from '../../../models/models';

@Component({
  selector: 'app-ufficio-dashboard',
  standalone: true,
  imports: [RouterLink, FormsModule, CommonModule],
  template: `
    <div class="page-header">
      <div>
        <h1 class="page-title">Dashboard Ufficio Overseas</h1>
        <p class="page-sub">Panoramica di tutte le pratiche di mobilità</p>
      </div>
    </div>

    <div class="cards-grid">
      <div class="metric-card"><div class="metric-label">Totale pratiche</div><div class="metric-value blue">{{ pratiche.length }}</div></div>
      <div class="metric-card"><div class="metric-label">Da verificare</div><div class="metric-value amber">{{ contaStato('in_attesa_approvazione_la') }}</div></div>
      <div class="metric-card"><div class="metric-label">In corso</div><div class="metric-value blue">{{ contaStato('mobilita_in_corso') }}</div></div>
      <div class="metric-card"><div class="metric-label">Chiuse</div><div class="metric-value green">{{ contaStato('chiusa') }}</div></div>
    </div>

    <div class="card">
      <div class="card-title">
        Tutte le pratiche
        <div style="display:flex;gap:8px">
          <select class="form-control" style="width:auto;font-size:12px" [(ngModel)]="filtroStato">
            <option value="">Tutti gli stati</option>
            <option value="creata">Creata</option>
            <option value="in_attesa_approvazione_la">Attesa LA</option>
            <option value="pre_partenza_completata">Pre-partenza completata</option>
            <option value="mobilita_in_corso">In corso</option>
            <option value="in_riconoscimento_esami">Riconoscimento</option>
            <option value="chiusa">Chiusa</option>
          </select>
          <select class="form-control" style="width:auto;font-size:12px" [(ngModel)]="filtroPaese">
            <option value="">Tutti i paesi</option>
            @for (paese of paesiDisponibili(); track paese) {
              <option [value]="paese">{{ paese }}</option>
            }
          </select>
        </div>
      </div>

      <div class="table-wrap">
        <table>
          <thead><tr><th>Studente</th><th>Istituto</th><th>Paese</th><th>Periodo</th><th>Docente ref.</th><th>Stato</th><th>Azioni</th></tr></thead>
          <tbody>
            @for (p of praticheFiltrate(); track p.id) {
              <tr>
                <td>{{ p.studente.nome }} {{ p.studente.cognome }}</td>
                <td>{{ p.istituto.nome }}</td>
                <td>{{ p.istituto.paese }}</td>
                <td>{{ p.periodo }}</td>
                <td>{{ p.docente.nome }} {{ p.docente.cognome }}</td>
                <td><span [class]="'badge ' + getBadgeClass(p.stato)">{{ getStatoLabel(p.stato) }}</span></td>
                <td><a [routerLink]="['/ufficio/pratica', p.id]" class="btn btn-sm">👁 Dettaglio</a></td>
              </tr>
            }
          </tbody>
        </table>
      </div>
    </div>
  `
})
export class UfficioDashboardComponent implements OnInit {
  pratiche: PraticaMobilita[] = [];
  filtroStato = '';
  filtroPaese = '';

  constructor(private praticaService: PraticaService) {}

  ngOnInit() { this.praticaService.getTutteLePratiche().subscribe(d => this.pratiche = d); }

  contaStato(stato: string): number { return this.pratiche.filter(p => p.stato === stato).length; }

  paesiDisponibili(): string[] {
    return [...new Set(this.pratiche.map(p => p.istituto.paese))];
  }

  praticheFiltrate(): PraticaMobilita[] {
    return this.pratiche.filter(p =>
      (!this.filtroStato || p.stato === this.filtroStato) &&
      (!this.filtroPaese || p.istituto.paese === this.filtroPaese)
    );
  }

  getBadgeClass(s: string) {
    const m: Record<string,string> = { 'creata':'badge-created','in_attesa_approvazione_la':'badge-waiting','pre_partenza_completata':'badge-approved','mobilita_in_corso':'badge-progress','in_riconoscimento_esami':'badge-waiting','chiusa':'badge-closed' };
    return m[s] ?? 'badge-created';
  }
  getStatoLabel(s: string) {
    const m: Record<string,string> = { 'creata':'Creata','in_attesa_approvazione_la':'Attesa LA','pre_partenza_completata':'Pre-partenza ok','mobilita_in_corso':'In corso','in_riconoscimento_esami':'In riconoscimento','chiusa':'Chiusa' };
    return m[s] ?? s;
  }
}
