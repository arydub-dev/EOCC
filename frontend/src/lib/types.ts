export type Role = "admin" | "emergency_manager" | "analyst" | "executive" | "viewer";

export type Industry =
  | "government"
  | "emergency_services"
  | "healthcare"
  | "utilities"
  | "disaster_response"
  | "ngo"
  | "critical_infrastructure"
  | "other";

export type WorkspaceModeType = "demo" | "connected";
export type PlanType = "starter" | "professional" | "enterprise";

export interface User {
  id: number;
  email: string;
  full_name: string;
  role: Role;
  organization_id?: number | null;
  organization?: string | null;
  is_active: boolean;
  is_verified: boolean;
  mfa_enabled?: boolean;
  last_login_at?: string | null;
  created_at: string;
  permissions?: string[];
}

export interface Organization {
  id: number;
  name: string;
  slug: string;
  industry: Industry;
  mode: WorkspaceModeType;
  plan: PlanType;
  is_demo: boolean;
  provisioned: boolean;
  region?: string | null;
}

export interface TokenResponse {
  access_token: string;
  refresh_token?: string | null;
  token_type: string;
  expires_in?: number;
  user: User;
  permissions?: string[];
  needs_onboarding: boolean;
  organization?: Organization | null;
  mfa_required?: boolean;
}

export interface SessionInfo {
  id: number;
  device_label?: string | null;
  ip_address?: string | null;
  user_agent?: string | null;
  issued_at: string;
  last_used_at?: string | null;
  expires_at: string;
  revoked_at?: string | null;
  revoked_reason?: string | null;
}

export interface SecurityOverview {
  security_score: number;
  grade: string;
  total_users: number;
  mfa_enabled_users: number;
  mfa_adoption_pct: number;
  verified_users: number;
  locked_users: number;
  active_sessions: number;
  failed_logins_24h: number;
  successful_logins_24h: number;
  audit_events_7d: number;
  security_events_7d: number;
  password_policy: {
    min_length: number;
    require_upper: boolean;
    require_lower: boolean;
    require_digit: boolean;
    require_symbol: boolean;
    lockout_threshold: number;
    lockout_minutes: number;
  };
  recommendations: string[];
}

export interface LoginActivity {
  id: number;
  email: string;
  successful: boolean;
  reason?: string | null;
  ip_address?: string | null;
  user_agent?: string | null;
  created_at: string;
}

export interface AuditEntry {
  id: number;
  actor_id?: number | null;
  actor_email?: string | null;
  action: string;
  category: string;
  entity_type?: string | null;
  entity_id?: string | null;
  detail?: Record<string, unknown> | null;
  old_value?: Record<string, unknown> | null;
  new_value?: Record<string, unknown> | null;
  ip_address?: string | null;
  correlation_id?: string | null;
  created_at: string;
}

export interface WorkspaceInfo {
  organization: Organization;
  data_sources_in_use: string[];
  primary_data_origin: string;
  record_counts: Record<string, number>;
  is_empty: boolean;
}

export interface Page<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

export interface MetricCard {
  key: string;
  label: string;
  value: number;
  unit?: string | null;
  trend?: number | null;
  status: string;
  detail?: string | null;
}

export interface RecommendedAction {
  priority: number;
  title: string;
  rationale: string;
  category: string;
  impact: string;
  confidence: number;
}

export interface Alert {
  id: number;
  category: string;
  severity: string;
  status: string;
  title: string;
  message: string;
  region?: string | null;
  source?: string | null;
  incident_id?: number | null;
  acknowledged_at?: string | null;
  resolved_at?: string | null;
  response_actions?: { action: string; notes?: string; at: string }[] | null;
  triggered_at: string;
}

export interface MissionControlSummary {
  overall_health_score: number;
  health_status: string;
  incident_severity_score: number;
  population_impacted: number;
  active_incidents: number;
  escalating_incidents: number;
  hospital_capacity_pct: number;
  hospitals_at_risk: number;
  shelter_utilization_pct: number;
  shelters_overcrowded: number;
  resource_availability_pct: number;
  resource_readiness_pct: number;
  open_alerts: number;
  critical_alerts: number;
  metrics: MetricCard[];
  critical_alerts_list: Alert[];
  recommended_actions: RecommendedAction[];
  situation_report: string;
}

