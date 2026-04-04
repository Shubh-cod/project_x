import * as React from "react";
import { ChevronLeft, ChevronRight, ChevronDown, ChevronUp } from "lucide-react";
import { DayPicker, type DayButton, type Locale, type ChevronProps } from "react-day-picker";

import { cn } from "@/lib/utils";
import { Button, buttonVariants } from "@/components/ui/button";

export type CalendarProps = React.ComponentProps<typeof DayPicker> & {
  buttonVariant?: React.ComponentProps<typeof Button>["variant"];
};

function Calendar({
  className,
  classNames,
  showOutsideDays = true,
  buttonVariant = "ghost",
  locale,
  formatters,
  components,
  ...props
}: CalendarProps) {
  return (
    <DayPicker
      showOutsideDays={showOutsideDays}
      className={cn("p-3", className)}
      classNames={{
        months: "flex flex-col sm:flex-row space-y-4 sm:space-x-4 sm:space-y-0 relative",
        month: "space-y-4",
        month_caption: "flex justify-center pt-1 relative items-center h-10",
        caption_label: "text-sm font-medium",
        nav: "flex items-center",
        button_previous: cn(
          buttonVariants({ variant: "outline" }),
          "h-7 w-7 bg-transparent p-0 opacity-50 hover:opacity-100 absolute left-1 top-1 z-10",
        ),
        button_next: cn(
          buttonVariants({ variant: "outline" }),
          "h-7 w-7 bg-transparent p-0 opacity-50 hover:opacity-100 absolute right-1 top-1 z-10",
        ),
        month_grid: "w-full border-collapse",
        weekdays: "flex",
        weekday: "text-muted-foreground rounded-md w-9 font-normal text-[0.8rem] flex items-center justify-center",
        week: "flex w-full mt-2",
        day: "h-9 w-9 text-center text-sm p-0 relative [&:has([aria-selected].day-range-end)]:rounded-e-md [&:has([aria-selected].day-outside)]:bg-accent/50 [&:has([aria-selected])]:bg-accent first:[&:has([aria-selected])]:rounded-s-md last:[&:has([aria-selected])]:rounded-e-md focus-within:relative focus-within:z-20",
        day_button: cn(
          buttonVariants({ variant: buttonVariant }),
          "h-9 w-9 p-0 font-normal aria-selected:opacity-100",
        ),
        selected:
          "bg-primary text-primary-foreground hover:bg-primary hover:text-primary-foreground focus:bg-primary focus:text-primary-foreground",
        today: "bg-accent text-accent-foreground",
        outside:
          "day-outside text-muted-foreground opacity-50 aria-selected:bg-accent/50 aria-selected:text-muted-foreground aria-selected:opacity-30",
        disabled: "text-muted-foreground opacity-50",
        range_middle: "aria-selected:bg-accent aria-selected:text-accent-foreground",
        hidden: "invisible",
        ...classNames,
      }}
      components={{
        Chevron: ({ orientation, ..._props }: ChevronProps) => {
          const Icon =
            orientation === "left"
              ? ChevronLeft
              : orientation === "right"
                ? ChevronRight
                : orientation === "up"
                  ? ChevronUp
                  : ChevronDown;
          return <Icon className="h-4 w-4" />;
        },
        DayButton: ({ ..._props }) => <CalendarDayButton locale={locale} {..._props} />,
        ...components,
      }}
      formatters={{
        formatMonthDropdown: (date) => date.toLocaleString(locale?.code, { month: "short" }),
        ...formatters,
      }}
      locale={locale}
      {...props}
    />
  );
}
Calendar.displayName = "Calendar";

function CalendarDayButton({
  className,
  day,
  modifiers,
  locale,
  ...props
}: React.ComponentProps<typeof DayButton> & { locale?: Partial<Locale> }) {
  return (
    <Button
      variant="ghost"
      size="icon"
      className={cn(
        "h-9 w-9 p-0 font-normal aria-selected:opacity-100",
        modifiers.selected && "bg-primary text-primary-foreground",
        modifiers.today && "bg-accent text-accent-foreground",
        modifiers.outside && "text-muted-foreground opacity-50",
        modifiers.disabled && "text-muted-foreground opacity-50",
        modifiers.range_start && "rounded-s-md",
        modifiers.range_end && "rounded-e-md",
        className,
      )}
      data-day={day.date.toLocaleDateString(locale?.code)}
      {...props}
    />
  );
}

export { Calendar };
