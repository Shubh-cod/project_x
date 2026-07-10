import { useQuery } from "@tanstack/react-query";
import { AppLayout } from "@/components/AppLayout";
import { PageHeader } from "@/components/shared/PageHeader";
import { PageSkeleton } from "@/components/shared/PageSkeleton";
import { EmptyState } from "@/components/shared/EmptyState";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Plus, ArrowRight, Target, Search } from "lucide-react";
import { leadsApi } from "@/api/leads.api";
import { useState, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import { LeadDialog } from "@/components/dialogs/LeadDialog";
import { LeadConvertDialog } from "@/components/dialogs/LeadConvertDialog";
import { formatCurrency } from "@/lib/utils";

const statusColors: Record<string, string> = {
  new: "bg-info/10 text-info border-info/20",
  contacted: "bg-warning/10 text-warning border-warning/20",
  qualified: "bg-success/10 text-success border-success/20",
  lost: "bg-destructive/10 text-destructive border-destructive/20",
};

const priorityColors: Record<string, string> = {
  high: "text-destructive font-semibold",
  medium: "text-warning font-medium",
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

  const leads = data?.items || [];
  const filtered = useMemo(() => {
    if (!search.trim()) return leads;
    const q = search.toLowerCase();
    return leads.filter(
      (l) =>
        l.title.toLowerCase().includes(q) ||
        l.source?.toLowerCase().includes(q) ||
        l.status.toLowerCase().includes(q)
    );
  }, [leads, search]);

  if (isLoading) {
    return <AppLayout><PageSkeleton columns={7} /></AppLayout>;
  }

  return (
    <AppLayout>
      <PageHeader
        icon={Target}
        title="Leads"
        description={`${leads.length} leads in your pipeline`}
        action={
          <Button onClick={() => { setEditingLead(null); setDialogOpen(true); }}>
            <Plus className="h-4 w-4 mr-2" />New Lead
          </Button>
        }
      />

      <div className="relative max-w-sm mb-5">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <Input
          placeholder="Search leads..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="pl-9 h-9"
        />
      </div>

      <div className="data-card overflow-hidden">
        {filtered.length === 0 ? (
          <EmptyState
            icon={Target}
            title={search ? "No leads found" : "No leads yet"}
            description={search ? "Try a different search term." : "Create your first lead to start tracking your pipeline."}
            action={
              !search && (
                <Button size="sm" onClick={() => { setEditingLead(null); setDialogOpen(true); }}>
                  <Plus className="h-4 w-4 mr-2" />New Lead
                </Button>
              )
            }
          />
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>Lead</th>
                <th>Status</th>
                <th>Priority</th>
                <th>Source</th>
                <th>Value</th>
                <th>Created</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((lead) => (
                <tr key={lead.id} className="cursor-pointer" onClick={() => navigate(`/leads/${lead.id}`)}>
                  <td className="font-medium">{lead.title}</td>
                  <td>
                    <Badge variant="outline" className={`${statusColors[lead.status]} text-xs capitalize border`}>
                      {lead.status}
                    </Badge>
                  </td>
                  <td>
                    <span className={`text-xs capitalize ${priorityColors[lead.priority]}`}>{lead.priority}</span>
                  </td>
                  <td className="text-xs text-muted-foreground">{lead.source || "—"}</td>
                  <td className="text-xs tabular-nums">
                    {lead.estimated_value ? formatCurrency(Number(lead.estimated_value)) : "—"}
                  </td>
                  <td className="text-xs text-muted-foreground tabular-nums">
                    {new Date(lead.created_at).toLocaleDateString()}
                  </td>
                  <td>
                    {lead.status !== "lost" && (
                      <Button
                        variant="ghost"
                        size="sm"
                        className="text-xs h-7"
                        onClick={(e) => { e.stopPropagation(); setConvertLeadId(lead.id); }}
                      >
                        Convert <ArrowRight className="h-3 w-3 ml-1" />
                      </Button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      <LeadDialog open={dialogOpen} onOpenChange={setDialogOpen} lead={editingLead} />
      {convertLeadId && (
        <LeadConvertDialog open={!!convertLeadId} onOpenChange={() => setConvertLeadId(null)} leadId={convertLeadId} />
      )}
    </AppLayout>
  );
}
