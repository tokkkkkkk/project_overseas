// models/models.ts
// Interfacce TypeScript che rispecchiano le tabelle del database

export interface Utente {
  id: number;
  nome: string;
  cognome: string;
  email: string;
  ruolo: 'studente' | 'docente' | 'ufficio';
}

export interface IstitutoOspitante {
  idin: string;
  nome: string;
  paese: string;
  citta: string;
}

export interface MappingEsame {
  id?: number;
  codice_estero: string;
  titolo_estero: string;
  crediti_esteri: number;
  codice_cafoscari: string;
  titolo_cafoscari: string;
  crediti_cafoscari: number;
  voto_ottenuto?: string;
  data_superamento?: string;
  stato_riconoscimento?: 'in_attesa' | 'approvato' | 'rifiutato';
}

export interface LearningAgreement {
  id: number;
  filename: string;
  data_caricamento: string;
  versione: number;
  stato: 'in_attesa' | 'approvato' | 'rifiutato';
  data_decisione?: string;
  motivazione_rifiuto?: string;
}

export interface TranscriptOfRecords {
  id: number;
  filename: string;
  data_caricamento: string;
}

export type StatoPratica =
  | 'creata'
  | 'in_attesa_approvazione_la'
  | 'pre_partenza_completata'
  | 'mobilita_in_corso'
  | 'in_riconoscimento_esami'
  | 'chiusa';

export interface PraticaMobilita {
  id: number;
  anno_accademico: string;
  periodo: string;
  note?: string;
  stato: StatoPratica;
  data_arrivo?: string;
  data_partenza?: string;
  data_creazione: string;
  studente: Utente;
  docente: Utente;
  istituto: IstitutoOspitante;
  mapping_esami: MappingEsame[];
  learning_agreements: LearningAgreement[];
  transcript?: TranscriptOfRecords;
}

export interface AuthResponse {
  token: string;
  ruolo: 'studente' | 'docente' | 'ufficio';
  utente: Utente;
}

export interface ApiResponse<T> {
  data?: T;
  messaggio?: string;
  errore?: string;
}
