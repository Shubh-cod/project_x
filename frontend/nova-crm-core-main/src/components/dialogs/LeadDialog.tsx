import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { leadsApi } from "@/api/leads.api";
import type { Lead } from "@/api/types";

interface LeadDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  lead?: Lead | null;
}

export function LeadDialog({ open, onOpenChange, lead }: LeadDialogProps) {
  const queryClient = useQueryClient();
  const isEditing = !!lead;

  const [form, setForm] = useState({
    title: lead?.title || "",
    contact_id: lead?.contact_id || "",
    source: lead?.source || "other",
    status: lead?.status || "new",
    priority: lead?.priority || "medium",
    estimated_value: lead?.estimated_value?.toString() || "",
    notes: lead?.notes || "",
  });

  const mutation = useMutation({
    mutationFn: (data: any) =>
      isEditing ? leadsApi.update(lead!.id, data) : leadsApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["leads"] });
      onOpenChange(false);
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const payload: any = { ...form };
    if (payload.estimated_value) payload.estimated_value = parseFloat(payload.estimated_value);
    else delete payload.estimated_value;
    mutation.mutate(payload);
  };

  const update = (key: string, value: string) => setForm((f) => ({ ...f, [key]: value }));

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>{isEditing ? "Edit Lead" : "New Lead"}</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-3">
          <div>
            <label className="text-sm font-medium mb-1 block">Title *</label>
            <Input value={form.title} onChange={(e) => update("title", e.target.value)} required />
          </div>
          <div>
            <label className="text-sm font-medium mb-1 block">Contact ID *</label>
            <Input value={form.contact_id} onChange={(e) => update("contact_id", e.target.value)} required placeholder="UUID of the contact" />
          </div>
          <div className="grid grid-cols-3 gap-3">
            <div>
              <label className="text-sm font-medium mb-1 block">Status</label>
              <select className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm" value={form.status} onChange={(e) => update("status", e.target.value)}>
                <option value="new">New</option>
                <option value="contacted">Contacted</option>
                <option value="qualified">Qualified</option>
                <option value="lost">Lost</option>
              </select>
            </div>
            <div>
              <label className="text-sm font-medium mb-1 block">Priority</label>
              <select className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm" value={form.priority} onChange={(e) => update("priority", e.target.value)}>
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
              </select>
            </div>
            <div>
              <label className="text-sm font-medium mb-1 block">Value</label>
              <Input type="number" value={form.estimated_value} onChange={(e) => update("estimated_value", e.target.value)} placeholder="$" />
            </div>
          </div>
          <div>
            <label className="text-sm font-medium mb-1 block">Source</label>
            <Input value={form.source} onChange={(e) => update("source", e.target.value)} />
          </div>
          {mutation.error && (
            <p className="text-sm text-destructive">{(mutation.error as Error).message}</p>
          )}
          <div className="flex justify-end gap-2 pt-2">
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>Cancel</Button>
            <Button type="submit" disabled={mutation.isPending}>
              {mutation.isPending ? "Saving..." : isEditing ? "Update" : "Create"}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
