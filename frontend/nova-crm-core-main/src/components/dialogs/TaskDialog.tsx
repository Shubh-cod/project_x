import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { tasksApi } from "@/api/tasks.api";
import type { Task } from "@/api/types";

interface TaskDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  task?: Task | null;
}

export function TaskDialog({ open, onOpenChange, task }: TaskDialogProps) {
  const queryClient = useQueryClient();
  const isEditing = !!task;

  const [form, setForm] = useState({
    title: task?.title || "",
    description: task?.description || "",
    due_date: task?.due_date ? task.due_date.split("T")[0] : "",
    priority: task?.priority || "medium",
    status: task?.status || "todo",
    linked_to_type: task?.linked_to_type || "",
    linked_to_id: task?.linked_to_id || "",
  });

  const mutation = useMutation({
    mutationFn: (data: any) =>
      isEditing ? tasksApi.update(task!.id, data) : tasksApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tasks"] });
      onOpenChange(false);
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const payload: any = { ...form };
    if (payload.due_date) payload.due_date = new Date(payload.due_date).toISOString();
    else delete payload.due_date;
    if (!payload.linked_to_type) {
      delete payload.linked_to_type;
      delete payload.linked_to_id;
    }
    if (!payload.description) delete payload.description;
    mutation.mutate(payload);
  };

  const update = (key: string, value: string) => setForm((f) => ({ ...f, [key]: value }));

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>{isEditing ? "Edit Task" : "New Task"}</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-3">
          <div>
            <label className="text-sm font-medium mb-1 block">Title *</label>
            <Input value={form.title} onChange={(e) => update("title", e.target.value)} required />
          </div>
          <div>
            <label className="text-sm font-medium mb-1 block">Description</label>
            <textarea
              className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm min-h-[60px]"
              value={form.description}
              onChange={(e) => update("description", e.target.value)}
            />
          </div>
          <div className="grid grid-cols-3 gap-3">
            <div>
              <label className="text-sm font-medium mb-1 block">Priority</label>
              <select className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm" value={form.priority} onChange={(e) => update("priority", e.target.value)}>
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
                <option value="urgent">Urgent</option>
              </select>
            </div>
            <div>
              <label className="text-sm font-medium mb-1 block">Status</label>
              <select className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm" value={form.status} onChange={(e) => update("status", e.target.value)}>
                <option value="todo">To Do</option>
                <option value="in_progress">In Progress</option>
                <option value="done">Done</option>
                <option value="deferred">Deferred</option>
              </select>
            </div>
            <div>
              <label className="text-sm font-medium mb-1 block">Due Date</label>
              <Input type="date" value={form.due_date} onChange={(e) => update("due_date", e.target.value)} />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-sm font-medium mb-1 block">Linked Entity</label>
              <select className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm" value={form.linked_to_type} onChange={(e) => update("linked_to_type", e.target.value)}>
                <option value="">None</option>
                <option value="contact">Contact</option>
                <option value="lead">Lead</option>
                <option value="deal">Deal</option>
              </select>
            </div>
            {form.linked_to_type && (
              <div>
                <label className="text-sm font-medium mb-1 block">Entity ID</label>
                <Input value={form.linked_to_id} onChange={(e) => update("linked_to_id", e.target.value)} placeholder="UUID" />
              </div>
            )}
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
