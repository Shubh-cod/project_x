import { type LucideIcon, TrendingUp, TrendingDown, Minus } from "lucide-react";
import { cn } from "@/lib/utils";

interface StatCardProps {
  title: string;
  value: string | number;
  icon: LucideIcon;
  subtitle?: string;
  trend?: "up" | "down" | "neutral";
  trendLabel?: string;
  className?: string;
}

export function StatCard({ title, value, icon: Icon, subtitle, trend, trendLabel, className }: StatCardProps) {
  const TrendIcon = trend === "up" ? TrendingUp : trend === "down" ? TrendingDown : Minus;
  const trendColor =
    trend === "up" ? "text-success" : trend === "down" ? "text-destructive" : "text-muted-foreground";

  return (
    <div className={cn("data-card p-5 hover:shadow-md transition-all duration-200", className)}>
      <div className="flex items-center justify-between mb-4">
        <span className="text-sm font-medium text-muted-foreground">{title}</span>
        <div className="h-9 w-9 rounded-lg bg-primary/10 flex items-center justify-center">
          <Icon className="h-4 w-4 text-primary" />
        </div>
      </div>
      <p className="text-3xl font-display font-semibold text-foreground tabular-nums tracking-tight">{value}</p>
      {(subtitle || trendLabel) && (
        <div className="flex items-center gap-1.5 mt-2">
          {trend && trendLabel && (
            <TrendIcon className={cn("h-3.5 w-3.5", trendColor)} />
          )}
          <p className={cn("text-xs", trendLabel ? trendColor : "text-muted-foreground")}>
            {trendLabel || subtitle}
          </p>
        </div>
      )}
    </div>
  );
}
