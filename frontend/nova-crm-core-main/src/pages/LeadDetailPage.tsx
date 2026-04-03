import { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { AppLayout } from "@/components/AppLayout";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ArrowLeft, Pencil, RefreshCw, User, Tag, DollarSign, Globe } from "lucide-react";
import { leadsApi } from "@/api/leads.api";
import { contactsApi } from "@/api/contacts.api";
import { dealsApi } from "@/api/deals.api";
import { EntityTimeline } from "@/components/EntityTimeline";
import { NotesPanel } from "@/components/NotesPanel";
import { LeadDialog } from "@/components/dialogs/LeadDialog";
import { LeadConvertDialog } from "@/components/dialogs/LeadConvertDialog";

export default function LeadDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [dialogOpen, setDialogOpen] = useState(false);
  const [convertOpen, setConvertOpen] = useState(false);

  const { data: lead, isLoading: leadLoading } = useQuery({
    queryKey: ["leads", id],
    queryFn: () => leadsApi.get(id!),
    enabled: !!id,
  });

  const { data: contact } = useQuery({
    queryKey: ["contacts", lead?.contact_id],
    queryFn: () => contactsApi.get(lead!.contact_id),
    enabled: !!lead?.contact_id,
  });

  const { data: deals } = useQuery({
    queryKey: ["deals", "lead", id],
    queryFn: () => dealsApi.list({ lead_id: id }),
    enabled: !!id,
  });

  if (leadLoading) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center h-[50vh]">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
        </div>
      </AppLayout>
    );
  }

  if (!lead) {
    return (
      <AppLayout>
        <div className="text-center py-12">
          <h2 className="text-xl font-semibold mb-2">Lead not found</h2>
          <Button variant="outline" onClick={() => navigate("/leads")}>Back to Leads</Button>
        </div>
      </AppLayout>
    );
  }

  const isWon = lead.status === "qualified";
  const isLost = lead.status === "lost";

  return (
    <AppLayout>
      <div className="mb-6">
        <Button variant="ghost" size="sm" onClick={() => navigate("/leads")} className="mb-4 -ml-2 text-muted-foreground">
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Leads
        </Button>
        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <h1 className="text-3xl font-display font-bold text-foreground">{lead.title}</h1>
              <Badge variant={isWon ? "default" : isLost ? "destructive" : "secondary"} className="capitalize">
                {lead.status}
              </Badge>
              <Badge variant="outline" className="capitalize">
                {lead.priority} Priority
              </Badge>
            </div>
            
            <div className="flex items-center gap-4 mt-3 text-sm text-muted-foreground">
              {contact && (
                <button
                  className="flex items-center gap-1.5 hover:text-primary transition-colors cursor-pointer"
                  onClick={() => navigate(`/contacts/${contact.id}`)}
                >
                  <User className="h-4 w-4" />{contact.name}
                </button>
              )}
              {lead.estimated_value ? (
                <span className="flex items-center gap-1.5 font-medium text-foreground">
                  <DollarSign className="h-4 w-4 text-muted-foreground" />${lead.estimated_value}
                </span>
              ) : null}
              {lead.source && (
                <span className="flex items-center gap-1.5 capitalize">
                  <Globe className="h-4 w-4" />{lead.source}
                </span>
              )}
            </div>
          </div>
          
          <div className="flex gap-2">
            {lead.status !== "qualified" && lead.status !== "lost" && (
              <Button variant="outline" onClick={() => setConvertOpen(true)}>
                <RefreshCw className="h-4 w-4 mr-2" />
                Convert
              </Button>
            )}
            <Button onClick={() => setDialogOpen(true)}>
              <Pencil className="h-4 w-4 mr-2" />
              Edit
            </Button>
          </div>
        </div>

        {lead.tags && lead.tags.length > 0 && (
          <div className="flex items-center gap-2 mt-4 pt-4 border-t border-border">
            <Tag className="h-3.5 w-3.5 text-muted-foreground" />
            <div className="flex gap-1.5">
              {lead.tags.map(t => <Badge key={t} variant="secondary" className="text-xs">{t}</Badge>)}
            </div>
          </div>
        )}
      </div>

      <Tabs defaultValue="timeline" className="w-full mt-8 border rounded-lg bg-card overflow-hidden">
        <div className="border-b border-border bg-secondary/20 px-4 pt-4">
          <TabsList className="bg-transparent h-auto p-0 mb-[-1px] space-x-6">
            <TabsTrigger value="timeline" className="rounded-none border-b-2 border-transparent data-[state=active]:border-primary data-[state=active]:bg-transparent px-2 pb-3 pt-2">Timeline</TabsTrigger>
            <TabsTrigger value="notes" className="rounded-none border-b-2 border-transparent data-[state=active]:border-primary data-[state=active]:bg-transparent px-2 pb-3 pt-2">Notes</TabsTrigger>
            <TabsTrigger value="deals" className="rounded-none border-b-2 border-transparent data-[state=active]:border-primary data-[state=active]:bg-transparent px-2 pb-3 pt-2">
              Linked Deals <Badge variant="secondary" className="ml-2 bg-background/50">{deals?.total || 0}</Badge>
            </TabsTrigger>
          </TabsList>
        </div>
        
        <div className="p-6">
          <TabsContent value="timeline" className="m-0 focus-visible:outline-none">
            <EntityTimeline entityType="lead" entityId={id!} />
          </TabsContent>
          
          <TabsContent value="notes" className="m-0 focus-visible:outline-none">
            <NotesPanel entityType="lead" entityId={id!} />
          </TabsContent>
          
          <TabsContent value="deals" className="m-0 focus-visible:outline-none">
            <div className="space-y-3">
              {deals?.items.map(deal => (
                <div key={deal.id} className="p-4 border border-border rounded-md cursor-pointer hover:border-primary/50 transition-colors" onClick={() => navigate(`/deals/${deal.id}`)}>
                  <div className="flex justify-between items-start">
                    <div>
                      <h4 className="font-semibold text-foreground">{deal.title}</h4>
                      <p className="text-sm text-muted-foreground mt-1">Value: ${deal.value}</p>
                    </div>
                    <Badge variant="outline" className="capitalize">{deal.stage}</Badge>
                  </div>
                </div>
              ))}
              {!deals?.items?.length && (
                <p className="text-sm text-muted-foreground py-4">No deals converted from this lead yet.</p>
              )}
            </div>
          </TabsContent>
        </div>
      </Tabs>

      <LeadDialog open={dialogOpen} onOpenChange={setDialogOpen} lead={lead} />
      <LeadConvertDialog open={convertOpen} onOpenChange={setConvertOpen} leadId={id!} />
    </AppLayout>
  );
}
