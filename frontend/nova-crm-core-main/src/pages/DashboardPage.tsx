import { useQuery } from "@tanstack/react-query";
import { Bar, BarChart, CartesianGrid, Cell, Pie, PieChart, XAxis, YAxis } from "recharts";
import { AppLayout } from "@/components/AppLayout";
import { StatCard } from "@/components/StatCard";
import { PageHeader } from "@/components/shared/PageHeader";
import { DashboardSkeleton } from "@/components/shared/PageSkeleton";
import { ActivityFeed } from "@/components/ActivityFeed";
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart";
import { Users, Target, DollarSign, CheckSquare, LayoutDashboard, TrendingUp, Medal } from "lucide-react";
import { dashboardApi } from "@/api/dashboard.api";
import { formatCurrency, getInitials } from "@/lib/utils";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";

const STAGE_COLORS: Record<string, string> = {
  prospect: "hsl(var(--info))",
  proposal: "hsl(var(--warning))",
  negotiation: "hsl(var(--primary))",
  won: "hsl(var(--success))",
  lost: "hsl(var(--destructive))",
};

const STAGE_ORDER = ["prospect", "proposal", "negotiation", "won", "lost"];

const pipelineChartConfig = {
  count: { label: "Deals", color: "hsl(var(--primary))" },
  value: { label: "Value", color: "hsl(var(--info))" },
};

