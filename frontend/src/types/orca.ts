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
  activity?: string;
  requested_time?: Record<string, string> | null;
  plan?: Array<Record<string, unknown>>;
  agent_results?: Array<Record<string, unknown>>;
  evidence?: OrcaEvidence[];
  risk_assessment?: OrcaRisk | Record<string, unknown>;
  recommendation?: Record<string, unknown>;
  assistant_response?: string;
  response_source?: string;
  errors?: string[];
  conversation_id?: string;
  [key: string]: unknown;
}
