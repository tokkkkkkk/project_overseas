// components/ufficio/dettaglio-pratica/dettaglio-pratica.component.ts
import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { PraticaService } from '../../../services/pratica.service';
import { PraticaMobilita } from '../../../models/models';

@Component({
  selector: 'app-ufficio-dettaglio-pratica',
  standalone: true,
  imports: [CommonModule],
  template: `
    @if (pratica) {
      <div class="page-header">
        <div>
          <h1 class="page-title">Pratica #{{ pratica.ida }} — {{ pratica.istituto.nome }}</h1>
          <p class="page-sub">Studente: {{ pratica.studente.nome }} {{ pratica.studente.cognome }} · Docente: {{ pratica.docente.nome }} {{ pratica.docente.cognome }}</p>
        </div>
        <span [class]="'badge ' + getBadgeClass(pratica.stato)">{{ getStatoLabel(pratica.stato) }}</span>
      </div>

      <!-- Barra di stato -->
      <div class="status-bar">
        @for (step of steps; track step.key) {
          <div [class]="'status-step ' + getStepClass(step.key)">
            <div class="status-dot"></div>
            <span>{{ step.label }}</span>
          </div>
        }
      </div>

      <!-- Verifica pre-partenza -->
      @if (pratica.stato === 'in_attesa_approvazione_la' && ultimoLaApprovato()) {
        <div class="alert-info">
          Il Learning Agreement è stato approvato dal docente. Puoi verificare e completare la fase pre-partenza.
        </div>
        <div class="card">
          <div class="card-title">Verifica pre-partenza</div>
          <button class="btn btn-primary" (click)="completaPrePartenza()">✓ Conferma completamento pre-partenza</button>
        </div>
      }

      <!-- Esami riconosciuti -->
      @if (pratica.mapping_esami.length > 0) {
        <div class="card">
          <div class="card-title">Esami</div>
          <table>
            <thead><tr><th>Esame estero</th><th>Esame Ca' Foscari</th><th>Voto</th><th>Stato</th></tr></thead>
            <tbody>
              @for (esame of pratica.mapping_esami; track esame.id) {
                <tr>
                  <td>{{ esame.codice_estero }} — {{ esame.titolo_estero }}</td>
                  <td>{{ esame.codice_cafoscari }} — {{ esame.titolo_cafoscari }}</td>
                  <td>{{ esame.voto_ottenuto ?? '—' }}</td>
                  <td><span [class]="'badge ' + getRiconoscimentoBadge(esame.stato_riconoscimento)">{{ esame.stato_riconoscimento ?? 'in_attesa' }}</span></td>
                </tr>
              }
            </tbody>
          </table>
        </div>
      }

      <!-- Chiusura pratica -->
      @if (pratica.stato === 'in_riconoscimento_esami' && tuttiEsamiApprovati() && pratica.transcript) {
        <div class="alert-success">
          Transcript of Records caricato e tutti gli esami approvati dal docente. La pratica può essere chiusa.
        </div>
        <div class="card">
          <div class="card-title">Chiusura pratica</div>
          <button class="btn btn-primary" (click)="chiudiPratica()">🔒 Chiudi pratica definitivamente</button>
        </div>
      }

      @if (messaggio) {
        <div class="alert-success" style="margin-top:1rem">{{ messaggio }}</div>
      }
    } @else {
      <p class="text-muted">Caricamento pratica...</p>
    }
  `,
  styles: [`
    .status-bar { display: flex; margin-bottom: 1.5rem; }
    .status-step { flex: 1; text-align: center; font-size: 11px; color: #9aa0b0; }
    .status-step.done { color: #27500a; }
    .status-step.active { color: #1a3a6b; font-weight: 500; }
    .status-dot { width: 10px; height: 10px; border-radius: 50%; background: #d0d8e0; margin: 0 auto 4px; }
    .status-step.done .status-dot { background: #639922; }
    .status-step.active .status-dot { background: #1a3a6b; }
    .alert-info { background: #e6f1fb; color: #0c447c; padding: 10px 14px; border-radius: 8px; font-size: 13px; margin-bottom: 1rem; }
    .alert-success { background: #eaf3de; color: #27500a; padding: 10px 14px; border-radius: 8px; font-size: 13px; margin-bottom: 1rem; }
  `]
})
export class UfficioDettaglioPraticaComponent implements OnInit {
  pratica: PraticaMobilita | null = null;
  messaggio = '';

  steps = [
    { key: 'creata', label: 'Creata' },
    { key: 'in_attesa_approvazione_la', label: 'LA approvato' },
    { key: 'pre_partenza_completata', label: 'Pre-partenza' },
    { key: 'mobilita_in_corso', label: 'In corso' },
    { key: 'in_riconoscimento_esami', label: 'Riconoscimento' },
    { key: 'chiusa', label: 'Chiusa' }
  ];

  statiOrder = ['creata','in_attesa_approvazione_la','pre_partenza_completata','mobilita_in_corso','in_riconoscimento_esami','chiusa'];

  constructor(private route: ActivatedRoute, private praticaService: PraticaService, private router: Router) {}

  ngOnInit() {
    const id = Number(this.route.snapshot.paramMap.get('id'));
    this.praticaService.getPraticaById(id).subscribe(p => this.pratica = p);
  }

  getStepClass(key: string): string {
    if (!this.pratica) return '';
    const currentIdx = this.statiOrder.indexOf(this.pratica.stato);
    const stepIdx = this.statiOrder.indexOf(key);
    if (stepIdx < currentIdx) return 'done';
    if (stepIdx === currentIdx) return 'active';
    return '';
  }

  ultimoLaApprovato(): boolean {
    const ultimo = this.pratica?.learning_agreements.at(-1);
    return ultimo?.stato === 'approvato';
  }

  tuttiEsamiApprovati(): boolean {
    if (!this.pratica) return false;
    return this.pratica.mapping_esami.every(e => e.stato_riconoscimento === 'approvato');
  }

  completaPrePartenza() {
    if (!this.pratica) return;
    this.praticaService.completaPrePartenza(this.pratica.ida).subscribe(() => {
      this.messaggio = 'Fase pre-partenza completata!';
      setTimeout(() => this.router.navigate(['/ufficio/dashboard']), 1500);
    });
  }

  chiudiPratica() {
    if (!this.pratica) return;
    this.praticaService.chiudiPratica(this.pratica.ida).subscribe(() => {
      this.messaggio = 'Pratica chiusa con successo!';
      setTimeout(() => this.router.navigate(['/ufficio/dashboard']), 1500);
    });
  }

  getBadgeClass(s: string) {
    const m: Record<string,string> = { 'creata':'badge-created','in_attesa_approvazione_la':'badge-waiting','pre_partenza_completata':'badge-approved','mobilita_in_corso':'badge-progress','in_riconoscimento_esami':'badge-waiting','chiusa':'badge-closed' };
    return m[s] ?? 'badge-created';
  }
  getStatoLabel(s: string) {
    const m: Record<string,string> = { 'creata':'Creata','in_attesa_approvazione_la':'Attesa LA','pre_partenza_completata':'Pre-partenza ok','mobilita_in_corso':'In corso','in_riconoscimento_esami':'In riconoscimento','chiusa':'Chiusa' };
    return m[s] ?? s;
  }
  getRiconoscimentoBadge(s?: string) {
    if (s === 'approvato') return 'badge-approved';
    if (s === 'rifiutato') return 'badge-rejected';
    return 'badge-waiting';
  }
}
