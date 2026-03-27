import { useState } from "react";
import { Search } from "lucide-react";
import { Input } from "@/components/ui/input";

export function GlobalSearch() {
  const [query, setQuery] = useState("");

  return (
    <div className="relative w-full max-w-md">
      <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
      <Input
        placeholder="Search contacts, leads, deals..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        className="pl-9 bg-secondary border-none h-9 text-sm"
      />
    </div>
  );
}
