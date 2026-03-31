import { useQuery } from "@tanstack/react-query";
import { activitiesApi } from "@/api/activities.api";
import { Activity as ActivityIcon, Plus, Pencil, ArrowRight, FileText, Zap } from "lucide-react";

interface EntityTimelineProps {
  entityType: string;
  entityId: string;
  limit?: number;
}

export function EntityTimeline({ entityType, entityId, limit = 50 }: EntityTimelineProps) {
  const { data, isLoading } = useQuery({
    queryKey: ["activities", entityType, entityId],
    queryFn: () => activitiesApi.listByEntity(entityType, entityId, 1, limit),
  });

  const activities = data?.items || [];

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (activities.length === 0) {
    return (
      <div className="py-12 text-center border rounded-lg border-dashed bg-secondary/10">
        <ActivityIcon className="h-8 w-8 text-muted-foreground mx-auto mb-3 opacity-50" />
        <h3 className="text-sm font-semibold text-foreground">No Timeline Activity</h3>
        <p className="text-sm text-muted-foreground mt-1">
          Activity such as updates and task completion will appear here.
        </p>
      </div>
    );
  }

  const getActionDetails = (action: string) => {
    switch (action) {
      case "created":
        return { icon: Plus, bgColor: "bg-blue-500/10", textColor: "text-blue-600" };
      case "updated":
        return { icon: Pencil, bgColor: "bg-zinc-500/10", textColor: "text-zinc-600" };
      case "status_changed":
        return { icon: ArrowRight, bgColor: "bg-orange-500/10", textColor: "text-orange-600" };
      case "note_added":
        return { icon: FileText, bgColor: "bg-purple-500/10", textColor: "text-purple-600" };
      case "converted":
        return { icon: Zap, bgColor: "bg-yellow-500/10", textColor: "text-yellow-600" };
      default:
        return { icon: ActivityIcon, bgColor: "bg-primary/10", textColor: "text-primary" };
    }
  };

  const renderDescription = (a: any) => {
    const defaultDesc = (
      <span>
        <span className="font-medium capitalize">{a.action}</span>
        {" on "}
        <span className="capitalize">{a.entity_type}</span>
      </span>
    );

    if (a.action === "status_changed" && a.metadata?.old && a.metadata?.new) {
      return (
        <span>
          Changed status from <span className="font-medium badge variant-secondary">{a.metadata.old}</span> to <span className="font-medium badge variant-secondary">{a.metadata.new}</span>
        </span>
      );
    }
    
    if (a.action === "note_added") {
      return <span>Added a note</span>;
    }

    if (a.entity_type === "task" && a.action === "created") {
      return <span>Created task <span className="font-semibold">{a.metadata?.title || "Task"}</span></span>;
    }

    return defaultDesc;
  };

  return (
    <div className="relative border-l border-border ml-4 mt-2 mb-4 space-y-6">
      {activities.map((a) => {
        const { icon: Icon, bgColor, textColor } = getActionDetails(a.action);
        return (
          <div key={a.id} className="relative pl-6">
            <div className={`absolute -left-3 top-0 h-6 w-6 rounded-full ${bgColor} flex items-center justify-center ring-4 ring-background`}>
              <Icon className={`h-3 w-3 ${textColor}`} />
            </div>
            <div>
              <p className="text-sm text-foreground">
                {renderDescription(a)}
              </p>
              <p className="text-xs text-muted-foreground mt-0.5">
                {new Date(a.created_at).toLocaleString()}
              </p>
            </div>
          </div>
        );
      })}
    </div>
  );
}
