import { useQuery } from "@tanstack/react-query";
import { activitiesApi } from "@/api/activities.api";
import { Activity as ActivityIcon } from "lucide-react";

interface ActivityFeedProps {
  entityType?: string;
  entityId?: string;
  limit?: number;
}

export function ActivityFeed({ entityType, entityId, limit = 10 }: ActivityFeedProps) {
  const { data, isLoading } = useQuery({
    queryKey: ["activities", entityType, entityId],
    queryFn: () =>
      entityType && entityId
        ? activitiesApi.listByEntity(entityType, entityId, 1, limit)
        : activitiesApi.listGlobal({ page_size: limit }),
  });

  const activities = data?.items || [];

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-4">
        <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (activities.length === 0) {
    return (
      <p className="text-sm text-muted-foreground text-center py-4">
        No recent activity.
      </p>
    );
  }

  return (
    <div className="space-y-3">
      {activities.map((a) => (
        <div key={a.id} className="flex items-start gap-3">
          <div className="h-6 w-6 rounded-full bg-primary/10 flex items-center justify-center shrink-0 mt-0.5">
            <ActivityIcon className="h-3 w-3 text-primary" />
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm text-foreground">
              <span className="font-medium capitalize">{a.action}</span>
              {" on "}
              <span className="text-muted-foreground capitalize">{a.entity_type}</span>
            </p>
            <p className="text-xs text-muted-foreground">
              {new Date(a.created_at).toLocaleString()}
            </p>
          </div>
        </div>
      ))}
    </div>
  );
}
