import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { AppLayout } from "@/components/AppLayout";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Plus, CheckCircle2, Circle, Clock } from "lucide-react";
import { tasksApi } from "@/api/tasks.api";

function isOverdue(dateStr: string, completed: boolean) {
  return !completed && new Date(dateStr) < new Date();
}

export default function TasksPage() {
  const queryClient = useQueryClient();
  const { data, isLoading } = useQuery({
    queryKey: ["tasks"],
    queryFn: () => tasksApi.list(),
  });

  const toggleMutation = useMutation({
    mutationFn: ({ id, completed }: { id: string; completed: boolean }) =>
      tasksApi.update(id, { completed }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tasks"] });
    },
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

  const tasks = data?.items || [];
  const pending = tasks.filter((t) => !t.completed);
  const completed = tasks.filter((t) => t.completed);

  return (
    <AppLayout>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-display font-bold text-foreground">Tasks</h1>
          <p className="text-sm text-muted-foreground mt-1">{pending.length} pending · {completed.length} completed</p>
        </div>
        <Button>
          <Plus className="h-4 w-4 mr-2" />
          New Task
        </Button>
      </div>

      <div className="space-y-2">
        {tasks.map((task) => {
          const overdue = task.due_date ? isOverdue(task.due_date, task.completed) : false;
          return (
            <div
              key={task.id}
              className={`bg-card rounded-lg border border-border px-5 py-3 flex items-center gap-4 hover:shadow-sm transition-shadow ${task.completed ? "opacity-60" : ""}`}
            >
              <button 
                onClick={() => toggleMutation.mutate({ id: task.id, completed: !task.completed })}
                disabled={toggleMutation.isPending}
              >
                {task.completed ? (
                  <CheckCircle2 className="h-5 w-5 text-success shrink-0" />
                ) : (
                  <Circle className="h-5 w-5 text-muted-foreground shrink-0 cursor-pointer hover:text-primary transition-colors" />
                )}
              </button>
              <div className="flex-1 min-w-0">
                <p className={`text-sm font-medium ${task.completed ? "line-through text-muted-foreground" : "text-foreground"}`}>
                  {task.title}
                </p>
                {task.entity_type && (
                  <span className="text-xs text-muted-foreground capitalize">
                    Linked to {task.entity_type}
                  </span>
                )}
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
            <div className="py-12 text-center text-muted-foreground">
              No tasks found. Create one to get started!
            </div>
          )}
      </div>
    </AppLayout>
  );
}
