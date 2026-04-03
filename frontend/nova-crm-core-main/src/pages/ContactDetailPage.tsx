import { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { AppLayout } from "@/components/AppLayout";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ArrowLeft, Pencil, Mail, Phone, Building, Globe, Tag } from "lucide-react";
import { contactsApi } from "@/api/contacts.api";
import { leadsApi } from "@/api/leads.api";
import { dealsApi } from "@/api/deals.api";
import { EntityTimeline } from "@/components/EntityTimeline";
import { NotesPanel } from "@/components/NotesPanel";
import { ContactDialog } from "@/components/dialogs/ContactDialog";

export default function ContactDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [dialogOpen, setDialogOpen] = useState(false);

  const { data: contact, isLoading } = useQuery({
    queryKey: ["contacts", id],
    queryFn: () => contactsApi.get(id!),
    enabled: !!id,
  });

  const { data: leads } = useQuery({
    queryKey: ["leads", "contact", id],
    queryFn: () => leadsApi.list({ contact_id: id }),
    enabled: !!id,
  });

  const { data: deals } = useQuery({
    queryKey: ["deals", "contact", id],
    queryFn: () => dealsApi.list({ contact_id: id }),
    enabled: !!id,
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

  if (!contact) {
    return (
      <AppLayout>
        <div className="text-center py-12">
          <h2 className="text-xl font-semibold mb-2">Contact not found</h2>
          <Button variant="outline" onClick={() => navigate("/contacts")}>Back to Contacts</Button>
        </div>
      </AppLayout>
    );
  }

  return (
    <AppLayout>
      <div className="mb-6">
        <Button variant="ghost" size="sm" onClick={() => navigate("/contacts")} className="mb-4 -ml-2 text-muted-foreground">
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Contacts
        </Button>
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-4">
            <div className="h-16 w-16 rounded-full bg-primary/10 flex items-center justify-center text-2xl font-bold text-primary">
              {contact.name.split(" ").map(n => n[0]).join("")}
            </div>
            <div>
              <h1 className="text-3xl font-display font-bold text-foreground">{contact.name}</h1>
              <div className="flex items-center gap-4 mt-2 text-sm text-muted-foreground">
                <span className="flex items-center gap-1.5"><Mail className="h-4 w-4" />{contact.email}</span>
                {contact.phone && <span className="flex items-center gap-1.5"><Phone className="h-4 w-4" />{contact.phone}</span>}
                {contact.company && <span className="flex items-center gap-1.5"><Building className="h-4 w-4" />{contact.company}</span>}
              </div>
            </div>
          </div>
          <Button onClick={() => setDialogOpen(true)}>
            <Pencil className="h-4 w-4 mr-2" />
            Edit
          </Button>
        </div>

        <div className="flex items-center gap-6 mt-6 pt-6 border-t border-border">
          {contact.source && (
            <div className="flex flex-col">
              <span className="text-xs text-muted-foreground flex items-center gap-1.5 mb-1"><Globe className="h-3 w-3" />Source</span>
              <span className="text-sm font-medium capitalize">{contact.source}</span>
            </div>
          )}
          {contact.tags && contact.tags.length > 0 && (
            <div className="flex flex-col">
              <span className="text-xs text-muted-foreground flex items-center gap-1.5 mb-1"><Tag className="h-3 w-3" />Tags</span>
              <div className="flex gap-1">
                {contact.tags.map(t => <Badge key={t} variant="secondary" className="text-xs">{t}</Badge>)}
              </div>
            </div>
          )}
        </div>
      </div>

      <Tabs defaultValue="timeline" className="w-full mt-8 border rounded-lg bg-card overflow-hidden">
        <div className="border-b border-border bg-secondary/20 px-4 pt-4">
          <TabsList className="bg-transparent h-auto p-0 mb-[-1px] space-x-6">
            <TabsTrigger value="timeline" className="rounded-none border-b-2 border-transparent data-[state=active]:border-primary data-[state=active]:bg-transparent px-2 pb-3 pt-2">Timeline</TabsTrigger>
            <TabsTrigger value="notes" className="rounded-none border-b-2 border-transparent data-[state=active]:border-primary data-[state=active]:bg-transparent px-2 pb-3 pt-2">Notes</TabsTrigger>
            <TabsTrigger value="leads" className="rounded-none border-b-2 border-transparent data-[state=active]:border-primary data-[state=active]:bg-transparent px-2 pb-3 pt-2">
              Leads <Badge variant="secondary" className="ml-2 bg-background/50">{leads?.total || 0}</Badge>
            </TabsTrigger>
            <TabsTrigger value="deals" className="rounded-none border-b-2 border-transparent data-[state=active]:border-primary data-[state=active]:bg-transparent px-2 pb-3 pt-2">
              Deals <Badge variant="secondary" className="ml-2 bg-background/50">{deals?.total || 0}</Badge>
            </TabsTrigger>
          </TabsList>
        </div>
        
        <div className="p-6">
          <TabsContent value="timeline" className="m-0 focus-visible:outline-none">
            <EntityTimeline entityType="contact" entityId={id!} />
          </TabsContent>
          <TabsContent value="notes" className="m-0 focus-visible:outline-none">
            <NotesPanel entityType="contact" entityId={id!} />
          </TabsContent>
          <TabsContent value="leads" className="m-0 focus-visible:outline-none">
            <div className="space-y-3">
              {leads?.items.map(lead => (
                <div key={lead.id} className="p-4 border border-border rounded-md cursor-pointer hover:border-primary/50 transition-colors" onClick={() => navigate(`/leads/${lead.id}`)}>
                  <div className="flex justify-between items-start">
                    <div>
                      <h4 className="font-semibold text-foreground">{lead.title}</h4>
                      <p className="text-sm text-muted-foreground mt-1">Value: ${lead.estimated_value || 0}</p>
                    </div>
                    <Badge variant={lead.status === "qualified" ? "default" : "secondary"}>{lead.status}</Badge>
                  </div>
                </div>
              ))}
              {!leads?.items.length && <p className="text-sm text-muted-foreground py-4">No leads attached.</p>}
            </div>
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
              {!deals?.items.length && <p className="text-sm text-muted-foreground py-4">No deals attached.</p>}
            </div>
          </TabsContent>
        </div>
      </Tabs>

      <ContactDialog open={dialogOpen} onOpenChange={setDialogOpen} contact={contact} />
    </AppLayout>
  );
}
