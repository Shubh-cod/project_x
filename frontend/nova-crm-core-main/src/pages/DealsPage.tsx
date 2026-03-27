import { useQuery } from "@tanstack/react-query";
import { AppLayout } from "@/components/AppLayout";
import { DollarSign } from "lucide-react";
import { dealsApi } from "@/api/deals.api";

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
  const { data, isLoading, error } = useQuery({
    queryKey: ["deals-pipeline"],
    queryFn: () => dealsApi.getPipeline(),
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

  const pipelineStages = data?.stages || [];

  return (
    <AppLayout>
      <div className="mb-6">
        <h1 className="text-2xl font-display font-bold text-foreground">Deals Pipeline</h1>
        <p className="text-sm text-muted-foreground mt-1">Visual overview of your sales pipeline</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {pipelineStages.map((stage: any) => (
          <div key={stage.stage} className={`bg-card rounded-lg border border-border border-t-4 ${STAGE_COLORS[stage.stage.toLowerCase()] || 'border-t-muted'}`}>
            <div className="px-4 py-3 border-b border-border">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-semibold text-foreground capitalize">{stage.stage}</h3>
                <span className="text-xs text-muted-foreground">{stage.count}</span>
              </div>
              <p className="text-xs text-muted-foreground mt-0.5">{formatCurrency(stage.total_value)}</p>
            </div>
            <div className="p-3 space-y-2">
              {/* Backend returns stages with count/value, details might need separate query or be included in expanded response */}
              {/* For now, displaying summary as per backend getPipeline response */}
              <div className="p-4 text-center text-xs text-muted-foreground italic bg-secondary/20 rounded-md">
                 Summary data for {stage.stage}
              </div>
            </div>
          </div>
        ))}
        {pipelineStages.length === 0 && (
          <div className="col-span-full py-12 text-center text-muted-foreground">
            No deals currently in the pipeline.
          </div>
        )}
      </div>
    </AppLayout>
  );
}
