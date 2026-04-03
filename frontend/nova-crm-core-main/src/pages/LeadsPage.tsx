import { useQuery } from "@tanstack/react-query";
import { AppLayout } from "@/components/AppLayout";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Plus, ArrowRight, Target } from "lucide-react";
import { leadsApi } from "@/api/leads.api";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { LeadDialog } from "@/components/dialogs/LeadDialog";
import { LeadConvertDialog } from "@/components/dialogs/LeadConvertDialog";

const statusColors: Record<string, string> = {
  new: "bg-info/10 text-info",
  contacted: "bg-warning/10 text-warning",
  qualified: "bg-success/10 text-success",
  lost: "bg-destructive/10 text-destructive",
};

const priorityColors: Record<string, string> = {
  high: "text-destructive font-bold",
  medium: "text-warning",
  low: "text-muted-foreground",
};

export default function LeadsPage() {
  const [search, setSearch] = useState("");
  const navigate = useNavigate();
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingLead, setEditingLead] = useState<any>(null);
  const [convertLeadId, setConvertLeadId] = useState<string | null>(null);

  const { data, isLoading } = useQuery({
    queryKey: ["leads"],
    queryFn: () => leadsApi.list(),
  });

  if (isLoading) {
    return (
      <AppLayout>
        <div className="mb-6">
          <div className="h-7 w-24 bg-secondary rounded animate-pulse" />
          <div className="h-4 w-56 bg-secondary/60 rounded animate-pulse mt-2" />
        </div>
        <div className="bg-card rounded-lg border border-border overflow-hidden">
          <div className="border-b border-border bg-secondary/50 px-5 py-3 flex gap-8">
            {[1, 2, 3, 4, 5, 6].map(i => <div key={i} className="h-3 w-16 bg-secondary rounded animate-pulse" />)}
          </div>
          {[1, 2, 3, 4].map(i => (
            <div key={i} className="px-5 py-4 border-b border-border flex items-center gap-6 animate-pulse">
              <div className="h-4 w-32 bg-secondary rounded" />
              <div className="h-5 w-16 bg-secondary rounded-full" />
              <div className="h-3 w-12 bg-secondary/60 rounded" />
              <div className="flex-1" />
              <div className="h-3 w-20 bg-secondary/60 rounded" />
            </div>
          ))}
        </div>
      </AppLayout>
    );
  }

  const leads = data?.items || [];

  return (
    <AppLayout>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-display font-bold text-foreground">Leads</h1>
          <p className="text-sm text-muted-foreground mt-1">Track and convert your sales pipeline</p>
        </div>
        <Button onClick={() => { setEditingLead(null); setDialogOpen(true); }}>
          <Plus className="h-4 w-4 mr-2" />
          New Lead
        </Button>
      </div>

      <div className="bg-card rounded-lg border border-border overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="border-b border-border bg-secondary/50">
              <th className="text-left px-5 py-3 text-xs font-semibold text-muted-foreground uppercase tracking-wider">Lead</th>
              <th className="text-left px-5 py-3 text-xs font-semibold text-muted-foreground uppercase tracking-wider">Status</th>
              <th className="text-left px-5 py-3 text-xs font-semibold text-muted-foreground uppercase tracking-wider">Priority</th>
              <th className="text-left px-5 py-3 text-xs font-semibold text-muted-foreground uppercase tracking-wider">Source</th>
              <th className="text-left px-5 py-3 text-xs font-semibold text-muted-foreground uppercase tracking-wider">Value</th>
              <th className="text-left px-5 py-3 text-xs font-semibold text-muted-foreground uppercase tracking-wider">Created</th>
              <th className="px-5 py-3"></th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {leads.map((lead) => (
              <tr key={lead.id} className="hover:bg-secondary/30 transition-colors cursor-pointer" onClick={() => navigate(`/leads/${lead.id}`)}>
                <td className="px-5 py-3 text-sm font-medium text-foreground">{lead.title}</td>
                <td className="px-5 py-3">
                  <Badge variant="secondary" className={`${statusColors[lead.status]} border-none text-xs capitalize`}>
                    {lead.status}
                  </Badge>
                </td>
                <td className="px-5 py-3">
                  <span className={`text-xs font-medium capitalize ${priorityColors[lead.priority]}`}>
                    {lead.priority}
                  </span>
                </td>
                <td className="px-5 py-3 text-xs text-muted-foreground">{lead.source}</td>
                <td className="px-5 py-3 text-xs text-foreground">
                  {lead.estimated_value ? `$${Number(lead.estimated_value).toLocaleString()}` : "-"}
                </td>
                <td className="px-5 py-3 text-xs text-muted-foreground">
                  {new Date(lead.created_at).toLocaleDateString()}
                </td>
                <td className="px-5 py-3">
                  {lead.status !== "lost" && (
                    <Button
                      variant="ghost"
                      size="sm"
                      className="text-xs"
                      onClick={(e) => { e.stopPropagation(); setConvertLeadId(lead.id); }}
                    >
                      Convert <ArrowRight className="h-3 w-3 ml-1" />
                    </Button>
                  )}
                </td>
              </tr>
            ))}
            {leads.length === 0 && (
              <tr>
                <td colSpan={7} className="px-5 py-16 text-center">
                  <Target className="h-10 w-10 text-muted-foreground mx-auto mb-3 opacity-40" />
                  <p className="text-sm font-semibold text-foreground">No leads yet</p>
                  <p className="text-sm text-muted-foreground mt-1 mb-4">Create your first lead to start tracking your pipeline.</p>
                  <Button size="sm" onClick={() => { setEditingLead(null); setDialogOpen(true); }}>
                    <Plus className="h-4 w-4 mr-2" />New Lead
                  </Button>
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      <LeadDialog open={dialogOpen} onOpenChange={setDialogOpen} lead={editingLead} />
      {convertLeadId && (
        <LeadConvertDialog open={!!convertLeadId} onOpenChange={() => setConvertLeadId(null)} leadId={convertLeadId} />
      )}
    </AppLayout>
  );
}
