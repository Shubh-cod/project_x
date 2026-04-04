import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import { useState, useEffect } from "react";

interface DeleteContactDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onConfirm: (deleteAssociated: boolean) => void;
  contactName?: string;
}

export function DeleteContactDialog({
  open,
  onOpenChange,
  onConfirm,
  contactName,
}: DeleteContactDialogProps) {
  const [deleteAssociated, setDeleteAssociated] = useState(false);

  // Reset checkbox when dialog closes
  useEffect(() => {
    if (!open) {
      setDeleteAssociated(false);
    }
  }, [open]);

  return (
    <AlertDialog open={open} onOpenChange={onOpenChange}>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>Delete Contact</AlertDialogTitle>
          <AlertDialogDescription>
            Are you sure you want to delete <span className="font-semibold text-foreground">{contactName || "this contact"}</span>? 
            This action will move the contact to the trash.
          </AlertDialogDescription>
        </AlertDialogHeader>
        
        <div className="flex items-start space-x-3 py-4 px-1">
          <Checkbox
            id="delete-associated"
            checked={deleteAssociated}
            onCheckedChange={(checked) => setDeleteAssociated(!!checked)}
            className="mt-1"
          />
          <div className="grid gap-1.5 leading-none">
            <Label
              htmlFor="delete-associated"
              className="text-sm font-medium leading-none cursor-pointer"
            >
              Delete associated records
            </Label>
            <p className="text-sm text-muted-foreground">
              This will also soft-delete all leads, deals, and tasks linked to this contact.
            </p>
          </div>
        </div>

        <AlertDialogFooter>
          <AlertDialogCancel>Cancel</AlertDialogCancel>
          <AlertDialogAction
            onClick={() => onConfirm(deleteAssociated)}
            className="bg-destructive text-destructive-foreground hover:bg-destructive/90 transition-colors"
          >
            Delete
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}
