import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { leadsApi } from "@/api/leads.api";

interface LeadConvertDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  leadId: string;
}

export function LeadConvertDialog({ open, onOpenChange, leadId }: LeadConvertDialogProps) {
  const queryClient = useQueryClient();
  const [createDeal, setCreateDeal] = useState(true);
  const [dealTitle, setDealTitle] = useState("");
  const [dealValue, setDealValue] = useState("");

  const mutation = useMutation({
    mutationFn: () =>
      leadsApi.convert(leadId, {
        create_deal: createDeal,
        deal_title: dealTitle || undefined,
        deal_value: dealValue ? parseFloat(dealValue) : undefined,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["leads"] });
      queryClient.invalidateQueries({ queryKey: ["contacts"] });
      queryClient.invalidateQueries({ queryKey: ["deals"] });
      onOpenChange(false);
    },
  });

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-sm">
        <DialogHeader>
          <DialogTitle>Convert Lead</DialogTitle>
        </DialogHeader>
        <div className="space-y-3">
          <p className="text-sm text-muted-foreground">
            This will convert the lead into a contact. Optionally create a deal as well.
          </p>
          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={createDeal}
              onChange={(e) => setCreateDeal(e.target.checked)}
              className="rounded border-input"
            />
            Also create a deal
          </label>
          {createDeal && (
            <>
              <div>
                <label className="text-sm font-medium mb-1 block">Deal Title</label>
                <Input value={dealTitle} onChange={(e) => setDealTitle(e.target.value)} />
              </div>
              <div>
                <label className="text-sm font-medium mb-1 block">Deal Value</label>
                <Input type="number" value={dealValue} onChange={(e) => setDealValue(e.target.value)} placeholder="$" />
              </div>
            </>
          )}
          {mutation.error && (
            <p className="text-sm text-destructive">{(mutation.error as Error).message}</p>
          )}
          <div className="flex justify-end gap-2 pt-2">
            <Button variant="outline" onClick={() => onOpenChange(false)}>Cancel</Button>
            <Button onClick={() => mutation.mutate()} disabled={mutation.isPending}>
              {mutation.isPending ? "Converting..." : "Convert"}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
