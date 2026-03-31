import { useState, useEffect } from "react";
import { toast } from "sonner";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { dealsApi } from "@/api/deals.api";
import { ContactPicker } from "@/components/ContactPicker";
import type { Deal } from "@/api/types";

interface DealDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  deal?: Deal | null;
}

export function DealDialog({ open, onOpenChange, deal }: DealDialogProps) {
  const queryClient = useQueryClient();
  const isEditing = !!deal;

  const [form, setForm] = useState({
    title: deal?.title || "",
    contact_id: deal?.contact_id || "",
    stage: deal?.stage || "prospect",
    value: deal?.value?.toString() || "0",
    currency: deal?.currency || "USD",
    close_date: deal?.close_date || "",
    probability: deal?.probability?.toString() || "",
    notes: deal?.notes || "",
  });

  useEffect(() => {
    if (open) {
      setForm({
        title: deal?.title || "",
        contact_id: deal?.contact_id || "",
        stage: deal?.stage || "prospect",
        value: deal?.value?.toString() || "0",
        currency: deal?.currency || "USD",
        close_date: deal?.close_date || "",
        probability: deal?.probability?.toString() || "",
        notes: deal?.notes || "",
      });
    }
  }, [open, deal]);

  const mutation = useMutation({
    mutationFn: (data: any) =>
      isEditing ? dealsApi.update(deal!.id, data) : dealsApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["deals"] });
      queryClient.invalidateQueries({ queryKey: ["deals-pipeline"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
      toast.success(isEditing ? "Deal updated" : "Deal created");
      onOpenChange(false);
    },
    onError: (error) => {
      toast.error(error.message || "Failed to save deal");
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const payload: any = { ...form };
    payload.value = parseFloat(payload.value) || 0;
    if (payload.probability) payload.probability = parseInt(payload.probability);
    else delete payload.probability;
    if (!payload.close_date) delete payload.close_date;
    mutation.mutate(payload);
  };

  const update = (key: string, value: string) => setForm((f) => ({ ...f, [key]: value }));

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>{isEditing ? "Edit Deal" : "New Deal"}</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-3">
          <div>
            <label className="text-sm font-medium mb-1 block">Title *</label>
            <Input value={form.title} onChange={(e) => update("title", e.target.value)} required />
          </div>
          <div>
            <label className="text-sm font-medium mb-1 block">Contact *</label>
            <ContactPicker value={form.contact_id} onChange={(id) => update("contact_id", id)} />
          </div>
          <div className="grid grid-cols-3 gap-3">
            <div>
              <label className="text-sm font-medium mb-1 block">Stage</label>
              <select className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm" value={form.stage} onChange={(e) => update("stage", e.target.value)}>
                <option value="prospect">Prospect</option>
                <option value="proposal">Proposal</option>
                <option value="negotiation">Negotiation</option>
                <option value="won">Won</option>
                <option value="lost">Lost</option>
              </select>
            </div>
            <div>
              <label className="text-sm font-medium mb-1 block">Value ($)</label>
              <Input type="number" value={form.value} onChange={(e) => update("value", e.target.value)} />
            </div>
            <div>
              <label className="text-sm font-medium mb-1 block">Probability %</label>
              <Input type="number" min="0" max="100" value={form.probability} onChange={(e) => update("probability", e.target.value)} />
            </div>
          </div>
          <div>
            <label className="text-sm font-medium mb-1 block">Close Date</label>
            <Input type="date" value={form.close_date} onChange={(e) => update("close_date", e.target.value)} />
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
