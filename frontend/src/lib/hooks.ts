"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type {
  Alert,
  AuditEntry,
  CopilotResponse,
  ExecutiveBriefing,
  Hospital,
  Incident,
  IncidentEvent,
  IntegrationOverview,
  LoginActivity,
  MapFeatures,
  MissionControlSummary,
  Page,
  PipelineMonitor,
  Resource,
  RiskAssessment,
  SecurityOverview,
  SessionInfo,
  Shelter,
  Simulation,
  UtilityOutage,
  WorkspaceInfo,
} from "@/lib/types";

type Query = Record<string, string | number | boolean | undefined | null>;

export function useSecurityOverview() {
  return useQuery({
    queryKey: ["security-overview"],
    queryFn: () => api<SecurityOverview>("/security/overview"),
    staleTime: 30_000,
    retry: false,
  });
}

export function useLoginActivity(limit = 25) {
  return useQuery({
    queryKey: ["login-activity", limit],
    queryFn: () => api<LoginActivity[]>("/security/login-activity", { query: { limit } }),
    retry: false,
  });
}

export function useMySessions() {
  return useQuery({
    queryKey: ["my-sessions"],
    queryFn: () => api<SessionInfo[]>("/auth/sessions"),
  });
}

export function useRevokeSession() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => api(`/auth/sessions/${id}`, { method: "DELETE" }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["my-sessions"] }),
  });
}

export function useLogoutAll() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: () => api("/auth/logout-all", { method: "POST" }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["my-sessions"] }),
  });
}

export function useAuditLog(params: Query) {
  return useQuery({
    queryKey: ["audit", params],
    queryFn: () => api<Page<AuditEntry>>("/audit", { query: params }),
    retry: false,
  });
}

export function useMfaSetup() {
  return useMutation({
    mutationFn: () => api<{ secret: string; otpauth_uri: string }>("/auth/mfa/setup", { method: "POST" }),
  });
}

export function useMfaEnable() {
  return useMutation({
    mutationFn: (code: string) => api("/auth/mfa/enable", { method: "POST", body: { code } }),
  });
}

export function useMfaDisable() {
  return useMutation({
    mutationFn: (code: string) => api("/auth/mfa/disable", { method: "POST", body: { code } }),
  });
}

export function useWorkspace() {
  return useQuery({
    queryKey: ["workspace"],
    queryFn: () => api<WorkspaceInfo>("/workspace"),
    staleTime: 60_000,
  });
}

export function useLaunchDemo() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: () => api<WorkspaceInfo>("/workspace/launch-demo", { method: "POST", body: {} }),
    onSuccess: () => qc.invalidateQueries(),
  });
}

export function useMissionControl() {
  return useQuery({
    queryKey: ["mission-control"],
    queryFn: () => api<MissionControlSummary>("/mission-control/summary"),
    refetchInterval: 30_000,
  });
}

export function useIncidents(query: Query) {
  return useQuery({
    queryKey: ["incidents", query],
    queryFn: () => api<Page<Incident>>("/incidents", { query }),
  });
}

export function useIncident(id: number) {
  return useQuery({
    queryKey: ["incident", id],
    queryFn: () => api<Incident & { events: IncidentEvent[] }>(`/incidents/${id}`),
    enabled: !!id,
  });
}

export function useHospitals(query: Query) {
  return useQuery({
    queryKey: ["hospitals", query],
    queryFn: () => api<Page<Hospital>>("/hospitals", { query }),
  });
}

export function useShelters(query: Query) {
  return useQuery({
    queryKey: ["shelters", query],
    queryFn: () => api<Page<Shelter>>("/shelters", { query }),
  });
}

export function useResources(query: Query) {
  return useQuery({
    queryKey: ["resources", query],
    queryFn: () => api<Page<Resource>>("/resources", { query }),
  });
}

export function useResourceUtilization() {
  return useQuery({
    queryKey: ["resource-utilization"],
    queryFn: () => api<{ by_type: Record<string, { total: number; availability_pct: number; utilization_pct: number; by_status: Record<string, number> }> }>("/resources/utilization"),
  });
}

export function useUtilities(query: Query) {
  return useQuery({
    queryKey: ["utilities", query],
    queryFn: () => api<Page<UtilityOutage>>("/utilities", { query }),
  });
}

export function useMapFeatures(layers: string) {
  return useQuery({
    queryKey: ["map", layers],
    queryFn: () => api<MapFeatures>("/geo/features", { query: { layers } }),
  });
}

export function useRisk() {
  return useQuery({ queryKey: ["risk"], queryFn: () => api<RiskAssessment[]>("/risk") });
}

export function useGenerateRisk() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: () => api<RiskAssessment[]>("/risk/generate", { method: "POST" }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["risk"] }),
  });
}

export function useAlerts(query: Query) {
  return useQuery({
    queryKey: ["alerts", query],
    queryFn: () => api<Page<Alert>>("/alerts", { query }),
  });
}

export function useAlertAction() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, action }: { id: number; action: "acknowledge" | "resolve" }) =>
      api<Alert>(`/alerts/${id}/${action}`, { method: "POST", body: {} }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["alerts"] });
      qc.invalidateQueries({ queryKey: ["mission-control"] });
    },
  });
}

export function useSimulations() {
  return useQuery({ queryKey: ["simulations"], queryFn: () => api<Simulation[]>("/simulations") });
}

export function useRunSimulation() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (body: { name: string; simulation_type: string; parameters: Record<string, unknown> }) =>
      api<Simulation>("/simulations/run", { method: "POST", body }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["simulations"] }),
  });
}

export function useCopilotStatus() {
  return useQuery({
    queryKey: ["copilot-status"],
    queryFn: () =>
      api<{ engine: string; ai_enabled: boolean; model: string; suggested_questions: string[] }>(
        "/copilot/status",
      ),
  });
}

export function useAskCopilot() {
  return useMutation({
    mutationFn: (question: string) =>
      api<CopilotResponse>("/copilot/ask", { method: "POST", body: { question } }),
  });
}

export function useGenerateBriefing() {
  return useMutation({
    mutationFn: () => api<ExecutiveBriefing>("/briefing/generate", { method: "POST", body: {} }),
  });
}

export function useIntegrationOverview() {
  return useQuery({
    queryKey: ["integration-overview"],
    queryFn: () => api<IntegrationOverview>("/integration/overview"),
  });
}

export function usePipeline() {
  return useQuery({
    queryKey: ["pipeline"],
    queryFn: () => api<PipelineMonitor>("/integration/pipeline"),
  });
}

export function useImportCsv() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (body: { target_entity: string; content: string; filename?: string }) =>
      api("/integration/import/csv", { method: "POST", body }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["pipeline"] });
      qc.invalidateQueries({ queryKey: ["integration-overview"] });
    },
  });
}
