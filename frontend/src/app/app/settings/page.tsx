"use client";

import { Building2, Mail, Shield, User as UserIcon } from "lucide-react";
import { useAuth } from "@/lib/auth";
import { useWorkspace } from "@/lib/hooks";
import { Card, CardHeader } from "@/components/ui/card";
import { LoadingPanel } from "@/components/ui/primitives";
import { DataSourceBadge } from "@/components/data-source-badge";
import { fmtNumber, titleCase } from "@/lib/utils";

export default function SettingsPage() {
  const { user, organization } = useAuth();
  const { data: workspace, isLoading } = useWorkspace();

  if (isLoading || !user) return <LoadingPanel />;

  const counts = workspace?.record_counts ?? {};

  return (
    <div className="space-y-6">
      <div className="border-b border-line pb-4">
        <h1 className="text-xl font-bold tracking-tight text-ink">Settings</h1>
        <p className="mt-1 text-sm text-ink-muted">Manage your profile, organization, and data.</p>
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader title="Profile" subtitle="Your account details" icon={<UserIcon className="h-4 w-4" />} />
          <div className="space-y-3">
            <Row label="Full name" value={user.full_name} />
            <Row label="Email" value={user.email} icon={<Mail className="h-3.5 w-3.5" />} />
            <Row label="Role" value={titleCase(user.role)} icon={<Shield className="h-3.5 w-3.5" />} />
            <Row label="Email verified" value={user.is_verified ? "Verified" : "Pending"} />
          </div>
        </Card>

        <Card>
          <CardHeader title="Organization" subtitle="Workspace configuration" icon={<Building2 className="h-4 w-4" />} />
          <div className="space-y-3">
            <Row label="Name" value={organization?.name ?? "—"} />
            <Row label="Industry" value={organization ? titleCase(organization.industry) : "—"} />
            <Row label="Plan" value={organization ? titleCase(organization.plan) : "—"} />
            <div className="flex items-center justify-between">
              <span className="text-xs text-ink-faint">Mode</span>
              <DataSourceBadge origin={workspace?.primary_data_origin ?? "none"} />
            </div>
          </div>
        </Card>
      </div>

      <Card>
        <CardHeader title="Data overview" subtitle="Records in this workspace" />
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-6">
          {[
            ["incidents", "Incidents"],
            ["hospitals", "Hospitals"],
            ["shelters", "Shelters"],
            ["resources", "Resources"],
            ["utility_outages", "Outages"],
            ["alerts", "Alerts"],
          ].map(([key, label]) => (
            <div key={key} className="rounded-lg border border-line bg-bg-soft p-4">
              <p className="text-2xl font-bold text-ink">{fmtNumber(counts[key] ?? 0)}</p>
              <p className="mt-1 text-[11px] uppercase tracking-wider text-ink-faint">{label}</p>
            </div>
          ))}
        </div>
        {workspace?.data_sources_in_use && workspace.data_sources_in_use.length > 0 && (
          <div className="mt-4 flex flex-wrap items-center gap-2 border-t border-line pt-4">
            <span className="text-xs text-ink-faint">Active data origins:</span>
            {workspace.data_sources_in_use.map((s) => (
              <span key={s} className="chip">{s}</span>
            ))}
          </div>
        )}
      </Card>
    </div>
  );
}

function Row({ label, value, icon }: { label: string; value: string; icon?: React.ReactNode }) {
  return (
    <div className="flex items-center justify-between">
      <span className="text-xs text-ink-faint">{label}</span>
      <span className="flex items-center gap-1.5 text-sm font-medium text-ink">
        {icon}
        {value}
      </span>
    </div>
  );
}
