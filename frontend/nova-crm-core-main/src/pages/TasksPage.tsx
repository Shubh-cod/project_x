import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { AppLayout } from "@/components/AppLayout";
import { PageHeader } from "@/components/shared/PageHeader";
import { PageSkeleton } from "@/components/shared/PageSkeleton";
import { EmptyState } from "@/components/shared/EmptyState";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Plus, CheckCircle2, Circle, Clock, CheckSquare } from "lucide-react";
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
      toast.success("Task updated");
    },
    onError: (error) => toast.error(error.message || "Failed to update task"),
  });

  if (isLoading) {
    return <AppLayout><PageSkeleton rows={4} columns={1} /></AppLayout>;
  }

  const tasks = data?.items || [];
  const pending = tasks.filter((t) => t.status !== "done");
  const completed = tasks.filter((t) => t.status === "done");
  const overdue = pending.filter((t) => t.due_date && new Date(t.due_date) < new Date());

  function isOverdue(dateStr: string, status: string) {
    return status !== "done" && new Date(dateStr) < new Date();
  }

  return (
    <AppLayout>
      <PageHeader
        icon={CheckSquare}
        title="Tasks"
        description={`${pending.length} pending · ${completed.length} completed${overdue.length > 0 ? ` · ${overdue.length} overdue` : ""}`}
        action={
          <Button onClick={() => { setEditingTask(null); setDialogOpen(true); }}>
            <Plus className="h-4 w-4 mr-2" />New Task
          </Button>
        }
      />

      {tasks.length === 0 ? (
        <div className="data-card">
          <EmptyState
            icon={CheckSquare}
            title="No tasks yet"
            description="Create tasks to stay on top of follow-ups and deadlines."
            action={
              <Button size="sm" onClick={() => { setEditingTask(null); setDialogOpen(true); }}>
                <Plus className="h-4 w-4 mr-2" />New Task
              </Button>
            }
          />
        </div>
      ) : (
        <div className="space-y-2">
          {tasks.map((task) => {
            const taskOverdue = task.due_date ? isOverdue(task.due_date, task.status) : false;
            const isDone = task.status === "done";
            return (
              <div
                key={task.id}
                className={`data-card px-5 py-3.5 flex items-center gap-4 hover:shadow-sm transition-all cursor-pointer ${isDone ? "opacity-60" : ""}`}
                onClick={() => { setEditingTask(task); setDialogOpen(true); }}
              >
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    toggleMutation.mutate({ id: task.id, status: isDone ? "todo" : "done" });
                  }}
                  disabled={toggleMutation.isPending}
                  className="shrink-0"
                >
                  {isDone ? (
                    <CheckCircle2 className="h-5 w-5 text-success" />
                  ) : (
                    <Circle className="h-5 w-5 text-muted-foreground hover:text-primary transition-colors" />
                  )}
                </button>
                <div className="flex-1 min-w-0">
                  <p className={`text-sm font-medium ${isDone ? "line-through text-muted-foreground" : ""}`}>
                    {task.title}
                  </p>
                  <div className="flex items-center gap-2 mt-0.5">
                    {task.linked_to_type && (
                      <span className="text-xs text-muted-foreground capitalize">
                        {task.linked_to_type}
                      </span>
                    )}
                    <Badge variant="secondary" className="text-xs capitalize">{task.priority}</Badge>
                  </div>
                </div>
                {task.due_date && (
                  <div className="flex items-center gap-1.5 shrink-0">
                    <Clock className={`h-3.5 w-3.5 ${taskOverdue ? "text-destructive" : "text-muted-foreground"}`} />
                    <span className={`text-xs tabular-nums ${taskOverdue ? "text-destructive font-medium" : "text-muted-foreground"}`}>
                      {new Date(task.due_date).toLocaleDateString()}
                    </span>
                    {taskOverdue && <Badge variant="destructive" className="text-xs">Overdue</Badge>}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      <TaskDialog open={dialogOpen} onOpenChange={setDialogOpen} task={editingTask} />
    </AppLayout>
  );
}