export default function DashboardPage() {
  const { data: stats, isLoading, error } = useQuery({
    queryKey: ["dashboard"],
    queryFn: () => dashboardApi.get(),
  });

  if (isLoading) {
    return (
      <AppLayout>
        <DashboardSkeleton />
      </AppLayout>
    );
  }

  if (error) {
    return (
      <AppLayout>
        <div className="p-4 bg-destructive/10 text-destructive rounded-xl border border-destructive/20 text-sm">
          Failed to load dashboard data. Please refresh the page.
        </div>
      </AppLayout>
    );
  }

  const { summary, pipeline_by_stage, agent_performance } = stats!;
  const totalPipelineValue = pipeline_by_stage.reduce((sum, s) => sum + s.total_value, 0);
  const totalDeals = pipeline_by_stage.reduce((sum, s) => sum + s.count, 0);
  const wonDeals = pipeline_by_stage.find((s) => s.stage === "won")?.count || 0;
  const winRate = totalDeals > 0 ? Math.round((wonDeals / totalDeals) * 100) : 0;

  const orderedPipeline = STAGE_ORDER
    .map((stage) => pipeline_by_stage.find((s) => s.stage === stage))
    .filter(Boolean) as typeof pipeline_by_stage;

  const pipelineChartData = orderedPipeline.map((s) => ({
    stage: s.stage.charAt(0).toUpperCase() + s.stage.slice(1),
    count: s.count,
    value: s.total_value,
    fill: STAGE_COLORS[s.stage] || "hsl(var(--muted-foreground))",
  }));

  const pieData = orderedPipeline
    .filter((s) => s.stage !== "lost" && s.count > 0)
    .map((s) => ({
      name: s.stage.charAt(0).toUpperCase() + s.stage.slice(1),
      value: s.total_value,
      fill: STAGE_COLORS[s.stage],
    }));

  return (
    <AppLayout>
      <PageHeader
        icon={LayoutDashboard}
        title="Dashboard"
        description="Your sales performance at a glance — pipeline health, activity, and team metrics."
      />

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <StatCard
          title="Total Contacts"
          value={summary.total_contacts.toLocaleString()}
          icon={Users}
          trend="neutral"
          trendLabel="Active in your workspace"
        />
        <StatCard
          title="Open Leads"
          value={summary.open_leads}
          icon={Target}
          trend={summary.open_leads > 0 ? "up" : "neutral"}
          trendLabel={summary.open_leads > 0 ? "Requires follow-up" : "All leads processed"}
        />
        <StatCard
          title="Pipeline Value"
          value={formatCurrency(totalPipelineValue)}
          icon={DollarSign}
          trend="up"
          trendLabel={`${winRate}% win rate`}
        />
        <StatCard
          title="Tasks Due Today"
          value={summary.tasks_due_today}
          icon={CheckSquare}
          trend={summary.tasks_due_today > 0 ? "down" : "up"}
          trendLabel={summary.tasks_due_today > 0 ? "Action required" : "All clear"}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
        <div className="lg:col-span-2 data-card">
          <div className="px-5 py-4 border-b border-border flex items-center gap-2">
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
            <h2 className="text-sm font-semibold">Pipeline by Stage</h2>
          </div>
          <div className="p-5">
            {pipelineChartData.length > 0 ? (
              <ChartContainer config={pipelineChartConfig} className="h-64 w-full">
                <BarChart data={pipelineChartData} margin={{ top: 8, right: 8, left: -16, bottom: 0 }}>
                  <CartesianGrid vertical={false} strokeDasharray="3 3" className="stroke-border/50" />
                  <XAxis dataKey="stage" tickLine={false} axisLine={false} className="text-xs" />
                  <YAxis tickLine={false} axisLine={false} className="text-xs" allowDecimals={false} />
                  <ChartTooltip
                    content={
                      <ChartTooltipContent
                        formatter={(value, name) => [
                          name === "value" ? formatCurrency(Number(value)) : value,
                          name === "value" ? "Value" : "Deals",
                        ]}
                      />
                    }
                  />
                  <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                    {pipelineChartData.map((entry, i) => (
                      <Cell key={i} fill={entry.fill} />
                    ))}
                  </Bar>
                </BarChart>
              </ChartContainer>
            ) : (
              <p className="text-sm text-muted-foreground text-center py-12">No pipeline data yet. Create your first deal to get started.</p>
            )}
          </div>
        </div>

        <div className="data-card">
          <div className="px-5 py-4 border-b border-border flex items-center gap-2">
            <DollarSign className="h-4 w-4 text-muted-foreground" />
            <h2 className="text-sm font-semibold">Value Distribution</h2>
          </div>
          <div className="p-5">
            {pieData.length > 0 ? (
              <>
                <ChartContainer config={pipelineChartConfig} className="h-48 w-full">
                  <PieChart>
                    <ChartTooltip
                      content={
                        <ChartTooltipContent
                          formatter={(value) => [formatCurrency(Number(value)), "Value"]}
                        />
                      }
                    />
                    <Pie
                      data={pieData}
                      dataKey="value"
                      nameKey="name"
                      cx="50%"
                      cy="50%"
                      innerRadius={50}
                      outerRadius={75}
                      paddingAngle={3}
                    >
                      {pieData.map((entry, i) => (
                        <Cell key={i} fill={entry.fill} />
                      ))}
                    </Pie>
                  </PieChart>
                </ChartContainer>
                <div className="mt-4 space-y-2">
                  {orderedPipeline.map((s) => (
                    <div key={s.stage} className="flex items-center justify-between text-xs">
                      <div className="flex items-center gap-2">
                        <div
                          className="h-2.5 w-2.5 rounded-full"
                          style={{ background: STAGE_COLORS[s.stage] }}
                        />
                        <span className="capitalize text-foreground font-medium">{s.stage}</span>
                      </div>
                      <span className="text-muted-foreground tabular-nums">
                        {s.count} · {formatCurrency(s.total_value)}
                      </span>
                    </div>
                  ))}
                </div>
              </>
            ) : (
              <p className="text-sm text-muted-foreground text-center py-12">No deal values to display.</p>
            )}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 data-card">
          <div className="px-5 py-4 border-b border-border">
            <h2 className="text-sm font-semibold">Recent Activity</h2>
          </div>
          <div className="p-5">
            <ActivityFeed limit={10} />
          </div>
        </div>

        <div className="data-card">
          <div className="px-5 py-4 border-b border-border flex items-center gap-2">
            <Medal className="h-4 w-4 text-muted-foreground" />
            <h2 className="text-sm font-semibold">Team Performance</h2>
          </div>
          <div className="p-5 space-y-4">
            {agent_performance.map((agent, i) => (
              <div key={agent.user_id} className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="relative">
                    <Avatar className="h-9 w-9">
                      <AvatarFallback className="bg-primary/10 text-primary text-xs font-semibold">
                        {getInitials(agent.full_name)}
                      </AvatarFallback>
                    </Avatar>
                    {i === 0 && agent.deals_won > 0 && (
                      <span className="absolute -top-1 -right-1 h-4 w-4 rounded-full bg-warning text-[9px] font-bold text-warning-foreground flex items-center justify-center">
                        1
                      </span>
                    )}
                  </div>
                  <div>
                    <p className="text-sm font-medium">{agent.full_name}</p>
                    <p className="text-xs text-muted-foreground">{agent.leads_contacted} leads contacted</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-lg font-semibold tabular-nums">{agent.deals_won}</p>
                  <p className="text-xs text-muted-foreground">deals won</p>
                </div>
              </div>
            ))}
            {agent_performance.length === 0 && (
              <p className="text-sm text-muted-foreground text-center py-6">No performance data yet.</p>
            )}
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
