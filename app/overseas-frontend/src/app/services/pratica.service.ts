// services/pratica.service.ts
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { PraticaMobilita, MappingEsame, IstitutoOspitante, Utente } from '../models/models';

@Injectable({ providedIn: 'root' })
export class PraticaService {

  private apiUrl = 'http://localhost:5000/api';

  constructor(private http: HttpClient) { }

  // ---- PRATICHE ----

  getMiePratiche(): Observable<PraticaMobilita[]> {
    return this.http.get<PraticaMobilita[]>(`${this.apiUrl}/studente/pratiche`);
  }

  getTutteLePratiche(): Observable<PraticaMobilita[]> {
    return this.http.get<PraticaMobilita[]>(`${this.apiUrl}/ufficio/app/tutte`);
  }

  getPraticaById(id: number): Observable<PraticaMobilita> {
    return this.http.get<PraticaMobilita>(`${this.apiUrl}/pratiche/${id}`);
  }

  creaPratica(dati: {
    anno_accademico: string;
    istituto_id: string;
    periodo: string;
    docente_id: number;
    note?: string;
    mapping_esami: MappingEsame[];
  }): Observable<PraticaMobilita> {
    return this.http.post<PraticaMobilita>(`${this.apiUrl}/studente/pratiche`, dati);
  }

  aggiornaPratica(id: string, dati: Partial<PraticaMobilita>): Observable<PraticaMobilita> {
    return this.http.put<PraticaMobilita>(`${this.apiUrl}/pratiche/${id}`, dati);
  }

  // ---- LEARNING AGREEMENT ----

  caricaLearningAgreement(praticaId: string, file: File): Observable<any> {
    const formData = new FormData();
    formData.append('file', file);
    return this.http.post(`${this.apiUrl}/pratiche/${praticaId}/learning-agreement`, formData);
  }

  valutaLearningAgreement(laId: number, decisione: 'approvato' | 'rifiutato', motivazione?: string): Observable<any> {
    return this.http.put(`${this.apiUrl}/learning-agreement/${laId}/valuta`, { decisione, motivazione });
  }

  // ---- TRANSCRIPT ----

  caricaTranscript(praticaId: string, file: File): Observable<any> {
    const formData = new FormData();
    formData.append('file', file);
    return this.http.post(`${this.apiUrl}/pratiche/${praticaId}/transcript`, formData);
  }

  // ---- ESAMI ----

  aggiornaVotiEsami(praticaId: string, esami: MappingEsame[]): Observable<any> {
    return this.http.put(`${this.apiUrl}/pratiche/${praticaId}/esami`, { esami });
  }

  riconosciEsame(esameId: number, decisione: 'approvato' | 'rifiutato'): Observable<any> {
    return this.http.put(`${this.apiUrl}/esami/${esameId}/riconosci`, { decisione });
  }

  // ---- UFFICIO ----

  completaPrePartenza(praticaId: string): Observable<any> {
    return this.http.put(`${this.apiUrl}/pratiche/${praticaId}/pre-partenza`, {});
  }

  chiudiPratica(praticaId: string): Observable<any> {
    return this.http.put(`${this.apiUrl}/pratiche/${praticaId}/chiudi`, {});
  }

  // ---- ISTITUTI E DOCENTI ----

  getIstituti(): Observable<IstitutoOspitante[]> {
    return this.http.get<IstitutoOspitante[]>(`${this.apiUrl}/studente/istituti`);
  }

  getDocenti(): Observable<Utente[]> {
    return this.http.get<Utente[]>(`${this.apiUrl}/studente/docente`);
  }

  aggiungiIstituo(datiIstituto: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/ufficio/istituti`, datiIstituto);
  }
}
