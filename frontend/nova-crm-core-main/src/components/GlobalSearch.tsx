import { useState, useRef, useEffect } from "react";
import { Search } from "lucide-react";
import { Input } from "@/components/ui/input";
import { searchApi } from "@/api/search.api";
import { useDebounce } from "@/hooks/use-debounce";
import { useNavigate } from "react-router-dom";

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
    if (type === "contact") navigate("/contacts");
    else if (type === "lead") navigate("/leads");
    else if (type === "deal") navigate("/deals");
  };

  const allResults = [
    ...(results?.contacts || []),
    ...(results?.leads || []),
    ...(results?.deals || []),
  ];

  return (
    <div className="relative w-full max-w-md" ref={ref}>
      <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
      <Input
        placeholder="Search contacts, leads, deals..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        onFocus={() => results && setOpen(true)}
        className="pl-9 bg-secondary border-none h-9 text-sm"
      />
      {open && (
        <div className="absolute top-full left-0 right-0 mt-1 bg-card border border-border rounded-lg shadow-lg z-50 max-h-80 overflow-y-auto">
          {loading && (
            <div className="px-4 py-3 text-sm text-muted-foreground">Searching...</div>
          )}
          {!loading && allResults.length === 0 && (
            <div className="px-4 py-3 text-sm text-muted-foreground">No results found</div>
          )}
          {!loading &&
            allResults.map((item: any) => (
              <button
                key={`${item.type}-${item.id}`}
                onClick={() => handleSelect(item.type, item.id)}
                className="w-full text-left px-4 py-2.5 hover:bg-secondary/50 transition-colors flex items-center gap-3"
              >
                <span className="text-xs font-semibold uppercase text-muted-foreground w-16">
                  {item.type}
                </span>
                <div>
                  <p className="text-sm font-medium text-foreground">{item.title}</p>
                  {item.subtitle && (
                    <p className="text-xs text-muted-foreground">{item.subtitle}</p>
                  )}
                </div>
              </button>
            ))}
        </div>
      )}
    </div>
  );
}