export interface Incident {
  id: number;
  name: string;
  incident_type: string;
  status: string;
  description?: string | null;
  region?: string | null;
  latitude: number;
  longitude: number;
  radius_km: number;
  severity: number;
  severity_score: number;
  population_impacted: number;
  started_at: string;
  estimated_duration_hours?: number | null;
  resolved_at?: string | null;
}

export interface IncidentEvent {
  id: number;
  event_type: string;
  description: string;
  severity_delta: number;
  occurred_at: string;
}

export interface Hospital {
  id: number;
  name: string;
  region?: string | null;
  latitude: number;
  longitude: number;
  total_beds: number;
  occupied_beds: number;
  icu_beds: number;
  icu_occupied: number;
  er_capacity: number;
  er_patients: number;
  staff_on_duty: number;
  staff_required: number;
  status: string;
  stress_score: number;
  bed_occupancy_pct: number;
  icu_occupancy_pct: number;
  er_load_pct: number;
}

export interface Shelter {
  id: number;
  name: string;
  region?: string | null;
  latitude: number;
  longitude: number;
  capacity: number;
  occupancy: number;
  food_supply_days: number;
  water_supply_days: number;
  medical_kits: number;
  medical_staff: number;
  status: string;
  utilization_score: number;
  occupancy_pct: number;
}

export interface Resource {
  id: number;
  name: string;
  resource_type: string;
  status: string;
  region?: string | null;
  home_base?: string | null;
  latitude: number;
  longitude: number;
  capacity: number;
  capacity_unit?: string | null;
  quantity_available: number;
  readiness: number;
}

export interface UtilityOutage {
  id: number;
  utility_type: string;
  status: string;
  region?: string | null;
  latitude: number;
  longitude: number;
  customers_affected: number;
  description?: string | null;
  started_at: string;
  estimated_restoration?: string | null;
}

export interface RiskAssessment {
  id: number;
  category: string;
  severity: string;
  score: number;
  title: string;
  explanation: string;
  recommendations?: string[] | null;
  factors?: Record<string, number> | null;
  region?: string | null;
  generated_at: string;
}

export interface Simulation {
  id: number;
  name: string;
  simulation_type: string;
  status: string;
  parameters: Record<string, unknown>;
  results?: Record<string, unknown> | null;
  recommendations?: string[] | null;
  operational_risk: number;
  created_at: string;
}

export interface CopilotResponse {
  answer: string;
  engine: string;
  confidence: number;
  grounding: Record<string, unknown>;
  suggested_actions: string[];
  citations: string[];
  follow_ups: string[];
}

export interface BriefingSection {
  heading: string;
  body: string;
  bullets: string[];
}

export interface ExecutiveBriefing {
  title: string;
  generated_at: string;
  engine: string;
  executive_summary: string;
  sections: BriefingSection[];
  markdown: string;
}

export interface DataSource {
  id: number;
  name: string;
  source_type: string;
  status: string;
  endpoint?: string | null;
  description?: string | null;
  last_sync_at?: string | null;
  sync_interval_minutes: number;
  records_synced: number;
  health_score: number;
  enabled: boolean;
}

export interface IntegrationOverview {
  connected_systems: number;
  healthy: number;
  degraded: number;
  offline: number;
  total_records_synced: number;
  avg_health_score: number;
  last_sync_at?: string | null;
  sources: DataSource[];
}

export interface ImportJob {
  id: number;
  source_type: string;
  target_entity: string;
  status: string;
  filename?: string | null;
  records_total: number;
  records_processed: number;
  records_failed: number;
  duration_ms: number;
  errors?: { row: number; error: string }[] | null;
  created_at: string;
}

export interface PipelineMonitor {
  total_jobs: number;
  completed: number;
  failed: number;
  partial: number;
  records_processed: number;
  records_failed: number;
  avg_duration_ms: number;
  pipeline_health: number;
  recent_jobs: ImportJob[];
}

export interface MapFeatures {
  layers: {
    incidents?: MapIncident[];
    hospitals?: MapPoint[];
    shelters?: MapPoint[];
    resources?: MapPoint[];
    utilities?: MapPoint[];
  };
}

export interface MapIncident {
  id: number;
  name: string;
  type: string;
  status: string;
  lat: number;
  lng: number;
  radius_km: number;
  severity_score: number;
  population_impacted: number;
  color: string;
}

export interface MapPoint {
  id: number;
  name?: string;
  type?: string;
  lat: number;
  lng: number;
  status: string;
  color?: string;
  stress_score?: number;
  utilization_score?: number;
  customers_affected?: number;
  occupancy?: number;
  capacity?: number;
}
