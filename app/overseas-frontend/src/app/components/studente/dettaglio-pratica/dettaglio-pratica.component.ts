// components/studente/dettaglio-pratica/dettaglio-pratica.component.ts
import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { PraticaService } from '../../../services/pratica.service';
import { PraticaMobilita } from '../../../models/models';

@Component({
  selector: 'app-dettaglio-pratica',
  standalone: true,
  imports: [FormsModule, CommonModule],
  template: `
    @if (pratica) {
      <div class="page-header">
        <div>
          <h1 class="page-title">Pratica #{{ pratica.ida }} — {{ pratica.istituto.nome }}</h1>
          <p class="page-sub">{{ pratica.anno_accademico }} · {{ pratica.periodo }} · Docente: {{ pratica.docente.nome }} {{ pratica.docente.cognome }}</p>
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

      <!-- Tab -->
      <div class="tabs">
        @for (tab of tabs; track tab.key) {
          <div class="tab" [class.active]="tabAttiva === tab.key" (click)="tabAttiva = tab.key">{{ tab.label }}</div>
        }
      </div>

      <!-- Tab: Informazioni -->
      @if (tabAttiva === 'info') {
        @if (pratica.stato === 'in corso') {
          <div class="card">
            <div class="card-title">Date mobilità</div>
            @if (pratica.data_arrivo && pratica.data_partenza) {
              <div class="form-row" style="display: flex; gap: 2rem; margin-bottom: 0.5rem;">
                <div>
                  <span class="text-muted" style="font-size: 13px; display: block;">Data arrivo effettiva</span>
                  <strong style="font-size: 15px;">{{ pratica.data_arrivo | date:'dd/MM/yyyy' }}</strong>
                </div>
                <div>
                  <span class="text-muted" style="font-size: 13px; display: block;">Data partenza effettiva</span>
                  <strong style="font-size: 15px;">{{ pratica.data_partenza | date:'dd/MM/yyyy' }}</strong>
                </div>
              </div>
            } 
            @else {
              <div class="form-row">
                <div class="form-group">
                  <label class="form-label">Data arrivo effettiva</label>
                  <input type="date" class="form-control" [(ngModel)]="dataArrivo" />
                </div>
                <div class="form-group">
                  <label class="form-label">Data partenza effettiva</label>
                  <input type="date" class="form-control" [(ngModel)]="dataPartenza" />
                </div>
              </div>
              <button class="btn btn-primary btn-sm" (click)="salvaDates()">✓ Salva date</button>
            }
          </div>
        }

        @if (pratica.stato === 'in corso' || pratica.stato === 'pre-partenza') {
          <div class="card">
            <div class="card-title">Transcript of Records</div>
            @if (pratica.transcript) {
              <div class="file-row">
                <span>📄 {{ pratica.transcript.filename }}</span>
                <span class="text-muted">{{ pratica.transcript.data_caricamento | date:'dd/MM/yyyy' }}</span>
              </div>
            } @else {
              <p class="alert-info">Carica il Transcript of Records dopo il rientro per procedere con il riconoscimento esami.</p>
              <div class="upload-box" (click)="transcriptInput.click()">
                @if (transcriptFile) {
                  <span>📄 {{ transcriptFile.name }}</span>
                } @else {
                  <span>📤 Clicca per selezionare il Transcript of Records (PDF)</span>
                }
              </div>
              <input #transcriptInput type="file" accept=".pdf" style="display:none" (change)="onTranscriptSelected($event)" />
              @if (transcriptFile) {
                <button class="btn btn-primary btn-sm" style="margin-top:8px" (click)="caricaTranscript()">Carica Transcript</button>
              }
            }
          </div>
        }
      }

      <!-- Tab: Esami -->
      @if (tabAttiva === 'esami') {
        <div class="card">
          <div class="card-title">Mapping esami</div>
          <table>
            <thead>
              <tr><th>Codice OC</th><th>Titolo estero</th><th>CFU</th><th>Codice EC</th><th>Titolo Ca' Foscari</th><th>CFU</th><th>Voto</th><th>Stato</th></tr>
            </thead>
            <tbody>
              @for (esame of pratica.pianoesami; track esame.id) {
                <tr>
                  <td>{{ esame.codice_estero }}</td>
                  <td>{{ esame.titolo_estero }}</td>
                  <td>{{ esame.crediti_estero }}</td>
                  <td>{{ esame.codice_cafoscari }}</td>
                  <td>{{ esame.titolo_cafoscari }}</td>
                  <td>{{ esame.crediti_cafoscari }}</td>
                  <td>
                    @if (pratica.stato === 'viaggioCompletato') {
                      <input [(ngModel)]="esame.voto_ottenuto" class="mini-input" placeholder="es. 28/30" style="width:80px" />
                    } @else {
                      {{ esame.voto_ottenuto ?? '—' }}
                    }
                  </td>
                  <td><span [class]="'badge ' + getRiconoscimentoBadge(esame.stato_riconoscimento)">{{ esame.stato_riconoscimento ?? 'in_attesa' }}</span></td>
                </tr>
              }
            </tbody>
          </table>
          @if (pratica.stato === 'viaggioCompletato') {
            <button class="btn btn-primary btn-sm" style="margin-top:1rem" (click)="salvaVoti()">✓ Salva voti</button>
          }
        </div>
      }

      <!-- Tab: Documenti -->
      @if (tabAttiva === 'documenti') {
        <div class="card">
          <div class="card-title">Storico Learning Agreement</div>
          <table>
            <thead><tr><th>Versione</th><th>Data caricamento</th><th>Stato</th><th></th></tr></thead>
            <tbody>
              @for (la of pratica.learning_agreements; track la.id) {
                <tr>
                  <td>v{{ la.versione }}</td>
                  <td>{{ la.data_caricamento | date:'dd/MM/yyyy' }}</td>
                  <td><span [class]="'badge ' + getLaBadge(la.stato)">{{ la.stato }}</span></td>
                  <td><a [href]="'/api/files/' + la.filename" class="btn btn-sm" download>⬇ Scarica</a></td>
                </tr>
              }
            </tbody>
          </table>

          @if (pratica.stato === 'in corso') {
            <div style="margin-top:1rem">
              <div class="card-title" style="font-size:14px">Carica nuovo Learning Agreement</div>
              <div class="upload-box" (click)="laInput.click()">
                @if (nuovoLaFile) { <span>📄 {{ nuovoLaFile.name }}</span> }
                @else { <span>📤 Clicca per selezionare il nuovo LA (PDF)</span> }
              </div>
              <input #laInput type="file" accept=".pdf" style="display:none" (change)="onNuovoLaSelected($event)" />
              @if (nuovoLaFile) {
                <button class="btn btn-primary btn-sm" style="margin-top:8px" (click)="caricaNuovoLa()">Carica nuovo LA</button>
              }
            </div>
          }
        </div>
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
    .tabs { display: flex; border-bottom: 1px solid #e8ecf0; margin-bottom: 1.5rem; }
    .tab { padding: 8px 16px; font-size: 13px; cursor: pointer; color: #7a8090; border-bottom: 2px solid transparent; margin-bottom: -1px; }
    .tab.active { color: #1a3a6b; border-bottom-color: #1a3a6b; font-weight: 500; }
    .upload-box { border: 2px dashed #c8d5e8; border-radius: 8px; padding: 1.5rem; text-align: center; color: #7a8090; font-size: 13px; cursor: pointer; }
    .file-row { display: flex; gap: 12px; align-items: center; font-size: 13px; }
    .alert-info { background: #e8eef8; color: #1a3a6b; padding: 10px 14px; border-radius: 8px; font-size: 13px; margin-bottom: 1rem; }
    .mini-input { border: 1px solid #e0e6ed; border-radius: 6px; padding: 4px 8px; font-size: 12px; }
  `]
})
export class DettaglioPraticaComponent implements OnInit {
  pratica: PraticaMobilita | null = null;
  tabAttiva = 'info';
  dataArrivo = '';
  dataPartenza = '';
  transcriptFile: File | null = null;
  nuovoLaFile: File | null = null;

