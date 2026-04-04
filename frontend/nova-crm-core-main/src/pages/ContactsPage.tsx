import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { AppLayout } from "@/components/AppLayout";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Plus, Search, Mail, Phone, Trash2, Users, Upload } from "lucide-react";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { contactsApi } from "@/api/contacts.api";
import { useDebounce } from "@/hooks/use-debounce";
import { ContactDialog } from "@/components/dialogs/ContactDialog";
import { DeleteContactDialog } from "@/components/dialogs/DeleteContactDialog";
import { ImportCSVDialog } from "@/components/dialogs/ImportCSVDialog";

export default function ContactsPage() {
  const [search, setSearch] = useState("");
  const navigate = useNavigate();
  const [dialogOpen, setDialogOpen] = useState(false);
  const [importDialogOpen, setImportDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [editingContact, setEditingContact] = useState<any>(null);
  const [contactToDelete, setContactToDelete] = useState<any>(null);
  const debouncedSearch = useDebounce(search, 300);
  const queryClient = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ["contacts", debouncedSearch],
    queryFn: () => contactsApi.list({ name: debouncedSearch || undefined }),
  });

  const deleteMutation = useMutation({
    mutationFn: ({ id, deleteAssociated }: { id: string; deleteAssociated: boolean }) => 
      contactsApi.delete(id, deleteAssociated),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["contacts"] });
      toast.success("Contact deleted");
    },
    onError: (error) => {
      toast.error(error.message || "Failed to delete contact");
    },
  });

  if (isLoading) {
    return (
      <AppLayout>
        <div className="mb-6">
          <div className="h-7 w-32 bg-secondary rounded animate-pulse" />
          <div className="h-4 w-48 bg-secondary/60 rounded animate-pulse mt-2" />
        </div>
        <div className="bg-card rounded-lg border border-border overflow-hidden">
          <div className="border-b border-border bg-secondary/50 px-5 py-3 flex gap-8">
            {[1, 2, 3, 4, 5].map(i => <div key={i} className="h-3 w-16 bg-secondary rounded animate-pulse" />)}
          </div>
          {[1, 2, 3, 4, 5].map(i => (
            <div key={i} className="px-5 py-4 border-b border-border flex items-center gap-4 animate-pulse">
              <div className="h-8 w-8 rounded-full bg-secondary" />
              <div className="flex-1 space-y-2">
                <div className="h-4 w-36 bg-secondary rounded" />
                <div className="h-3 w-24 bg-secondary/60 rounded" />
              </div>
              <div className="h-3 w-20 bg-secondary/60 rounded" />
            </div>
          ))}
        </div>
      </AppLayout>
    );
  }

  const contacts = data?.items || [];
  const total = data?.total || 0;

  return (
    <AppLayout>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-display font-bold text-foreground">Contacts</h1>
          <p className="text-sm text-muted-foreground mt-1">{total} total contacts</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => setImportDialogOpen(true)}>
            <Upload className="h-4 w-4 mr-2" />
            Import
          </Button>
          <Button onClick={() => { setEditingContact(null); setDialogOpen(true); }}>
            <Plus className="h-4 w-4 mr-2" />
            Add Contact
          </Button>
        </div>
      </div>

      <div className="relative max-w-sm mb-4">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <Input placeholder="Search contacts..." value={search} onChange={(e) => setSearch(e.target.value)} className="pl-9" />
      </div>

      <div className="bg-card rounded-lg border border-border overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="border-b border-border bg-secondary/50">
              <th className="text-left px-5 py-3 text-xs font-semibold text-muted-foreground uppercase tracking-wider">Name</th>
              <th className="text-left px-5 py-3 text-xs font-semibold text-muted-foreground uppercase tracking-wider">Contact</th>
              <th className="text-left px-5 py-3 text-xs font-semibold text-muted-foreground uppercase tracking-wider">Company</th>
              <th className="text-left px-5 py-3 text-xs font-semibold text-muted-foreground uppercase tracking-wider">Tags</th>
              <th className="text-left px-5 py-3 text-xs font-semibold text-muted-foreground uppercase tracking-wider">Added</th>
              <th className="px-5 py-3"></th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {contacts.map((c) => (
              <tr key={c.id} className="hover:bg-secondary/30 transition-colors cursor-pointer" onClick={() => navigate(`/contacts/${c.id}`)}>
                <td className="px-5 py-3">
                  <div className="flex items-center gap-3">
                    <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center text-xs font-semibold text-primary">
                      {c.name.split(" ").map((n) => n[0]).join("")}
                    </div>
                    <span className="text-sm font-medium text-foreground">{c.name}</span>
                  </div>
                </td>
                <td className="px-5 py-3">
                  <div className="space-y-1">
                    <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
                      <Mail className="h-3 w-3" />{c.email}
                    </div>
                    {c.phone && (
                      <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
                        <Phone className="h-3 w-3" />{c.phone}
                      </div>
                    )}
                  </div>
                </td>
                <td className="px-5 py-3 text-sm text-foreground">{c.company || "-"}</td>
                <td className="px-5 py-3">
                  <div className="flex gap-1 flex-wrap">
                    {c.tags?.map((t) => (
                      <Badge key={t} variant="secondary" className="text-xs">{t}</Badge>
                    ))}
                  </div>
                </td>
                <td className="px-5 py-3 text-xs text-muted-foreground">
                  {new Date(c.created_at).toLocaleDateString()}
                </td>
                <td className="px-5 py-3">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={(e) => { 
                      e.stopPropagation(); 
                      setContactToDelete(c);
                      setDeleteDialogOpen(true);
                    }}
                  >
                    <Trash2 className="h-3.5 w-3.5 text-destructive" />
                  </Button>
                </td>
              </tr>
            ))}
            {contacts.length === 0 && (
              <tr>
                <td colSpan={6} className="px-5 py-16 text-center">
                  <Users className="h-10 w-10 text-muted-foreground mx-auto mb-3 opacity-40" />
                  <p className="text-sm font-semibold text-foreground">No contacts found</p>
                  <p className="text-sm text-muted-foreground mt-1 mb-4">
                    {search ? "Try adjusting your search terms." : "Add your first contact to get started."}
                  </p>
                  {!search && (
                    <Button size="sm" onClick={() => { setEditingContact(null); setDialogOpen(true); }}>
                      <Plus className="h-4 w-4 mr-2" />Add Contact
                    </Button>
                  )}
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      <ContactDialog open={dialogOpen} onOpenChange={setDialogOpen} contact={editingContact} />
      
      <ImportCSVDialog open={importDialogOpen} onOpenChange={setImportDialogOpen} />

      <DeleteContactDialog 
        open={deleteDialogOpen} 
        onOpenChange={setDeleteDialogOpen}
        contactName={contactToDelete?.name}
        onConfirm={(deleteAssociated) => {
          if (contactToDelete) {
            deleteMutation.mutate({ id: contactToDelete.id, deleteAssociated });
            setDeleteDialogOpen(false);
          }
        }}
      />
    </AppLayout>
  );
}
