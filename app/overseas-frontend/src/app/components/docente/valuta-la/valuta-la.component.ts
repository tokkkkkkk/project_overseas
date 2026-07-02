// components/docente/valuta-la/valuta-la.component.ts
import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { PraticaService } from '../../../services/pratica.service';
import { PraticaMobilita } from '../../../models/models';

@Component({
  selector: 'app-valuta-la',
  standalone: true,
  imports: [FormsModule, CommonModule],
  template: `
    @if (pratica) {
      <div class="page-header">
        <div>
          <h1 class="page-title">Valutazione Learning Agreement</h1>
          <p class="page-sub">Studente: {{ pratica.studente.nome }} {{ pratica.studente.cognome }} — {{ pratica.istituto.nome }}</p>
        </div>
      </div>

      <!-- Documento -->
      <div class="card">
        <div class="card-title">Documento caricato</div>
        <div class="file-row">
          <span>📄 {{ ultimoLa?.filename }}</span>
          <span class="text-muted">Versione {{ ultimoLa?.versione }} · {{ ultimoLa?.data_caricamento | date:'dd/MM/yyyy' }}</span>
          <a [href]="'/api/files/' + ultimoLa?.filename" class="btn btn-sm" download style="margin-left:auto">⬇ Scarica</a>
        </div>
      </div>

      <!-- Mapping esami -->
      <div class="card">
        <div class="card-title">Mapping esami proposto</div>
        <div class="mapping-header">
          <span>Esame estero (OC)</span><span></span><span>Esame Ca' Foscari (EC)</span>
        </div>
        @for (esame of pratica.mapping_esami; track esame.id) {
          <div class="mapping-row">
            <div class="mapping-cell">{{ esame.codice_estero }} — {{ esame.titolo_estero }} — {{ esame.crediti_estero }} CFU</div>
            <div class="mapping-arrow">⇄</div>
            <div class="mapping-cell">{{ esame.codice_cafoscari }} — {{ esame.titolo_cafoscari }} — {{ esame.crediti_cafoscari }} CFU</div>
          </div>
        }
      </div>

      <!-- Decisione -->
      <div class="card">
        <div class="card-title">Decisione</div>
        <div style="display:flex;gap:8px;margin-bottom:1rem">
          <button class="btn btn-success" (click)="approva()">✓ Approva Learning Agreement</button>
          <button class="btn btn-danger" (click)="mostraRifiuto = !mostraRifiuto">✕ Rifiuta</button>
        </div>
        @if (mostraRifiuto) {
          <div class="form-group">
            <label class="form-label">Motivazione rifiuto</label>
            <textarea class="form-control" [(ngModel)]="motivazione" rows="3" placeholder="Indica il motivo del rifiuto..."></textarea>
          </div>
          <button class="btn btn-danger btn-sm" (click)="rifiuta()">Conferma rifiuto</button>
        }
        @if (messaggio) {
          <div class="alert-success" style="margin-top:1rem">{{ messaggio }}</div>
        }
      </div>
    }
  `,
  styles: [`
    .file-row { display: flex; gap: 12px; align-items: center; font-size: 13px; background: #f5f7fa; border-radius: 8px; padding: 12px; }
    .mapping-header { display: grid; grid-template-columns: 1fr 40px 1fr; gap: 8px; font-size: 11px; color: #9aa0b0; margin-bottom: 6px; }
    .mapping-row { display: grid; grid-template-columns: 1fr 40px 1fr; gap: 8px; margin-bottom: 8px; font-size: 12px; }
    .mapping-cell { background: #f5f7fa; border-radius: 6px; padding: 8px 10px; }
    .mapping-arrow { color: #9aa0b0; text-align: center; font-size: 16px; }
    .btn-success { background: #eaf3de; color: #27500a; border: 1px solid #97c459; border-radius: 8px; padding: 7px 14px; cursor: pointer; font-size: 13px; }
    .btn-danger { background: #fcebeb; color: #791f1f; border: 1px solid #f09595; border-radius: 8px; padding: 7px 14px; cursor: pointer; font-size: 13px; }
    .alert-success { background: #eaf3de; color: #27500a; padding: 10px 14px; border-radius: 8px; font-size: 13px; }
  `]
})
export class ValutaLaComponent implements OnInit {
  pratica: PraticaMobilita | null = null;
  mostraRifiuto = false;
  motivazione = '';
  messaggio = '';

  get ultimoLa() { return this.pratica?.learning_agreements.at(-1); }

  constructor(private route: ActivatedRoute, private praticaService: PraticaService, private router: Router) {}

  ngOnInit() {
    const id = Number(this.route.snapshot.paramMap.get('id'));
    this.praticaService.getPraticaById(id).subscribe(p => this.pratica = p);
  }

  approva() {
    if (!this.ultimoLa) return;
    this.praticaService.valutaLearningAgreement(this.ultimoLa.id, 'approvato').subscribe(() => {
      this.messaggio = 'Learning Agreement approvato!';
      setTimeout(() => this.router.navigate(['/docente/dashboard']), 1500);
    });
  }

  rifiuta() {
    if (!this.ultimoLa || !this.motivazione) return;
    this.praticaService.valutaLearningAgreement(this.ultimoLa.id, 'rifiutato', this.motivazione).subscribe(() => {
      this.messaggio = 'Learning Agreement rifiutato.';
      setTimeout(() => this.router.navigate(['/docente/dashboard']), 1500);
    });
  }
}
