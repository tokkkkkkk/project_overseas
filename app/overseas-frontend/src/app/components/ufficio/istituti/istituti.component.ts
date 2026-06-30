// components/ufficio/istituti/istituti.component.ts
import { Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { PraticaService } from '../../../services/pratica.service';
import { IstitutoOspitante } from '../../../models/models';

@Component({
  selector: 'app-istituti',
  standalone: true,
  imports: [FormsModule, CommonModule],
  template: `
    <div class="page-header">
      <div>
        <h1 class="page-title">Gestione istituti partner</h1>
        <p class="page-sub">Lista degli istituti ospitanti disponibili</p>
      </div>
    </div>

    <div class="card">
      <div class="card-title">
        Istituti partner
        <button class="btn btn-primary btn-sm" (click)="mostraForm = !mostraForm">+ Aggiungi istituto</button>
      </div>

      @if (mostraForm) {
        <div class="form-row" style="margin-bottom:1rem">
          <div class="form-group"><label class="form-label">Nome</label>
            <input class="form-control" [(ngModel)]="nuovoIstituto.nome" /></div>
          <div class="form-group"><label class="form-label">Paese</label>
            <input class="form-control" [(ngModel)]="nuovoIstituto.paese" /></div>
          <div class="form-group"><label class="form-label">Città</label>
            <input class="form-control" [(ngModel)]="nuovoIstituto.citta" /></div>
        </div>
        <button class="btn btn-primary btn-sm" (click)="salvaIstituto()">Salva istituto</button>
      }

      <table style="margin-top:1rem">
        <thead><tr><th>Nome</th><th>Paese</th><th>Città</th></tr></thead>
        <tbody>
          @for (ist of istituti; track ist.idin) {
            <tr>
              <td>{{ ist.nome }}</td>
              <td>{{ ist.paese }}</td>
              <td>{{ ist.citta }}</td>
            </tr>
          }
        </tbody>
      </table>
    </div>
  `
})
export class IstitutiComponent implements OnInit {
  istituti: IstitutoOspitante[] = [];
  mostraForm = false;
  nuovoIstituto: Partial<IstitutoOspitante> = { nome: '', paese: '', citta: '' };

  constructor(private praticaService: PraticaService) {}

  ngOnInit() { this.praticaService.getIstituti().subscribe(d => this.istituti = d); }

  salvaIstituto() {
    // Nota: implementa l'endpoint POST /api/istituti nel backend per completare questa funzione
    this.mostraForm = false;
  }
}
