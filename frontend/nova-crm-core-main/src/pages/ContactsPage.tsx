import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { AppLayout } from "@/components/AppLayout";
import { PageHeader } from "@/components/shared/PageHeader";
import { PageSkeleton } from "@/components/shared/PageSkeleton";
import { EmptyState } from "@/components/shared/EmptyState";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Plus, Search, Mail, Phone, Trash2, Users, Upload } from "lucide-react";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { contactsApi } from "@/api/contacts.api";
import { useDebounce } from "@/hooks/use-debounce";
import { ContactDialog } from "@/components/dialogs/ContactDialog";
import { DeleteContactDialog } from "@/components/dialogs/DeleteContactDialog";
import { ImportCSVDialog } from "@/components/dialogs/ImportCSVDialog";
import { getInitials } from "@/lib/utils";

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
    onError: (error) => toast.error(error.message || "Failed to delete contact"),
  });

  if (isLoading) {
    return <AppLayout><PageSkeleton /></AppLayout>;
  }

  const contacts = data?.items || [];
  const total = data?.total || 0;

  return (
    <AppLayout>
      <PageHeader
        icon={Users}
        title="Contacts"
        description={`${total.toLocaleString()} contacts in your workspace`}
        action={
          <>
            <Button variant="outline" onClick={() => setImportDialogOpen(true)}>
              <Upload className="h-4 w-4 mr-2" />Import
            </Button>
            <Button onClick={() => { setEditingContact(null); setDialogOpen(true); }}>
              <Plus className="h-4 w-4 mr-2" />Add Contact
            </Button>
          </>
        }
      />

      <div className="relative max-w-sm mb-5">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <Input
          placeholder="Search by name..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="pl-9 h-9"
        />
      </div>

      <div className="data-card overflow-hidden">
        {contacts.length === 0 ? (
          <EmptyState
            icon={Users}
            title={search ? "No contacts found" : "No contacts yet"}
            description={search ? "Try adjusting your search terms." : "Add your first contact to start building relationships."}
            action={
              !search && (
                <Button size="sm" onClick={() => { setEditingContact(null); setDialogOpen(true); }}>
                  <Plus className="h-4 w-4 mr-2" />Add Contact
                </Button>
              )
            }
          />
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Contact</th>
                <th>Company</th>
                <th>Tags</th>
                <th>Added</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {contacts.map((c) => (
                <tr key={c.id} className="cursor-pointer" onClick={() => navigate(`/contacts/${c.id}`)}>
                  <td>
                    <div className="flex items-center gap-3">
                      <Avatar className="h-8 w-8">
                        <AvatarFallback className="bg-primary/10 text-primary text-xs font-semibold">
                          {getInitials(c.name)}
                        </AvatarFallback>
                      </Avatar>
                      <span className="font-medium">{c.name}</span>
                    </div>
                  </td>
                  <td>
                    <div className="space-y-0.5">
                      <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
                        <Mail className="h-3 w-3 shrink-0" />{c.email}
                      </div>
                      {c.phone && (
                        <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
                          <Phone className="h-3 w-3 shrink-0" />{c.phone}
                        </div>
                      )}
                    </div>
                  </td>
                  <td className="text-foreground">{c.company || "—"}</td>
                  <td>
                    <div className="flex gap-1 flex-wrap">
                      {c.tags?.map((t) => (
                        <Badge key={t} variant="secondary" className="text-xs">{t}</Badge>
                      ))}
                    </div>
                  </td>
                  <td className="text-xs text-muted-foreground tabular-nums">
                    {new Date(c.created_at).toLocaleDateString()}
                  </td>
                  <td>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-8 w-8"
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
            </tbody>
          </table>
        )}
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
