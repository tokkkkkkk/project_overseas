// components/studente/nuova-pratica/nuova-pratica.component.ts
import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { CommonModule } from '@angular/common';
import { PraticaService } from '../../../services/pratica.service';
import { IstitutoOspitante, MappingEsame, Utente } from '../../../models/models';



@Component({
  selector: 'app-nuova-pratica',
  standalone: true,
  imports: [FormsModule, CommonModule, RouterLink],
  template: `
    <div class="page-header">
      <div>
        <h1 class="page-title">Nuova pratica di mobilità</h1>
        <p class="page-sub">Compila i dati per creare una nuova pratica Overseas</p>
      </div>
    </div>

    <!-- Dati principali -->
    <div class="card">
      <div class="card-title">Dati principali</div>
      <div class="form-row">
        <div class="form-group">
          <label class="form-label">Anno accademico</label>
          <select class="form-control" [(ngModel)]="form.anno_accademico">
            <option value="2025/2026">2025/2026</option>
            <option value="2026/2027">2026/2027</option>
          </select>
        </div>
        <div class="form-group">
          <label class="form-label">Periodo</label>
          <select class="form-control" [(ngModel)]="form.periodo">
            <option value="Primo semestre">Primo semestre</option>
            <option value="Secondo semestre">Secondo semestre</option>
            <option value="Anno intero">Anno intero</option>
          </select>
        </div>
      </div>
      <div class="form-row">
        <div class="form-group">
          <label class="form-label">Istituto ospitante</label>
          @if (loading_3) {
            <p>Caricamento...</p>
          }@else {
            <select class="form-control" [(ngModel)]="form.istituto_id">
            <option value="" disabled>Seleziona istituto...</option>
              @for (ist of istituti; track ist.idin) {
                <option [value]="ist.idin">{{ ist.nome }} — {{ ist.paese }}</option>
              }
            </select>
          }
        </div>
        <div class="form-group">
          <label class="form-label">Docente referente</label>
          @if (loading_2) {
            <p>Caricamento...</p>
          }@else {
            <select class="form-control" [(ngModel)]="form.docente_id">
            <option value="" disabled>Seleziona docente...</option>
              @for (doc of docenti; track doc.username) {
                <option [value]="doc.username">{{ doc.nome }} {{ doc.cognome }}</option>
              }
            </select>
          }
        </div>
      </div>
      <div class="form-group">
        <label class="form-label">Note aggiuntive</label>
        <textarea class="form-control" [(ngModel)]="form.note" rows="2" placeholder="Eventuali note..."></textarea>
      </div>
    </div>

    <!-- Mapping esami -->
    <div class="card">
      <div class="card-title">
        Mapping esami
        <button class="btn btn-sm" (click)="aggiungiEsame()">+ Aggiungi esame</button>
      </div>

      <div class="mapping-header">
        <span>Esame estero (OC)</span>
        <span></span>
        <span>Esame Ca' Foscari (EC)</span>
      </div>

      @for (esame of form.mapping_esami; track $index; let i = $index) {
        <div class="mapping-row">
          <div class="mapping-cell">
            <input [(ngModel)]="esame.codice_estero" placeholder="Codice" class="mini-input" />
            <input [(ngModel)]="esame.titolo_estero" placeholder="Titolo corso" class="mini-input" />
            <input [(ngModel)]="esame.crediti_estero" placeholder="CFU" type="number" class="mini-input mini-cfu" />
          </div>
          <div class="mapping-arrow">⇄</div>
          <div class="mapping-cell">
            <input [(ngModel)]="esame.codice_cafoscari" placeholder="Codice" class="mini-input" />
            <input [(ngModel)]="esame.titolo_cafoscari" placeholder="Titolo corso" class="mini-input" />
            <input [(ngModel)]="esame.crediti_cafoscari" placeholder="CFU" type="number" class="mini-input mini-cfu" />
          </div>
          <button class="btn-remove" (click)="rimuoviEsame(i)" title="Rimuovi">✕</button>
        </div>
      }

      <!-- Upload Learning Agreement -->
      <div class="divider"></div>
      <div class="form-group">
        <label class="form-label">Learning Agreement (PDF)</label>
        <div class="upload-box" (click)="fileInput.click()">
          @if (fileSelezionato) {
            <span>📄 {{ fileSelezionato.name }}</span>
          } @else {
            <span>📤 Clicca per selezionare il Learning Agreement (PDF)</span>
          }
        </div>
        <input #fileInput type="file" accept=".pdf" style="display:none" (change)="onFileSelected($event)" />
      </div>

      @if (errore) {
        <div class="alert-error">{{ errore }}</div>
      }

      <div class="form-actions">
        <a routerLink="/studente/dashboard" class="btn">Annulla</a>
        <button class="btn btn-primary" (click)="creaPratica()" [disabled]="loading">
          {{ loading ? 'Salvataggio...' : '✓ Crea pratica' }}
        </button>
      </div>
    </div>
  `,
  styles: [`
    .mapping-header { display: grid; grid-template-columns: 1fr 40px 1fr; gap: 8px; font-size: 11px; color: #9aa0b0; padding: 0 2px; margin-bottom: 6px; }
    .mapping-row { display: grid; grid-template-columns: 1fr 40px 1fr auto; gap: 8px; align-items: start; margin-bottom: 8px; }
    .mapping-cell { background: #f5f7fa; border-radius: 8px; padding: 8px; display: flex; gap: 6px; flex-wrap: wrap; }
    .mapping-arrow { color: #9aa0b0; font-size: 18px; text-align: center; padding-top: 12px; }
    .mini-input { border: 1px solid #e0e6ed; border-radius: 6px; padding: 5px 8px; font-size: 12px; flex: 1; min-width: 80px; }
    .mini-cfu { max-width: 60px; }
    .btn-remove { background: #fef0f0; border: 1px solid #f5c0c0; color: #a32d2d; border-radius: 6px; padding: 4px 8px; cursor: pointer; font-size: 12px; align-self: center; }
    .divider { height: 1px; background: #e8ecf0; margin: 1.5rem 0; }
    .upload-box { border: 2px dashed #c8d5e8; border-radius: 8px; padding: 1.5rem; text-align: center; color: #7a8090; font-size: 13px; cursor: pointer; }
    .upload-box:hover { background: #f5f7fa; }
    .form-actions { display: flex; gap: 8px; justify-content: flex-end; margin-top: 1rem; }
    .alert-error { background: #fef0f0; border: 1px solid #f5c0c0; color: #a32d2d; padding: 10px 14px; border-radius: 8px; font-size: 13px; margin-bottom: 1rem; }
  `]
})
export class NuovaPraticaComponent implements OnInit {
  istituti: IstitutoOspitante[] = [];
  docenti: Utente[] = [];
  fileSelezionato: File | null = null;
  errore = '';
  loading = false;
  loading_2 = false;
  loading_3 = false;


