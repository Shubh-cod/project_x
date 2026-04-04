import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Progress } from "@/components/ui/progress";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { 
  Upload, 
  FileUp, 
  CheckCircle2, 
  AlertCircle, 
  X, 
  FileText,
  Loader2
} from "lucide-react";
import { contactsApi } from "@/api/contacts.api";

interface ImportCSVDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function ImportCSVDialog({ open, onOpenChange }: ImportCSVDialogProps) {
  const [file, setFile] = useState<File | null>(null);
  const [results, setResults] = useState<any>(null);
  const queryClient = useQueryClient();

  const importMutation = useMutation({
    mutationFn: (file: File) => contactsApi.importCSV(file),
    onSuccess: (data) => {
      setResults(data);
      queryClient.invalidateQueries({ queryKey: ["contacts"] });
      if (data.success_count > 0) {
        toast.success(`Successfully imported ${data.success_count} contacts`);
      }
    },
    onError: (error: any) => {
      toast.error(error.message || "Failed to import contacts");
    },
  });

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      if (!selectedFile.name.endsWith(".csv")) {
        toast.error("Please select a CSV file");
        return;
      }
      setFile(selectedFile);
      setResults(null);
    }
  };

  const handleImport = () => {
    if (file) {
      importMutation.mutate(file);
    }
  };

  const reset = () => {
    setFile(null);
    setResults(null);
    importMutation.reset();
  };

  const handleClose = (open: boolean) => {
    if (!open) {
      reset();
    }
    onOpenChange(open);
  };

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Upload className="h-5 w-5 text-primary" />
            Import Contacts
          </DialogTitle>
          <DialogDescription>
            Upload a CSV file to bulk import contacts. 
            Columns will be automatically mapped.
          </DialogDescription>
        </DialogHeader>

        {!results && !importMutation.isPending && (
          <div className="space-y-4 py-4">
            <div 
              className={`border-2 border-dashed rounded-lg p-8 flex flex-col items-center justify-center gap-3 transition-colors ${
                file ? "border-primary bg-primary/5" : "border-border hover:border-primary/50"
              }`}
            >
              {file ? (
                <FileText className="h-10 w-10 text-primary" />
              ) : (
                <FileUp className="h-10 w-10 text-muted-foreground" />
              )}
              <div className="text-center">
                <p className="text-sm font-medium">
                  {file ? file.name : "Choose a CSV file or drag and drop"}
                </p>
                <p className="text-xs text-muted-foreground mt-1">
                  Max file size: 5MB
                </p>
              </div>
              <Input
                type="file"
                accept=".csv"
                className="hidden"
                id="csv-upload"
                onChange={handleFileChange}
              />
              <Button 
                variant="outline" 
                size="sm" 
                asChild
              >
                <label htmlFor="csv-upload" className="cursor-pointer">
                  {file ? "Change File" : "Select File"}
                </label>
              </Button>
            </div>

            {importMutation.isError && (
              <Alert variant="destructive">
                <AlertCircle className="h-4 w-4" />
                <AlertTitle>Import Failed</AlertTitle>
                <AlertDescription>
                  {importMutation.error instanceof Error ? importMutation.error.message : "An unexpected error occurred"}
                </AlertDescription>
              </Alert>
            )}

            <div className="bg-secondary/30 rounded-md p-3 text-xs text-muted-foreground space-y-1">
              <p className="font-semibold text-foreground mb-1">Supported headers:</p>
              <p>• name (required), email, phone, company, address, tags, notes</p>
              <p>• Tags can be comma-separated</p>
            </div>
          </div>
        )}

        {importMutation.isPending && (
          <div className="py-12 flex flex-col items-center justify-center gap-4">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
            <p className="text-sm font-medium">Processing your file...</p>
            <Progress value={undefined} className="w-[80%]" />
          </div>
        )}

        {results && (
          <div className="space-y-4 py-2">
            <div className="grid grid-cols-2 gap-3">
              <div className="bg-emerald-500/10 border border-emerald-500/20 rounded-lg p-3 flex items-center gap-3">
                <CheckCircle2 className="h-5 w-5 text-emerald-500" />
                <div>
                  <p className="text-sm font-bold text-emerald-600">{results.success_count}</p>
                  <p className="text-[10px] uppercase tracking-wider font-semibold text-emerald-600/70">Imported</p>
                </div>
              </div>
              <div className="bg-amber-500/10 border border-amber-500/20 rounded-lg p-3 flex items-center gap-3">
                <AlertCircle className="h-5 w-5 text-amber-500" />
                <div>
                  <p className="text-sm font-bold text-amber-600">{results.failed_count}</p>
                  <p className="text-[10px] uppercase tracking-wider font-semibold text-amber-600/70">Failed</p>
                </div>
              </div>
            </div>

            {results.errors.length > 0 && (
              <div className="space-y-2">
                <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Errors ({results.errors.length})</p>
                <ScrollArea className="h-[150px] rounded-md border border-border p-2">
                  <div className="space-y-2">
                    {results.errors.map((err: any, idx: number) => (
                      <div key={idx} className="text-xs flex gap-2 items-start p-1.5 rounded hover:bg-secondary/50">
                        <span className="bg-secondary px-1.5 py-0.5 rounded font-mono text-[10px]">Row {err.row}</span>
                        <span className="text-destructive font-medium">{err.error}</span>
                      </div>
                    ))}
                  </div>
                </ScrollArea>
              </div>
            )}

            {!results.errors.length && results.success_count > 0 && (
              <Alert className="bg-emerald-500/5 border-emerald-500/20">
                <CheckCircle2 className="h-4 w-4 text-emerald-500" />
                <AlertTitle className="text-emerald-700">Success!</AlertTitle>
                <AlertDescription className="text-emerald-600/80">
                  All contacts from your file have been successfully imported.
                </AlertDescription>
              </Alert>
            )}
          </div>
        )}

        <div className="flex justify-end gap-3 mt-4">
          {!results ? (
            <>
              <Button variant="ghost" onClick={() => handleClose(false)} disabled={importMutation.isPending}>
                Cancel
              </Button>
              <Button onClick={handleImport} disabled={!file || importMutation.isPending}>
                Confirm Import
              </Button>
            </>
          ) : (
            <Button onClick={() => handleClose(false)} className="w-full">
              Done
            </Button>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}
