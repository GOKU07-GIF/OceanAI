export interface OrcaRequest {
  query: string;
  language?: string;
  latitude?: number;
  longitude?: number;
  conversation_id?: string;
}

export interface OrcaEvidence {
  source?: string;
  metric?: string;
  value?: string | number | null;
  unit?: string;
  timestamp?: string | null;
  [key: string]: unknown;
}

export interface OrcaRisk {
  level?: string;
  score?: number;
  factors?: string[];
  [key: string]: unknown;
}

export interface OrcaResponse {
  response?: string;
  answer?: string;
  recommendation?: string | Record<string, unknown>;
  evidence?: OrcaEvidence[] | Record<string, unknown>;
  risk?: OrcaRisk | string | Record<string, unknown>;
  errors?: string[];
  agent_results?: Record<string, unknown>;
  conversation_id?: string;
  [key: string]: unknown;
}
