import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { AppLayout } from "@/components/AppLayout";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Plus, CheckCircle2, Circle, Clock } from "lucide-react";
import { tasksApi } from "@/api/tasks.api";
import { useState } from "react";
import { TaskDialog } from "@/components/dialogs/TaskDialog";

export default function TasksPage() {
  const queryClient = useQueryClient();
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingTask, setEditingTask] = useState<any>(null);

  const { data, isLoading } = useQuery({
    queryKey: ["tasks"],
    queryFn: () => tasksApi.list(),
  });

  const toggleMutation = useMutation({
    mutationFn: ({ id, status }: { id: string; status: string }) =>
      tasksApi.update(id, { status }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tasks"] });
      toast.success("Task status updated");
    },
    onError: (error) => {
      toast.error(error.message || "Failed to update task");
    },
  });

  if (isLoading) {
    return (
      <AppLayout>
        <div className="mb-6">
          <div className="h-7 w-20 bg-secondary rounded animate-pulse" />
          <div className="h-4 w-40 bg-secondary/60 rounded animate-pulse mt-2" />
        </div>
        <div className="space-y-2">
          {[1, 2, 3, 4].map(i => (
            <div key={i} className="bg-card rounded-lg border border-border px-5 py-3 flex items-center gap-4 animate-pulse">
              <div className="h-5 w-5 rounded-full bg-secondary" />
              <div className="flex-1 space-y-2">
                <div className="h-4 w-48 bg-secondary rounded" />
                <div className="h-3 w-24 bg-secondary/60 rounded" />
              </div>
              <div className="h-3 w-20 bg-secondary/60 rounded" />
            </div>
          ))}
        </div>
      </AppLayout>
    );
  }

  const tasks = data?.items || [];
  const pending = tasks.filter((t) => t.status !== "done");
  const completed = tasks.filter((t) => t.status === "done");

  function isOverdue(dateStr: string, status: string) {
    return status !== "done" && new Date(dateStr) < new Date();
  }

  return (
    <AppLayout>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-display font-bold text-foreground">Tasks</h1>
          <p className="text-sm text-muted-foreground mt-1">{pending.length} pending · {completed.length} completed</p>
        </div>
        <Button onClick={() => { setEditingTask(null); setDialogOpen(true); }}>
          <Plus className="h-4 w-4 mr-2" />
          New Task
        </Button>
      </div>

      <div className="space-y-2">
        {tasks.map((task) => {
          const overdue = task.due_date ? isOverdue(task.due_date, task.status) : false;
          const isDone = task.status === "done";
          return (
            <div
              key={task.id}
              className={`bg-card rounded-lg border border-border px-5 py-3 flex items-center gap-4 hover:shadow-sm transition-shadow cursor-pointer ${isDone ? "opacity-60" : ""}`}
              onClick={() => { setEditingTask(task); setDialogOpen(true); }}
            >
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  toggleMutation.mutate({ id: task.id, status: isDone ? "todo" : "done" });
                }}
                disabled={toggleMutation.isPending}
              >
                {isDone ? (
                  <CheckCircle2 className="h-5 w-5 text-success shrink-0" />
                ) : (
                  <Circle className="h-5 w-5 text-muted-foreground shrink-0 cursor-pointer hover:text-primary transition-colors" />
                )}
              </button>
              <div className="flex-1 min-w-0">
                <p className={`text-sm font-medium ${isDone ? "line-through text-muted-foreground" : "text-foreground"}`}>
                  {task.title}
                </p>
                <div className="flex items-center gap-2 mt-0.5">
                  {task.linked_to_type && (
                    <span className="text-xs text-muted-foreground capitalize">
                      Linked to {task.linked_to_type}
                    </span>
                  )}
                  <Badge variant="secondary" className="text-xs capitalize">{task.priority}</Badge>
                </div>
              </div>
              {task.due_date && (
                <div className="flex items-center gap-1.5">
                  <Clock className={`h-3 w-3 ${overdue ? "text-destructive" : "text-muted-foreground"}`} />
                  <span className={`text-xs ${overdue ? "text-destructive font-medium" : "text-muted-foreground"}`}>
                    {new Date(task.due_date).toLocaleDateString()}
                  </span>
                  {overdue && <Badge variant="destructive" className="text-xs ml-1">Overdue</Badge>}
                </div>
              )}
            </div>
          );
        })}
        {tasks.length === 0 && (
          <div className="py-16 text-center border rounded-lg border-dashed bg-secondary/10">
            <CheckCircle2 className="h-10 w-10 text-muted-foreground mx-auto mb-3 opacity-40" />
            <p className="text-sm font-semibold text-foreground">No tasks yet</p>
            <p className="text-sm text-muted-foreground mt-1 mb-4">Create a task to stay on top of your follow-ups.</p>
            <Button size="sm" onClick={() => { setEditingTask(null); setDialogOpen(true); }}>
              <Plus className="h-4 w-4 mr-2" />New Task
            </Button>
          </div>
        )}
      </div>

      <TaskDialog open={dialogOpen} onOpenChange={setDialogOpen} task={editingTask} />
    </AppLayout>
  );
}
