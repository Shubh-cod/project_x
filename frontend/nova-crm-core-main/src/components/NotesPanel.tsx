import { useState } from "react";
import { toast } from "sonner";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { notesApi } from "@/api/notes.api";
import { Button } from "@/components/ui/button";
import { Trash2 } from "lucide-react";

interface NotesPanelProps {
  entityType: string;
  entityId: string;
}

export function NotesPanel({ entityType, entityId }: NotesPanelProps) {
  const queryClient = useQueryClient();
  const [content, setContent] = useState("");

  const { data, isLoading } = useQuery({
    queryKey: ["notes", entityType, entityId],
    queryFn: () => notesApi.listByEntity(entityType, entityId),
  });

  const createMutation = useMutation({
    mutationFn: () => notesApi.create({ entity_type: entityType, entity_id: entityId, content }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["notes", entityType, entityId] });
      setContent("");
      toast.success("Note added");
    },
    onError: (error) => {
      toast.error(error.message || "Failed to add note");
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => notesApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["notes", entityType, entityId] });
      toast.success("Note deleted");
    },
    onError: (error) => {
      toast.error(error.message || "Failed to delete note");
    },
  });

  const notes = data?.items || [];

  return (
    <div className="space-y-3">
      <div className="flex gap-2">
        <textarea
          className="flex-1 rounded-md border border-input bg-background px-3 py-2 text-sm min-h-[40px]"
          placeholder="Add a note..."
          value={content}
          onChange={(e) => setContent(e.target.value)}
        />
        <Button
          size="sm"
          onClick={() => createMutation.mutate()}
          disabled={!content.trim() || createMutation.isPending}
        >
          Add
        </Button>
      </div>
      {isLoading && (
        <div className="flex items-center justify-center py-2">
          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary"></div>
        </div>
      )}
      {notes.map((note) => (
        <div key={note.id} className="bg-secondary/30 rounded-md p-3 flex items-start gap-2">
          <div className="flex-1">
            <p className="text-sm text-foreground whitespace-pre-wrap">{note.content}</p>
            <p className="text-xs text-muted-foreground mt-1">
              {new Date(note.created_at).toLocaleString()}
            </p>
          </div>
          <button onClick={() => deleteMutation.mutate(note.id)}>
            <Trash2 className="h-3.5 w-3.5 text-muted-foreground hover:text-destructive transition-colors" />
          </button>
        </div>
      ))}
      {!isLoading && notes.length === 0 && (
        <p className="text-xs text-muted-foreground text-center py-2">No notes yet.</p>
      )}
    </div>
  );
}