  form = {
    anno_accademico: '2025/2026',
    periodo: 'Primo semestre',
    istituto_id: '',
    docente_id: 0,
    note: '',
    mapping_esami: [this.nuovoEsame()]
  };

  constructor(private praticaService: PraticaService, private router: Router, private cdr: ChangeDetectorRef) { }

  ngOnInit() {
    console.log('ngOnInit fired');
    this.praticaService.getIstituti().subscribe({
      next: data => {
        console.log('data received', data);
        this.istituti = data;
        this.loading_3 = false;
      },
      error: err => {
        console.error('request failed', err);
        this.loading_3 = false;
      }
    });
    this.praticaService.getDocenti().subscribe({
      next: data => {
        console.log('data received', data);
        this.docenti = data;
        this.loading_2 = false;
        this.cdr.markForCheck();
      },
      error: err => {
        console.error('request failed', err);
        this.loading_2 = false;
      }
    });
  }

  nuovoEsame(): MappingEsame {
    return { codice_estero: '', titolo_estero: '', crediti_estero: 0, codice_cafoscari: '', titolo_cafoscari: '', crediti_cafoscari: 0 };
  }

  aggiungiEsame() { this.form.mapping_esami.push(this.nuovoEsame()); }

  rimuoviEsame(i: number) {
    if (this.form.mapping_esami.length > 1) this.form.mapping_esami.splice(i, 1);
  }

  onFileSelected(event: Event) {
    const input = event.target as HTMLInputElement;
    if (input.files?.[0]) this.fileSelezionato = input.files[0];
  }

  creaPratica() {
    if (!this.form.istituto_id || !this.form.docente_id) {
      this.errore = 'Seleziona istituto e docente referente';
      return;
    }
    this.loading = true;
    this.praticaService.creaPratica(this.form).subscribe({
      next: (pratica) => {
        if (this.fileSelezionato) {
          this.praticaService.caricaLearningAgreement(pratica.ida, this.fileSelezionato).subscribe({
            next: () => this.router.navigate(['/studente/dashboard']),
            error: () => this.router.navigate(['/studente/dashboard'])
          });
        } else {
          this.router.navigate(['/studente/dashboard']);
        }
      },
      error: () => { this.errore = 'Errore durante la creazione della pratica'; this.loading = false; }
    });
  }
}
