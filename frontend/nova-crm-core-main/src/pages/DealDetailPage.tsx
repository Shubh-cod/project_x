import { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { AppLayout } from "@/components/AppLayout";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ArrowLeft, Pencil, User, DollarSign, Calendar, Percent } from "lucide-react";
import { dealsApi } from "@/api/deals.api";
import { contactsApi } from "@/api/contacts.api";
import { EntityTimeline } from "@/components/EntityTimeline";
import { NotesPanel } from "@/components/NotesPanel";
import { DealDialog } from "@/components/dialogs/DealDialog";

export default function DealDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [dialogOpen, setDialogOpen] = useState(false);

  const { data: deal, isLoading: dealLoading } = useQuery({
    queryKey: ["deals", id],
    queryFn: () => dealsApi.get(id!),
    enabled: !!id,
  });

  const { data: contact } = useQuery({
    queryKey: ["contacts", deal?.contact_id],
    queryFn: () => contactsApi.get(deal!.contact_id),
    enabled: !!deal?.contact_id,
  });

  if (dealLoading) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center h-[50vh]">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
        </div>
      </AppLayout>
    );
  }

  if (!deal) {
    return (
      <AppLayout>
        <div className="text-center py-12">
          <h2 className="text-xl font-semibold mb-2">Deal not found</h2>
          <Button variant="outline" onClick={() => navigate("/deals")}>Back to Deals</Button>
        </div>
      </AppLayout>
    );
  }

  const isWon = deal.stage === "won";
  const isLost = deal.stage === "lost";

  return (
    <AppLayout>
      <div className="mb-6">
        <Button variant="ghost" size="sm" onClick={() => navigate("/deals")} className="mb-4 -ml-2 text-muted-foreground">
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Deals
        </Button>
        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <h1 className="text-3xl font-display font-bold text-foreground">{deal.title}</h1>
              <Badge variant={isWon ? "default" : isLost ? "destructive" : "secondary"} className="capitalize">
                {deal.stage}
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
              <span className="flex items-center gap-1.5 font-medium text-foreground">
                <DollarSign className="h-4 w-4 text-muted-foreground" />
                {deal.value} {deal.currency}
              </span>
              {deal.probability ? (
                <span className="flex items-center gap-1.5">
                  <Percent className="h-4 w-4" />{deal.probability}% Prob
                </span>
              ) : null}
              {deal.close_date && (
                <span className="flex items-center gap-1.5">
                  <Calendar className="h-4 w-4" />
                  Close: {new Date(deal.close_date).toLocaleDateString()}
                </span>
              )}
            </div>
          </div>
          
          <Button onClick={() => setDialogOpen(true)}>
            <Pencil className="h-4 w-4 mr-2" />
            Edit
          </Button>
        </div>
      </div>

      <Tabs defaultValue="timeline" className="w-full mt-8 border rounded-lg bg-card overflow-hidden">
        <div className="border-b border-border bg-secondary/20 px-4 pt-4">
          <TabsList className="bg-transparent h-auto p-0 mb-[-1px] space-x-6">
            <TabsTrigger value="timeline" className="rounded-none border-b-2 border-transparent data-[state=active]:border-primary data-[state=active]:bg-transparent px-2 pb-3 pt-2">Timeline</TabsTrigger>
            <TabsTrigger value="notes" className="rounded-none border-b-2 border-transparent data-[state=active]:border-primary data-[state=active]:bg-transparent px-2 pb-3 pt-2">Notes</TabsTrigger>
          </TabsList>
        </div>
        
        <div className="p-6">
          <TabsContent value="timeline" className="m-0 focus-visible:outline-none">
            <EntityTimeline entityType="deal" entityId={id!} />
          </TabsContent>
          <TabsContent value="notes" className="m-0 focus-visible:outline-none">
            <NotesPanel entityType="deal" entityId={id!} />
          </TabsContent>
        </div>
      </Tabs>

      <DealDialog open={dialogOpen} onOpenChange={setDialogOpen} deal={deal} />
    </AppLayout>
  );
}
