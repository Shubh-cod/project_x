import { useState, useRef, useEffect } from "react";
import { Search, Users, Target, DollarSign } from "lucide-react";
import { Input } from "@/components/ui/input";
import { searchApi } from "@/api/search.api";
import { useDebounce } from "@/hooks/use-debounce";
import { useNavigate } from "react-router-dom";

const TYPE_ICONS = {
  contact: Users,
  lead: Target,
  deal: DollarSign,
};

const TYPE_ROUTES: Record<string, (id: string) => string> = {
  contact: (id) => `/contacts/${id}`,
  lead: (id) => `/leads/${id}`,
  deal: (id) => `/deals/${id}`,
};

export function GlobalSearch() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<any>(null);
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const debouncedQuery = useDebounce(query, 300);
  const navigate = useNavigate();
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!debouncedQuery || debouncedQuery.length < 2) {
      setResults(null);
      setOpen(false);
      return;
    }
    setLoading(true);
    searchApi
      .global(debouncedQuery)
      .then((data) => {
        setResults(data);
        setOpen(true);
      })
      .catch(() => setResults(null))
      .finally(() => setLoading(false));
  }, [debouncedQuery]);

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false);
      }
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  const handleSelect = (type: string, id: string) => {
    setOpen(false);
    setQuery("");
    const route = TYPE_ROUTES[type]?.(id);
    if (route) navigate(route);
  };

  const allResults = [
    ...(results?.contacts || []),
    ...(results?.leads || []),
    ...(results?.deals || []),
  ];

  return (
    <div className="relative flex-1 max-w-md" ref={ref}>
      <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground pointer-events-none" />
      <Input
        placeholder="Search contacts, leads, deals..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        onFocus={() => results && setOpen(true)}
        className="pl-9 h-9 bg-muted/50 border-transparent focus-visible:bg-background focus-visible:border-input text-sm"
      />
      {open && (
        <div className="absolute top-full left-0 right-0 mt-1.5 bg-popover border border-border rounded-xl shadow-lg z-50 max-h-80 overflow-y-auto">
          {loading && (
            <div className="px-4 py-3 text-sm text-muted-foreground">Searching...</div>
          )}
          {!loading && allResults.length === 0 && (
            <div className="px-4 py-3 text-sm text-muted-foreground">No results for "{debouncedQuery}"</div>
          )}
          {!loading &&
            allResults.map((item: any) => {
              const Icon = TYPE_ICONS[item.type as keyof typeof TYPE_ICONS] || Search;
              return (
                <button
                  key={`${item.type}-${item.id}`}
                  onClick={() => handleSelect(item.type, item.id)}
                  className="w-full text-left px-4 py-2.5 hover:bg-muted/60 transition-colors flex items-center gap-3 first:rounded-t-xl last:rounded-b-xl"
                >
                  <div className="h-8 w-8 rounded-lg bg-muted flex items-center justify-center shrink-0">
                    <Icon className="h-4 w-4 text-muted-foreground" />
                  </div>
                  <div className="min-w-0">
                    <p className="text-sm font-medium text-foreground truncate">{item.title}</p>
                    <p className="text-xs text-muted-foreground capitalize truncate">
                      {item.type}{item.subtitle ? ` · ${item.subtitle}` : ""}
                    </p>
                  </div>
                </button>
              );
            })}
        </div>
      )}
    </div>
  );
}
