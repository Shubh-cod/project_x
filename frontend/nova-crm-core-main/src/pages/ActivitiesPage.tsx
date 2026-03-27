import { AppLayout } from "@/components/AppLayout";
import { ActivityFeed } from "@/components/ActivityFeed";
import { Activity } from "lucide-react";

export default function ActivitiesPage() {
  return (
    <AppLayout>
      <div className="mb-6">
        <h1 className="text-2xl font-display font-bold text-foreground flex items-center gap-2">
          <Activity className="h-6 w-6 text-primary" />
          Activity Feed
        </h1>
        <p className="text-sm text-muted-foreground mt-1">
          All recent actions across your CRM
        </p>
      </div>

      <div className="bg-card rounded-lg border border-border p-5">
        <ActivityFeed limit={50} />
      </div>
    </AppLayout>
  );
}