  tabs = [
    { key: 'info', label: 'Informazioni' },
    { key: 'esami', label: 'Esami' },
    { key: 'documenti', label: 'Documenti' }
  ];

  steps = [
    { key: 'creato', label: 'Creata' },
    { key: 'in attesa', label: 'LA approvato' },
    { key: 'pre-partenza', label: 'Pre-partenza' },
    { key: 'in corso', label: 'In corso' },
    { key: 'in riconoscimento', label: 'Riconoscimento' },
    { key: 'completato', label: 'Chiusa' }
  ];

  statiOrder = ['creato', 'in attesa', 'pre-partenza', 'in corso', 'in riconoscimento', 'completato'];
  constructor(private route: ActivatedRoute, private praticaService: PraticaService, private cdr: ChangeDetectorRef) { }

  ngOnInit() {
    const id = String(this.route.snapshot.paramMap.get('id'));
    this.praticaService.getPraticaById(id).subscribe(p => {
      this.pratica = p;
      this.dataArrivo = p.data_arrivo ?? '';
      this.dataPartenza = p.data_partenza ?? '';
      this.cdr.detectChanges(); // force it

    });
  }

  getStepClass(key: string): string {
    if (!this.pratica) return '';
    const currentIdx = this.statiOrder.indexOf(this.pratica.stato);
    const stepIdx = this.statiOrder.indexOf(key);
    if (stepIdx < currentIdx) return 'done';
    if (stepIdx === currentIdx) return 'active';
    return '';
  }

