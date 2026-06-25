"use client";

import { useEffect } from "react";
import { usePathname, useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth";
import { useWorkspace } from "@/lib/hooks";
import { Sidebar } from "@/components/shell";
import { Topbar } from "@/components/topbar";
import { DemoBanner } from "@/components/demo-banner";
import { ConnectedOnboarding } from "@/components/connected-onboarding";
import { CommandPaletteProvider } from "@/components/command-palette";
import { LoadingPanel } from "@/components/ui/primitives";

// Routes that must remain reachable even when the workspace has no data,
// so users can actually bring data online.
const ALLOW_WHEN_EMPTY = ["/app/integration", "/app/settings", "/app/security", "/app/audit"];

function WorkspaceGate({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const { data: workspace, isLoading } = useWorkspace();

  if (isLoading) return <LoadingPanel label="Loading workspace…" />;

  const allowed = ALLOW_WHEN_EMPTY.some((p) => pathname.startsWith(p));
  if (workspace?.is_empty && !allowed) {
    return <ConnectedOnboarding />;
  }
  return <>{children}</>;
}

export default function AppLayout({ children }: { children: React.ReactNode }) {
  const { user, organization, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (loading) return;
    if (!user) {
      router.replace("/login");
    } else if (!organization && !user.organization_id) {
      router.replace("/onboarding");
    }
  }, [loading, user, organization, router]);

  if (loading || !user) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <LoadingPanel label="Establishing secure session…" />
      </div>
    );
  }

  if (!organization) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <LoadingPanel label="Loading your organization…" />
      </div>
    );
  }

  return (
    <CommandPaletteProvider>
      <div className="min-h-screen">
        <Sidebar />
        <div className="pl-64">
          {organization.is_demo && <DemoBanner />}
          <Topbar />
          <main className="mx-auto max-w-[1500px] px-6 py-6">
            <WorkspaceGate>{children}</WorkspaceGate>
          </main>
        </div>
      </div>
    </CommandPaletteProvider>
  );
}
