import { AppSidebar } from "./AppSidebar";
import { GlobalSearch } from "./GlobalSearch";
import { useAuth } from "@/contexts/AuthContext";

export function AppLayout({ children }: { children: React.ReactNode }) {
  const { user } = useAuth();
  const initials = user?.full_name
    ?.split(" ")
    .map((n) => n[0])
    .join("")
    .toUpperCase() || "U";

  return (
    <div className="min-h-screen bg-background">
      <AppSidebar />
      <div className="ml-64">
        {/* Top bar */}
        <header className="sticky top-0 z-40 bg-card/80 backdrop-blur-sm border-b border-border px-6 py-3 flex items-center justify-between">
          <GlobalSearch />
          <div className="flex items-center gap-3">
            <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center text-xs font-semibold text-primary">
              {initials}
            </div>
            {user && <span className="text-sm text-muted-foreground">{user.full_name}</span>}
          </div>
        </header>
        {/* Content */}
        <main className="p-6 animate-fade-in">{children}</main>
      </div>
    </div>
  );
}
