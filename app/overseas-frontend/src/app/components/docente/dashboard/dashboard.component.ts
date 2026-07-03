// components/docente/dashboard/dashboard.component.ts
import { Component, OnInit,ChangeDetectorRef } from '@angular/core';
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

    @if (laInAttesa.length > 0) {
      <div class="card">
        <div class="card-title">Learning Agreement da valutare</div>
        <table>
          <thead><tr><th>Studente</th><th>Istituto</th><th>Periodo</th><th>LA caricato il</th><th>Azioni</th></tr></thead>
          <tbody>
            @for (p of laInAttesa; track p.ida) {
              <tr>
                <td>{{ p.studente?.nome }} {{ p.studente?.cognome }}</td>
                <td>{{ p.istituto?.nome }}</td>
                <td>{{ p.periodo }}</td>
                <td>{{ getUltimoLa(p)?.data_caricamento | date:'dd/MM/yyyy' }}</td>
                <td style="display:flex;gap:6px">
                  <a *ngIf="getUltimoLa(p)?.filename" [href]="'/api/files/' + getUltimoLa(p)?.filename" class="btn btn-sm" download>📄 Vedi LA</a>
                  <a [routerLink]="['/docente/valuta-la', p.ida]" class="btn btn-sm btn-success">✓ Valuta</a>
                </td>
              </tr>
            }
          </tbody>
        </table>
      </div>
    }

    @if (esamiInAttesa.length > 0) {
      <div class="card">
        <div class="card-title">Esami da riconoscere</div>
        <table>
          <thead><tr><th>Studente</th><th>Istituto</th><th>N° esami</th><th>Azioni</th></tr></thead>
          <tbody>
            @for (p of esamiInAttesa; track p.ida) {
              <tr>
                <td>{{ p.studente?.nome }} {{ p.studente?.cognome }}</td>
                <td>{{ p.istituto?.nome }}</td>
                <td>{{ p.pianoesami?.length || 0 }} esami</td>
                <td><a [routerLink]="['/docente/riconosci-esami', p.ida]" class="btn btn-sm btn-success">🎓 Riconosci esami</a></td>
              </tr>
            }
          </tbody>
        </table>
      </div>
    }

    <div class="card">
      <div class="card-title">Tutte le pratiche</div>
      <table>
        <thead><tr><th>Studente</th><th>Istituto</th><th>Periodo</th><th>Stato</th></tr></thead>
        <tbody>
          @for (p of pratiche; track p.ida) {
            <tr>
              <td>{{ p.studente?.nome }} {{ p.studente?.cognome }}</td>
              <td>{{ p.istituto?.nome }}</td>
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

  get laInAttesa() { return this.pratiche.filter(p => p.stato === 'in attesa'); }
  get esamiInAttesa() { return this.pratiche.filter(p => p.stato === 'in corso'); }

  constructor(private praticaService: PraticaService, private cdr: ChangeDetectorRef) {}

 ngOnInit() {
    this.praticaService.getPraticheDocente().subscribe({
      next: (data) => {
        console.log("I DATI SONO ARRIVATI IN ANGULAR:", data);
        this.pratiche = data; 
        this.cdr.detectChanges();
      },
      error: (err) => {
        console.error("Errore di rete:", err);
      }
    });
  }
  getUltimoLa(p: PraticaMobilita) { return p.learning_agreements.at(-1); }

  getBadgeClass(s: string) {
    const m: Record<string,string> = { 
      'creato':'badge-created',
      'in attesa':'badge-waiting',
      'pre-partenza':'badge-approved',
      'in corso':'badge-progress',
      'completato':'badge-closed',
      'annullato':'badge-closed',
      'viaggioCompletato':'badge-closed' 
    };
    return m[s] ?? 'badge-created';
  }

  getStatoLabel(s: string) {
    const m: Record<string,string> = { 
      'creato':'Creata',
      'in attesa':'Attesa LA',
      'pre-partenza':'Pre-partenza ok',
      'in corso':'In corso',
      'completato':'Completata',
      'annullato':'Annullata',
      'viaggioCompletato':'badge-closed' 
    };
    return m[s] ?? s;
  }
}
