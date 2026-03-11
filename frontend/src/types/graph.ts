// TypeScript interfaces matching graph.json schema

export type NodeType = 'person' | 'company' | 'institution' | 'corporate_client';
export type EdgeType =
  | 'owned'
  | 'heads'
  | 'family'
  | 'works_at'
  | 'contract'
  | 'advisory'
  | 'met_with'
  | 'received_gift'
  | 'board'
  | 'govt_role'
  | 'rumored';

export type NodeStatus = 'mapped' | 'seed';

export type RedFlag =
  | 'SELF_DEALING'
  | 'REVOLVING_DOOR'
  | 'DIRECT_AWARD_CLUSTER'
  | 'LOBBY_TO_CONTRACT'
  | 'CONCENTRATION'
  | 'CORPORATE_RESTRUCTURING'
  | 'GOV_CONTRACTOR'
  | 'COLLUSION_LINK'
  | 'ACTIVE_CONTRACT';

export interface VerifyUrl {
  label: string;
  url: string;
}

export interface GraphNode {
  id: string;
  type: NodeType;
  label: string;
  role?: string;
  party?: string;
  ministry?: string;
  rut?: string;
  flags: RedFlag[];
  sources: string[];
  sourceKeys?: string[];
  verifyUrls: VerifyUrl[];
  addedDate: string;
  lastModified: string;
  status: NodeStatus;
  notes?: string;
  case?: string;
}

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  type: EdgeType;
  label: string;
  flags: RedFlag[];
  sources: string[];
  sourceKeys?: string[];
  verifyUrls: VerifyUrl[];
  addedDate: string;
  lastModified: string;
  amount_clp?: number | null;
  year?: number;
}

export interface GraphSource {
  name: string;
  url: string;
}

export interface GraphMeta {
  generatedAt: string;
  nodeCount: number;
  edgeCount: number;
  sources: Record<string, GraphSource>;
  phase?: number;
  description?: string;
}

export interface Graph {
  nodes: GraphNode[];
  edges: GraphEdge[];
  meta: GraphMeta;
}

// Changelog types

export type EventSeverity = 'high' | 'medium' | 'low' | 'info';

export interface ChangeEvent {
  type: string;
  date: string;
  severity: EventSeverity;
  icon: string;
  title: string;
  desc: string;
  source: string;
  nodeRefs: string[];
}

export interface ChangeWeek {
  week: string;
  events: ChangeEvent[];
}

export interface Changelog {
  updatedAt?: string;
  totalEvents?: number;
  weeks: ChangeWeek[];
}
