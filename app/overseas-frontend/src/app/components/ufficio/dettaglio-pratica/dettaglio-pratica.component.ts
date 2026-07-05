// components/ufficio/dettaglio-pratica/dettaglio-pratica.component.ts
import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { PraticaService } from '../../../services/pratica.service';
import { PraticaMobilita } from '../../../models/models';

@Component({
  selector: 'app-ufficio-dettaglio-pratica',
  standalone: true,
  imports: [CommonModule, FormsModule],
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

      <!-- modifica stato -->
      <div class="card" style="margin-bottom: 1.5rem; border-left: 4px solid #1a3a6b;">
        <div class="card-title" style="margin-bottom: 10px; font-weight: bold;">Modifica Stato</div>
        <div style="display: flex; gap: 15px; align-items: center;">
          
          <select class="form-control" [(ngModel)]="nuovoStato" style="max-width: 250px; padding: 8px; border: 1px solid #ccc; border-radius: 4px;">
            @for (stato of statiOrder; track stato) {
              <option [value]="stato">{{ getStatoLabel(stato) }}</option>
            }
          </select>
          
          <button class="btn btn-primary" (click)="salvaNuovoStato()">
            ✏️ Aggiorna Stato
          </button>
        </div>
      </div>

      <!-- Esami riconosciuti -->
      @if (pratica.pianoesami.length > 0) {
        <div class="card">
          <div class="card-title">Esami</div>
          <table>
            <thead><tr><th>Esame estero</th><th>Esame Ca' Foscari</th><th>Voto</th><th>Stato</th></tr></thead>
            <tbody>
              @for (esame of pratica.pianoesami; track esame.id) {
                <tr>
                  <td>{{ esame.codice_estero }} — {{ esame.titolo_estero }}</td>
                  <td>{{ esame.codice_cafoscari }} — {{ esame.titolo_cafoscari }}</td>
                  <td>{{ esame.voto_ottenuto ?? '—' }}</td>
                  <td><span [class]="'badge ' + getRiconoscimentoBadge(esame.stato_riconoscimento)">{{ getStatoEsameLabel(esame.stato_riconoscimento ?? 'in_attesa') }}</span></td>
                </tr>
              }
            </tbody>
          </table>
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
  nuovoStato = '';

  steps = [
    { key: 'creato', label: 'Creato' },
    { key: 'in attesa', label: 'LA approvato' },
    { key: 'pre-partenza', label: 'Pre-partenza' },
    { key: 'in corso', label: 'In corso' },
    { key: 'viaggioCompletato', label: 'Riconoscimento' },
    { key: 'completato', label: 'Chiuso' }
  ];

  statiOrder = ['creato', 'in attesa', 'pre-partenza', 'in corso', 'viaggioCompletato', 'completato', 'annullato'];

  constructor(private route: ActivatedRoute, private praticaService: PraticaService, private router: Router, private cdr: ChangeDetectorRef) { }

  ngOnInit() {
    const id = String(this.route.snapshot.paramMap.get('id'));
    this.praticaService.getPraticaUfficioById(id).subscribe(p => {
      this.pratica = p;
      this.nuovoStato = p.stato;
      console.log(this.pratica);
      this.cdr.detectChanges();
    });
  }

  getStepClass(key: string): string {
    if (!this.pratica) return '';

    if ((this.pratica.stato as string) === 'annullato') return '';

    const currentIdx = this.statiOrder.indexOf(this.pratica.stato);
    const stepIdx = this.statiOrder.indexOf(key);

    if (stepIdx === -1 || currentIdx === -1) return '';

    if (stepIdx < currentIdx) return 'done';
    if (stepIdx === currentIdx) return 'active';
    return '';
  }

  ultimoLaApprovato(): boolean {

    if (!this.pratica || !this.pratica.learning_agreements) {
      return false;
    }

    const ultimo = this.pratica?.learning_agreements.at(-1);
    return ultimo?.stato === 'approvato';
  }

  tuttiEsamiApprovati(): boolean {
    if (!this.pratica) return false;
    return this.pratica.pianoesami.every(e => e.stato_riconoscimento === 'approvato');
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
    const m: Record<string, string> = { 'creato': 'badge-created', 'in attesa': 'badge-waiting', 'pre-partenza': 'badge-approved', 'in corso': 'badge-progress', 'viaggioCompletato': 'badge-waiting', 'chiusa': 'badge-closed', 'annullata': 'badge-rejected' };
    return m[s] ?? 'badge-created';
  }
  getStatoLabel(s: string) {
    const m: Record<string, string> = { 'creato': 'Creato', 'in attesa': 'Attesa LA', 'pre-partenza': 'Pre-partenza ok', 'in corso': 'In corso', 'viaggioCompletato': 'In riconoscimento', 'chiusa': 'Chiuso', 'annullata': 'Annullato' };
    return m[s] ?? s;
  }
  getRiconoscimentoBadge(s?: string) {
    if (s === 'approvato') return 'badge-approved';
    if (s === 'rifiutato') return 'badge-rejected';
    return 'badge-waiting';
  }

  getStatoEsameLabel(stato: string): string {
    const map: Record<string, string> = {
      'in_attesa': 'In attesa',
      'approvato': 'Approvato',
      'rifiutato': 'Rifiutato'
    };
    return map[stato] ?? stato;
  }

  salvaNuovoStato() {
    if (!this.pratica || !this.nuovoStato) return;

    this.praticaService.aggiornaStatoPraticaUfficio(this.pratica.ida, this.nuovoStato).subscribe({
      next: (risposta) => {

        this.pratica!.stato = this.nuovoStato as any;

        this.messaggio = 'Stato della pratica aggiornato con successo!';
        setTimeout(() => this.messaggio = '', 3000);
        this.cdr.detectChanges();
      },
      error: (err) => {

        console.error("Errore salvataggio stato", err);

        let msgErrore = "Impossibile aggiornare lo stato (Errore di rete generico)";

        if(err.error && err.error.msg){
          msgErrore = err.error.msg;
        }else{
          if(typeof err.error === "string"){
            msgErrore = err.error;
          }
        }
        alert(msgErrore);
      }
    });
  }
}
