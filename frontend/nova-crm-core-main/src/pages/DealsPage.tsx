import { useQuery, useQueryClient } from "@tanstack/react-query";
import { AppLayout } from "@/components/AppLayout";
import { Button } from "@/components/ui/button";
import { Plus, DollarSign, GripVertical } from "lucide-react";
import { dealsApi } from "@/api/deals.api";
import { useNavigate } from "react-router-dom";
import { useState } from "react";
import { DealDialog } from "@/components/dialogs/DealDialog";

function formatCurrency(val: number) {
  return new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 }).format(val);
}

const STAGE_COLORS: Record<string, string> = {
  prospect: "border-t-info",
  proposal: "border-t-warning",
  negotiation: "border-t-primary",
  won: "border-t-success",
  lost: "border-t-destructive",
};

export default function DealsPage() {
  const queryClient = useQueryClient();
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
        <div className="flex items-center justify-center h-[50vh]">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
        </div>
      </AppLayout>
    );
  }

  const pipelineStages = pipelineData?.stages || [];
  const allDeals = dealsData?.items || [];

  // Group deals by stage for card display
  const dealsByStage: Record<string, any[]> = {};
  allDeals.forEach((d) => {
    if (!dealsByStage[d.stage]) dealsByStage[d.stage] = [];
    dealsByStage[d.stage].push(d);
  });

  // Merge pipeline stage info with actual deals
  const stages = pipelineStages.map((ps: any) => ({
    ...ps,
    deals: dealsByStage[ps.stage] || [],
  }));

  return (
    <AppLayout>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-display font-bold text-foreground">Deals Pipeline</h1>
          <p className="text-sm text-muted-foreground mt-1">Visual overview of your sales pipeline</p>
        </div>
        <Button onClick={() => { setEditingDeal(null); setDialogOpen(true); }}>
          <Plus className="h-4 w-4 mr-2" />
          New Deal
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        {stages.map((stage: any) => (
          <div key={stage.stage} className={`bg-card rounded-lg border border-border border-t-4 ${STAGE_COLORS[stage.stage?.toLowerCase()] || "border-t-muted"}`}>
            <div className="px-4 py-3 border-b border-border">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-semibold text-foreground capitalize">{stage.stage}</h3>
                <span className="text-xs text-muted-foreground">{stage.count}</span>
              </div>
              <p className="text-xs text-muted-foreground mt-0.5">{formatCurrency(stage.total_value)}</p>
            </div>
            <div className="p-3 space-y-2 max-h-96 overflow-y-auto">
              {stage.deals.map((deal: any) => (
                <div
                  key={deal.id}
                  onClick={() => navigate(`/deals/${deal.id}`)}
                  className="p-3 bg-secondary/30 rounded-md cursor-pointer hover:bg-secondary/60 transition-colors"
                >
                  <p className="text-sm font-medium text-foreground truncate">{deal.title}</p>
                  <div className="flex items-center gap-1 mt-1">
                    <DollarSign className="h-3 w-3 text-muted-foreground" />
                    <span className="text-xs text-muted-foreground">{formatCurrency(Number(deal.value))}</span>
                  </div>
                  {deal.close_date && (
                    <p className="text-xs text-muted-foreground mt-1">Close: {new Date(deal.close_date).toLocaleDateString()}</p>
                  )}
                </div>
              ))}
              {stage.deals.length === 0 && (
                <div className="p-4 text-center text-xs text-muted-foreground italic bg-secondary/20 rounded-md">
                  No deals
                </div>
              )}
            </div>
          </div>
        ))}
        {stages.length === 0 && (
          <div className="col-span-full py-12 text-center text-muted-foreground">
            No deals currently in the pipeline.
          </div>
        )}
      </div>

      <DealDialog open={dialogOpen} onOpenChange={setDialogOpen} deal={editingDeal} />
    </AppLayout>
  );
}
