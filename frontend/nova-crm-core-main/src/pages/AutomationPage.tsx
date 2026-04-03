import { useState } from "react";
import { toast } from "sonner";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { AppLayout } from "@/components/AppLayout";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Zap,
  Plus,
  Trash2,
  Power,
  PowerOff,
  Target,
  Clock,
  AlertTriangle,
  CheckCircle2,
  Settings,
} from "lucide-react";
import { automationApi } from "@/api/automation.api";
import type { AutomationRule } from "@/api/types";

const TRIGGER_LABELS: Record<string, { label: string; icon: any; color: string }> = {
  lead_created: { label: "Lead Created", icon: Target, color: "bg-blue-500/10 text-blue-600" },
  deal_stale: { label: "Deal Stale", icon: AlertTriangle, color: "bg-amber-500/10 text-amber-600" },
  task_overdue: { label: "Task Overdue", icon: Clock, color: "bg-red-500/10 text-red-600" },
};

const ACTION_LABELS: Record<string, string> = {
  create_task: "Create Task",
};

export default function AutomationPage() {
  const queryClient = useQueryClient();
  const [dialogOpen, setDialogOpen] = useState(false);

  const [form, setForm] = useState({
    name: "",
    trigger_event: "lead_created",
    action_type: "create_task",
    title_template: "",
    priority: "medium",
    due_in_hours: "24",
  });

  const { data, isLoading } = useQuery({
    queryKey: ["automation-rules"],
    queryFn: () => automationApi.listRules(),
  });

  const createMutation = useMutation({
    mutationFn: () =>
      automationApi.createRule({
        name: form.name,
        trigger_event: form.trigger_event,
        action_type: form.action_type,
        action_config: {
          title_template: form.title_template,
          priority: form.priority,
          due_in_hours: parseInt(form.due_in_hours) || 24,
        },
        is_active: true,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["automation-rules"] });
      toast.success("Automation rule created");
      setDialogOpen(false);
      setForm({
        name: "",
        trigger_event: "lead_created",
        action_type: "create_task",
        title_template: "",
        priority: "medium",
        due_in_hours: "24",
      });
    },
    onError: (error) => {
      toast.error(error.message || "Failed to create rule");
    },
  });

  const toggleMutation = useMutation({
    mutationFn: ({ id, is_active }: { id: string; is_active: boolean }) =>
      automationApi.updateRule(id, { is_active }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["automation-rules"] });
      toast.success("Rule updated");
    },
    onError: (error) => {
      toast.error(error.message || "Failed to update rule");
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => automationApi.deleteRule(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["automation-rules"] });
      toast.success("Rule deleted");
    },
    onError: (error) => {
      toast.error(error.message || "Failed to delete rule");
    },
  });

  const update = (key: string, value: string) =>
    setForm((f) => ({ ...f, [key]: value }));

  const rules: AutomationRule[] = data?.items || [];

  if (isLoading) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center h-[50vh]">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
        </div>
      </AppLayout>
    );
  }

  return (
    <AppLayout>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-display font-bold text-foreground flex items-center gap-2">
            <Zap className="h-6 w-6 text-primary" />
            Automation
          </h1>
          <p className="text-sm text-muted-foreground mt-1">
            Smart rules that create follow-up tasks automatically
          </p>
        </div>
        <Button
          onClick={() => setDialogOpen(true)}
        >
          <Plus className="h-4 w-4 mr-2" />
          New Rule
        </Button>
      </div>

      {/* Info banner */}
      <div className="mb-6 p-4 rounded-lg border border-primary/20 bg-primary/5">
        <div className="flex items-start gap-3">
          <Settings className="h-5 w-5 text-primary mt-0.5 shrink-0" />
          <div>
            <p className="text-sm font-medium text-foreground">
              How automation works
            </p>
            <p className="text-xs text-muted-foreground mt-1">
              When a trigger event occurs (e.g., a new lead is created), active
              rules matching that trigger will automatically create follow-up
              tasks. Tasks are prefixed with <code className="text-xs font-mono bg-secondary/60 px-1 py-0.5 rounded">[Auto]</code> so
              you can easily identify them.
            </p>
          </div>
        </div>
      </div>

      {/* Rules list */}
      <div className="space-y-3">
        {rules.map((rule) => {
          const triggerInfo = TRIGGER_LABELS[rule.trigger_event] || {
            label: rule.trigger_event,
            icon: Zap,
            color: "bg-primary/10 text-primary",
          };
          const TriggerIcon = triggerInfo.icon;
          const config = rule.action_config || {};

          return (
            <div
              key={rule.id}
              className={`bg-card rounded-lg border border-border p-5 transition-all ${
                rule.is_active
                  ? "hover:shadow-md hover:border-primary/30"
                  : "opacity-60"
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start gap-4 flex-1 min-w-0">
                  <div
                    className={`h-10 w-10 rounded-lg ${triggerInfo.color} flex items-center justify-center shrink-0`}
                  >
                    <TriggerIcon className="h-5 w-5" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <h3 className="text-sm font-semibold text-foreground truncate">
                        {rule.name}
                      </h3>
                      {rule.is_active ? (
                        <Badge
                          variant="default"
                          className="bg-success/10 text-success border-success/20 text-xs"
                        >
                          <CheckCircle2 className="h-3 w-3 mr-1" />
                          Active
                        </Badge>
                      ) : (
                        <Badge variant="secondary" className="text-xs">
                          Inactive
                        </Badge>
                      )}
                    </div>
                    <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-muted-foreground">
                      <span className="flex items-center gap-1">
                        <span className="font-medium text-foreground">
                          Trigger:
                        </span>{" "}
                        {triggerInfo.label}
                      </span>
                      <span className="flex items-center gap-1">
                        <span className="font-medium text-foreground">
                          Action:
                        </span>{" "}
                        {ACTION_LABELS[rule.action_type] || rule.action_type}
                      </span>
                      {config.title_template && (
                        <span className="flex items-center gap-1">
                          <span className="font-medium text-foreground">
                            Template:
                          </span>{" "}
                          <code className="font-mono bg-secondary/60 px-1.5 py-0.5 rounded text-foreground">
                            {config.title_template}
                          </code>
                        </span>
                      )}
                      {config.priority && (
                        <span className="flex items-center gap-1">
                          <span className="font-medium text-foreground">
                            Priority:
                          </span>{" "}
                          <span className="capitalize">{config.priority}</span>
                        </span>
                      )}
                      {config.due_in_hours && (
                        <span className="flex items-center gap-1">
                          <span className="font-medium text-foreground">
                            Due in:
                          </span>{" "}
                          {config.due_in_hours}h
                        </span>
                      )}
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-1 ml-4 shrink-0">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() =>
                      toggleMutation.mutate({
                        id: rule.id,
                        is_active: !rule.is_active,
                      })
                    }
                    disabled={toggleMutation.isPending}
                    title={rule.is_active ? "Deactivate" : "Activate"}
                  >
                    {rule.is_active ? (
                      <Power className="h-4 w-4 text-success" />
                    ) : (
                      <PowerOff className="h-4 w-4 text-muted-foreground" />
                    )}
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => deleteMutation.mutate(rule.id)}
                    disabled={deleteMutation.isPending}
                  >
                    <Trash2 className="h-4 w-4 text-destructive" />
                  </Button>
                </div>
              </div>
            </div>
          );
        })}

        {rules.length === 0 && (
          <div className="py-16 text-center border rounded-lg border-dashed bg-secondary/10">
            <Zap className="h-10 w-10 text-muted-foreground mx-auto mb-3 opacity-40" />
            <h3 className="text-sm font-semibold text-foreground">
              No automation rules yet
            </h3>
            <p className="text-sm text-muted-foreground mt-1 mb-4">
              Create your first rule to start automating follow-ups.
            </p>
            <Button size="sm" onClick={() => setDialogOpen(true)}>
              <Plus className="h-4 w-4 mr-2" />
              Create Rule
            </Button>
          </div>
        )}
      </div>

      {/* Create Rule Dialog */}
      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>New Automation Rule</DialogTitle>
          </DialogHeader>
          <form
            onSubmit={(e) => {
              e.preventDefault();
              createMutation.mutate();
            }}
            className="space-y-3"
          >
            <div>
              <label className="text-sm font-medium mb-1 block">
                Rule Name *
              </label>
              <Input
                value={form.name}
                onChange={(e) => update("name", e.target.value)}
                placeholder="e.g. Follow up on new lead"
                required
              />
            </div>
            <div>
              <label className="text-sm font-medium mb-1 block">
                Trigger Event *
              </label>
              <select
                className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                value={form.trigger_event}
                onChange={(e) => update("trigger_event", e.target.value)}
              >
                <option value="lead_created">Lead Created</option>
                <option value="deal_stale">Deal Stale (&gt;5 days)</option>
                <option value="task_overdue">Task Overdue</option>
              </select>
            </div>
            <div>
              <label className="text-sm font-medium mb-1 block">
                Task Title Template *
              </label>
              <Input
                value={form.title_template}
                onChange={(e) => update("title_template", e.target.value)}
                placeholder="e.g. Follow up: {lead_title}"
                required
              />
              <p className="text-xs text-muted-foreground mt-1">
                Use <code className="font-mono bg-secondary/60 px-1 rounded">{"{lead_title}"}</code>, <code className="font-mono bg-secondary/60 px-1 rounded">{"{deal_title}"}</code> as placeholders.
              </p>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-sm font-medium mb-1 block">
                  Priority
                </label>
                <select
                  className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                  value={form.priority}
                  onChange={(e) => update("priority", e.target.value)}
                >
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                  <option value="urgent">Urgent</option>
                </select>
              </div>
              <div>
                <label className="text-sm font-medium mb-1 block">
                  Due In (hours)
                </label>
                <Input
                  type="number"
                  min="1"
                  value={form.due_in_hours}
                  onChange={(e) => update("due_in_hours", e.target.value)}
                />
              </div>
            </div>
            {createMutation.error && (
              <p className="text-sm text-destructive">
                {(createMutation.error as Error).message}
              </p>
            )}
            <div className="flex justify-end gap-2 pt-2">
              <Button
                type="button"
                variant="outline"
                onClick={() => setDialogOpen(false)}
              >
                Cancel
              </Button>
              <Button type="submit" disabled={createMutation.isPending}>
                {createMutation.isPending ? "Creating..." : "Create Rule"}
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>
    </AppLayout>
  );
}
