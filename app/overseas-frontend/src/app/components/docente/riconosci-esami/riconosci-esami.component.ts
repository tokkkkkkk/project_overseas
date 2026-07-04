// components/docente/riconosci-esami/riconosci-esami.component.ts
import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { PraticaService } from '../../../services/pratica.service';
import { PraticaMobilita, MappingEsame } from '../../../models/models';

@Component({
  selector: 'app-riconosci-esami',
  standalone: true,
  imports: [CommonModule],
  template: `
    @if (pratica) {
      <div class="page-header">
        <div>
          <h1 class="page-title">Riconoscimento esami</h1>
          <p class="page-sub">Studente: {{ pratica.studente.nome }} {{ pratica.studente.cognome }} — {{ pratica.istituto.nome }}</p>
        </div>
      </div>

      @if (pratica.transcript) {
        <div class="card">
          <div class="card-title">Transcript of Records caricato</div>
          <div class="file-row">
            <span>📄 {{ pratica.transcript.filename }}</span>
            <span class="text-muted">{{ pratica.transcript.data_caricamento | date:'dd/MM/yyyy' }}</span>
            <a [href]="'/api/files/' + pratica.transcript.filename" class="btn btn-sm" download style="margin-left:auto">⬇ Scarica</a>
          </div>
        </div>
      }

      <div class="card">
        <div class="card-title">Esami da approvare</div>
        <table>
          <thead><tr><th>Esame estero</th><th>Equivalente Ca' Foscari</th><th>Voto</th><th>Data</th><th>Decisione</th></tr></thead>
          <tbody>
            @for (esame of pratica.pianoesami; track esame.id) {
              <tr>
                <td>{{ esame.titolo_estero }} ({{ esame.codice_estero }})</td>
                <td>{{ esame.titolo_cafoscari }}</td>
                <td>{{ esame.voto_ottenuto ?? '—' }}</td>
                <td>{{ esame.data_superamento ?? '—' }}</td>
                <td style="display:flex;gap:4px">
                  <button class="btn-icon-success" [class.selected]="esame.stato_riconoscimento === 'approvato'" (click)="decidi(esame, 'approvato')">✓</button>
                  <button class="btn-icon-danger" [class.selected]="esame.stato_riconoscimento === 'rifiutato'" (click)="decidi(esame, 'rifiutato')">✕</button>
                </td>
              </tr>
            }
          </tbody>
        </table>
        <div style="margin-top:1rem">
          <button class="btn btn-primary" (click)="confermaRiconoscimento()">✓ Conferma riconoscimento</button>
        </div>
        @if (messaggio) {
          <div class="alert-success" style="margin-top:1rem">{{ messaggio }}</div>
        }
      </div>
    }
  `,
  styles: [`
    .file-row { display: flex; gap: 12px; align-items: center; font-size: 13px; background: #f5f7fa; border-radius: 8px; padding: 12px; }
    .btn-icon-success, .btn-icon-danger { border-radius: 6px; padding: 4px 10px; cursor: pointer; font-size: 13px; border: 1px solid; }
    .btn-icon-success { background: #fff; color: #639922; border-color: #97c459; }
    .btn-icon-success.selected { background: #eaf3de; }
    .btn-icon-danger { background: #fff; color: #a32d2d; border-color: #f09595; }
    .btn-icon-danger.selected { background: #fcebeb; }
    .alert-success { background: #eaf3de; color: #27500a; padding: 10px 14px; border-radius: 8px; font-size: 13px; }
  `]
})
export class RiconosciEsamiComponent implements OnInit {
  pratica: PraticaMobilita | null = null;
  messaggio = '';

  constructor(private route: ActivatedRoute, private praticaService: PraticaService, private router: Router, private cdr: ChangeDetectorRef) { }

  ngOnInit() {
    const id = String(this.route.snapshot.paramMap.get('id'));
    this.praticaService.getPraticaDocenteById(id).subscribe(p => {
      this.pratica = p;
      console.log(this.pratica);
      this.cdr.detectChanges();
    });
  }

  decidi(esame: MappingEsame, decisione: 'approvato' | 'rifiutato') {
    esame.stato_riconoscimento = decisione;
  }

  confermaRiconoscimento() {
    if (!this.pratica) return;
    const richieste = this.pratica.pianoesami
      .filter(e => e.id && e.stato_riconoscimento)
      .map(e => this.praticaService.riconosciEsame(e.id!, e.stato_riconoscimento as 'approvato' | 'rifiutato'));

    if (richieste.length === 0) return;

    // Esegue tutte le chiamate e poi torna alla dashboard
    let completate = 0;
    richieste.forEach(req => req.subscribe(() => {
      completate++;
      if (completate === richieste.length) {
        this.messaggio = 'Esami riconosciuti con successo!';
        setTimeout(() => this.router.navigate(['/docente/dashboard']), 1500);
      }
    }));
  }
}
