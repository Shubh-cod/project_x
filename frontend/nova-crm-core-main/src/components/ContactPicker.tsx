import { useState, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { Check, ChevronsUpDown, Users } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "@/components/ui/command";
import { contactsApi } from "@/api/contacts.api";
import { useDebounce } from "@/hooks/use-debounce";
import type { Contact } from "@/api/types";

interface ContactPickerProps {
  value: string; // contact_id (UUID)
  onChange: (contactId: string) => void;
  disabled?: boolean;
}

export function ContactPicker({ value, onChange, disabled }: ContactPickerProps) {
  const [open, setOpen] = useState(false);
  const [search, setSearch] = useState("");
  const debouncedSearch = useDebounce(search, 250);

  // Fetch contacts based on search
  const { data, isLoading } = useQuery({
    queryKey: ["contacts-picker", debouncedSearch],
    queryFn: () => contactsApi.list({ name: debouncedSearch || undefined, page_size: "50" }),
    enabled: open, // only fetch when popover is open
  });

  // Fetch the selected contact details for display (when we have a value but popover is closed)
  const { data: selectedContact } = useQuery({
    queryKey: ["contact-detail", value],
    queryFn: () => contactsApi.get(value),
    enabled: !!value,
  });

  const contacts = data?.items || [];

  const displayLabel = selectedContact
    ? `${selectedContact.name}${selectedContact.company ? ` · ${selectedContact.company}` : ""}`
    : value
      ? "Loading..."
      : "Select a contact...";

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button
          variant="outline"
          role="combobox"
          aria-expanded={open}
          disabled={disabled}
          className={cn(
            "w-full justify-between font-normal",
            !value && "text-muted-foreground"
          )}
        >
          <span className="flex items-center gap-2 truncate">
            <Users className="h-3.5 w-3.5 shrink-0 opacity-60" />
            <span className="truncate">{displayLabel}</span>
          </span>
          <ChevronsUpDown className="ml-2 h-3.5 w-3.5 shrink-0 opacity-50" />
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-[--radix-popover-trigger-width] p-0" align="start">
        <Command shouldFilter={false}>
          <CommandInput
            placeholder="Search contacts by name..."
            value={search}
            onValueChange={setSearch}
          />
          <CommandList>
            {isLoading ? (
              <div className="flex items-center justify-center py-6">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary" />
              </div>
            ) : (
              <>
                <CommandEmpty>No contacts found.</CommandEmpty>
                <CommandGroup>
                  {contacts.map((contact: Contact) => (
                    <CommandItem
                      key={contact.id}
                      value={contact.id}
                      onSelect={() => {
                        onChange(contact.id);
                        setOpen(false);
                        setSearch("");
                      }}
                      className="flex items-center gap-3 py-2.5 cursor-pointer"
                    >
                      {/* Avatar */}
                      <div className="h-7 w-7 rounded-full bg-primary/10 flex items-center justify-center text-[10px] font-semibold text-primary shrink-0">
                        {contact.name
                          .split(" ")
                          .map((n) => n[0])
                          .join("")
                          .toUpperCase()}
                      </div>
                      {/* Info */}
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium truncate">{contact.name}</p>
                        <p className="text-xs text-muted-foreground truncate">
                          {contact.email}
                          {contact.company ? ` · ${contact.company}` : ""}
                        </p>
                      </div>
                      {/* Checkmark */}
                      <Check
                        className={cn(
                          "h-4 w-4 shrink-0",
                          value === contact.id ? "opacity-100 text-primary" : "opacity-0"
                        )}
                      />
                    </CommandItem>
                  ))}
                </CommandGroup>
              </>
            )}
          </CommandList>
        </Command>
      </PopoverContent>
    </Popover>
  );
}
