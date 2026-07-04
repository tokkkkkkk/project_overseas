// components/studente/dashboard/dashboard.component.ts
import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { RouterLink, Router } from '@angular/router';
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
        <div class="metric-value blue">{{ contaStato('in corso') }}</div>
      </div>
      <div class="metric-card">
        <div class="metric-label">In approvazione LA</div>
        <div class="metric-value amber">{{ contaStato('in attesa') }}</div>
      </div>
      <div class="metric-card">
        <div class="metric-label">Chiuse</div>
        <div class="metric-value green">{{ contaStato('completato') }}</div>
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
                <th>Anno Acc.</th><th>Istituto</th><th>Paese</th><th>Periodo</th><th>Docente</th><th>Stato</th><th>Azioni</th>
              </tr>
            </thead>
            <tbody>
              @for (pratica of pratiche; track pratica.ida) {
                <tr>
                  <td>{{ pratica.anno_accademico }}</td>
                  <td>{{ pratica.istituto.nome }}</td>
                  <td>{{ pratica.istituto.paese }}</td>
                  <td>{{ pratica.periodo }}</td>
                  <td>{{ pratica.docente.nome + ' ' + pratica.docente.cognome }}</td>
                  <td><span [class]="'badge ' + getBadgeClass(pratica.stato)">{{ getStatoLabel(pratica.stato) }}</span></td>
                  <td>
                    <a [routerLink]="['/studente/pratica', pratica.ida]" class="btn btn-sm">Dettaglio</a>
                    @if (pratica.stato === 'creato' ){
                      <button (click)="cancellaPratica(pratica.ida)" class="btn btn-sm" type="button">🗑️</button>
                    }
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

  constructor(private praticaService: PraticaService, private cdr: ChangeDetectorRef, private router: Router) { }

  ngOnInit() {
    this.praticaService.getMiePratiche().subscribe({
      next: (data: PraticaMobilita[]) => {
        console.log('got data', data);
        this.pratiche = data;
        this.loading = false;
        this.cdr.detectChanges(); // force it
      },
      error: () => { this.loading = false; }
    });
  }

  contaStato(stato: string): number {
    return this.pratiche.filter(p => p.stato === stato).length;
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

  cancellaPratica(idDaCancellare: string) {
    const confermato = confirm('Sei sicuro di voler eliminare definitivamente questa pratica?');

    if (confermato) {

      this.praticaService.eliminaPratica(idDaCancellare).subscribe({
        next: () => {


          // Filtriamo l'array
          this.pratiche = this.pratiche.filter(p => p.ida !== idDaCancellare);


          this.cdr.detectChanges();
        },
        error: (err) => {
          console.error('ERRORE DAL BACKEND:', err);
          alert('Il backend ha rifiutato l\'eliminazione. Guarda la console.');
        }
      });
    }
  }
}
