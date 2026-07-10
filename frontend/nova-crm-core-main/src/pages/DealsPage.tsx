import { useQuery } from "@tanstack/react-query";
import { AppLayout } from "@/components/AppLayout";
import { PageHeader } from "@/components/shared/PageHeader";
import { EmptyState } from "@/components/shared/EmptyState";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Plus, DollarSign, Calendar } from "lucide-react";
import { dealsApi } from "@/api/deals.api";
import { useNavigate } from "react-router-dom";
import { useState } from "react";
import { DealDialog } from "@/components/dialogs/DealDialog";
import { formatCurrency } from "@/lib/utils";

const STAGE_COLORS: Record<string, string> = {
  prospect: "border-t-info",
  proposal: "border-t-warning",
  negotiation: "border-t-primary",
  won: "border-t-success",
  lost: "border-t-destructive",
};

const STAGE_BG: Record<string, string> = {
  prospect: "bg-info/5",
  proposal: "bg-warning/5",
  negotiation: "bg-primary/5",
  won: "bg-success/5",
  lost: "bg-destructive/5",
};

export default function DealsPage() {
  const navigate = useNavigate();
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingDeal, setEditingDeal] = useState<any>(null);

  const { data: pipelineData, isLoading: pipelineLoading } = useQuery({
    queryKey: ["deals-pipeline"],
    queryFn: () => dealsApi.getPipeline(),
  });

  const { data: dealsData } = useQuery({
    queryKey: ["deals"],
    queryFn: () => dealsApi.list({ page_size: "100" }),
  });

  if (pipelineLoading) {
    return (
      <AppLayout>
        <div className="space-y-6">
          <Skeleton className="h-16 w-full" />
          <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
            {Array.from({ length: 5 }).map((_, i) => (
              <Skeleton key={i} className="h-72 rounded-xl" />
            ))}
          </div>
        </div>
      </AppLayout>
    );
  }

  const pipelineStages = pipelineData?.stages || [];
  const allDeals = dealsData?.items || [];
  const totalValue = pipelineStages.reduce((sum: number, s: any) => sum + s.total_value, 0);

  const dealsByStage: Record<string, any[]> = {};
  allDeals.forEach((d) => {
    if (!dealsByStage[d.stage]) dealsByStage[d.stage] = [];
    dealsByStage[d.stage].push(d);
  });

  const stages = pipelineStages.map((ps: any) => ({
    ...ps,
    deals: dealsByStage[ps.stage] || [],
  }));

  return (
    <AppLayout>
      <PageHeader
        icon={DollarSign}
        title="Deals Pipeline"
        description={`${allDeals.length} deals · ${formatCurrency(totalValue)} total pipeline value`}
        action={
          <Button onClick={() => { setEditingDeal(null); setDialogOpen(true); }}>
            <Plus className="h-4 w-4 mr-2" />New Deal
          </Button>
        }
      />

      {stages.length === 0 ? (
        <div className="data-card">
          <EmptyState
            icon={DollarSign}
            title="No deals in pipeline"
            description="Create your first deal to visualize your sales pipeline."
            action={
              <Button size="sm" onClick={() => { setEditingDeal(null); setDialogOpen(true); }}>
                <Plus className="h-4 w-4 mr-2" />New Deal
              </Button>
            }
          />
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
          {stages.map((stage: any) => (
            <div
              key={stage.stage}
              className={`data-card border-t-4 ${STAGE_COLORS[stage.stage?.toLowerCase()] || "border-t-muted"} flex flex-col`}
            >
              <div className={`px-4 py-3 border-b border-border ${STAGE_BG[stage.stage?.toLowerCase()] || ""}`}>
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-semibold capitalize">{stage.stage}</h3>
                  <span className="text-xs font-medium bg-muted px-2 py-0.5 rounded-full tabular-nums">{stage.count}</span>
                </div>
                <p className="text-xs text-muted-foreground mt-0.5 tabular-nums">{formatCurrency(stage.total_value)}</p>
              </div>
              <div className="p-3 space-y-2 flex-1 max-h-[28rem] overflow-y-auto">
                {stage.deals.map((deal: any) => (
                  <div
                    key={deal.id}
                    onClick={() => navigate(`/deals/${deal.id}`)}
                    className="p-3 rounded-lg border border-border bg-card hover:bg-muted/40 hover:shadow-sm transition-all cursor-pointer"
                  >
                    <p className="text-sm font-medium truncate">{deal.title}</p>
                    <p className="text-xs text-primary font-medium tabular-nums mt-1">
                      {formatCurrency(Number(deal.value))}
                    </p>
                    {deal.close_date && (
                      <div className="flex items-center gap-1 mt-1.5">
                        <Calendar className="h-3 w-3 text-muted-foreground" />
                        <span className="text-xs text-muted-foreground">
                          {new Date(deal.close_date).toLocaleDateString()}
                        </span>
                      </div>
                    )}
                    {deal.probability != null && (
                      <div className="mt-2">
                        <div className="h-1 rounded-full bg-muted overflow-hidden">
                          <div
                            className="h-full rounded-full bg-primary/60"
                            style={{ width: `${deal.probability}%` }}
                          />
                        </div>
                        <p className="text-[10px] text-muted-foreground mt-0.5 tabular-nums">{deal.probability}% probability</p>
                      </div>
                    )}
                  </div>
                ))}
                {stage.deals.length === 0 && (
                  <p className="text-xs text-muted-foreground text-center py-6 italic">No deals</p>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      <DealDialog open={dialogOpen} onOpenChange={setDialogOpen} deal={editingDeal} />
    </AppLayout>
  );
}
