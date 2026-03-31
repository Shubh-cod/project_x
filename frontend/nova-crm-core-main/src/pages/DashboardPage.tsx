import { useQuery } from "@tanstack/react-query";
import { AppLayout } from "@/components/AppLayout";
import { StatCard } from "@/components/StatCard";
import { Users, Target, DollarSign, CheckSquare, TrendingUp, Clock, Medal } from "lucide-react";
import { dashboardApi } from "@/api/dashboard.api";
import { ActivityFeed } from "@/components/ActivityFeed";

export default function DashboardPage() {
  const { data: stats, isLoading, error } = useQuery({
    queryKey: ["dashboard"],
    queryFn: () => dashboardApi.get(),
  });

  if (isLoading) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center h-[50vh]">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
        </div>
      </AppLayout>
    );
  }

  if (error) {
    return (
      <AppLayout>
        <div className="p-4 bg-destructive/10 text-destructive rounded-lg border border-destructive/20">
          Failed to load dashboard data. Please try again later.
        </div>
      </AppLayout>
    );
  }

  const { summary, pipeline_by_stage } = stats!;

  return (
    <AppLayout>
      <div className="mb-6">
        <h1 className="text-2xl font-display font-bold text-foreground">Dashboard</h1>
        <p className="text-sm text-muted-foreground mt-1">Welcome back. Here's your CRM overview.</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <StatCard title="Total Contacts" value={summary.total_contacts.toLocaleString()} icon={Users} trend="Currently active" />
        <StatCard title="Open Leads" value={summary.open_leads} icon={Target} trend="Action required" />
        <StatCard title="Deals Won" value={summary.deals_won_this_month} icon={DollarSign} trend="This month" />
        <StatCard title="Tasks Due Today" value={summary.tasks_due_today} icon={CheckSquare} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Activities */}
        <div className="lg:col-span-2 bg-card rounded-lg border border-border">
          <div className="px-5 py-4 border-b border-border flex items-center gap-2">
            <Clock className="h-4 w-4 text-muted-foreground" />
            <h2 className="text-sm font-semibold text-foreground">Recent Activity</h2>
          </div>
          <div className="p-5">
            <ActivityFeed limit={10} />
          </div>
        </div>

        {/* Right Column: Pipeline & Performance */}
        <div className="space-y-6">
          <div className="bg-card rounded-lg border border-border flex flex-col h-full">
          <div className="px-5 py-4 border-b border-border flex items-center gap-2">
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
            <h2 className="text-sm font-semibold text-foreground">Pipeline Summary</h2>
          </div>
          <div className="p-5 space-y-4">
            {pipeline_by_stage.map((s) => (
              <div key={s.stage}>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-foreground font-medium capitalize">{s.stage}</span>
                  <span className="text-muted-foreground">{s.count} · ${s.total_value.toLocaleString()}</span>
                </div>
                <div className="h-2 rounded-full bg-secondary">
                  <div
                    className="h-full rounded-full bg-primary transition-all"
                    style={{ width: `${Math.min(100, (s.count / 20) * 100)}%` }}
                  />
                </div>
              </div>
            ))}
            {pipeline_by_stage.length === 0 && (
              <p className="text-sm text-muted-foreground text-center py-4">No deals in pipeline.</p>
            )}
          </div>
        </div>

        {/* Agent Performance */}
        <div className="bg-card rounded-lg border border-border">
          <div className="px-5 py-4 border-b border-border flex items-center gap-2">
            <Medal className="h-4 w-4 text-muted-foreground" />
            <h2 className="text-sm font-semibold text-foreground">Agent Performance</h2>
          </div>
          <div className="p-5">
            <div className="space-y-4">
              {stats.agent_performance.map((agent) => (
                <div key={agent.user_id} className="flex items-center justify-between border-b border-border/50 pb-3 last:border-0 last:pb-0">
                  <div className="flex items-center gap-3">
                    <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center text-xs font-semibold text-primary">
                      {agent.full_name.split(" ").map((n) => n[0]).join("")}
                    </div>
                    <div>
                      <h4 className="text-sm font-medium text-foreground">{agent.full_name}</h4>
                      <p className="text-xs text-muted-foreground">{agent.leads_contacted} leads contacted</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <span className="text-sm font-bold text-foreground">{agent.deals_won}</span>
                    <p className="text-xs text-muted-foreground">deals won</p>
                  </div>
                </div>
              ))}
              {stats.agent_performance.length === 0 && (
                <p className="text-sm text-muted-foreground text-center py-4">No performance data yet.</p>
              )}
            </div>
          </div>
        </div>
        </div>
      </div>
    </AppLayout>
  );
}