  salvaDates() {
    if (!this.pratica) return;
    this.praticaService.aggiornaPratica(this.pratica.ida, { data_arrivo: this.dataArrivo, data_partenza: this.dataPartenza }).subscribe();
  }

  onTranscriptSelected(e: Event) {
    const input = e.target as HTMLInputElement;
    if (input.files?.[0]) this.transcriptFile = input.files[0];
  }

  caricaTranscript() {
    if (!this.pratica || !this.transcriptFile) return;
    this.praticaService.caricaTranscript(this.pratica.ida, this.transcriptFile).subscribe(() => window.location.reload());
  }

  onNuovoLaSelected(e: Event) {
    const input = e.target as HTMLInputElement;
    if (input.files?.[0]) this.nuovoLaFile = input.files[0];
  }

  caricaNuovoLa() {
    if (!this.pratica || !this.nuovoLaFile) return;
    this.praticaService.caricaLearningAgreement(this.pratica.ida, this.nuovoLaFile).subscribe(() => window.location.reload());
  }

  salvaVoti() {
    if (!this.pratica) return;
    this.praticaService.aggiornaVotiEsami(this.pratica.ida, this.pratica.pianoesami).subscribe();
  }

  getBadgeClass(stato: string): string {
    const map: Record<string, string> = {
      'creato': 'badge-created',
      'in attesa': 'badge-waiting',
      'pre-partenza': 'badge-approved',
      'in corso': 'badge-progress',
      'viaggioCompletato': 'badge-waiting', // Assuming this is when exams are being recognized
      'completato': 'badge-closed',
      'annullato': 'badge-danger' // Add a red badge for cancelled!
    };
    return map[stato] ?? 'badge-created';
  }

  getStatoLabel(stato: string): string {
    const map: Record<string, string> = {
      'creato': 'Creata',
      'in attesa': 'Attesa approvazione LA',
      'pre-partenza': 'Pre-partenza completata',
      'in corso': 'Mobilità in corso',
      'viaggioCompletato': 'In riconoscimento esami', 
      'completato': 'Chiusa',
      'annullato': 'Annullata'
    };
    return map[stato] ?? stato;
  }

  getLaBadge(stato?: string): string {
    if (stato === 'approvato') return 'badge-approved';
    if (stato === 'rifiutato') return 'badge-rejected';
    return 'badge-waiting';
  }

  getRiconoscimentoBadge(stato?: string): string {
    if (stato === 'approvato') return 'badge-approved';
    if (stato === 'rifiutato') return 'badge-rejected';
    return 'badge-waiting';
  }
}
