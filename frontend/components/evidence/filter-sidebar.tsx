"use client"

import { addDays } from "date-fns"
import { CalendarIcon, Tag, ListFilter } from "lucide-react"
import * as React from "react"

import { Button } from "@/components/ui/button"
import { Calendar } from "@/components/ui/calendar"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Checkbox } from "@/components/ui/checkbox"
import { Label } from "@/components/ui/label"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { statuses, types, frameworks } from "@/lib/data/evidence"
import { cn } from "@/lib/utils"

import type { DateRange } from "react-day-picker"

export function FilterSidebar() {
  const [date, setDate] = React.useState<DateRange | undefined>({
    from: new Date(2024, 5, 1),
    to: addDays(new Date(2024, 5, 1), 30),
  })

  return (
    <Card className="ruleiq-card w-full lg:w-80 shrink-0 bg-midnight-blue border-gold/20">
      <CardHeader className="border-b border-gold/20">
        <CardTitle className="text-gold flex items-center gap-2">
          <ListFilter className="h-5 w-5" />
          Filters
        </CardTitle>
      </CardHeader>
      <CardContent className="p-6 space-y-6">
        {/* Status Filter */}
        <div className="space-y-3">
          <Label className="text-eggshell-white font-semibold">Status</Label>
          <div className="space-y-2">
            {statuses.map((status) => (
              <div key={status.value} className="flex items-center space-x-2">
                <Checkbox id={`status-${status.value}`} className="ruleiq-checkbox" />
                <Label htmlFor={`status-${status.value}`} className="text-eggshell-white/80 font-normal">
                  {status.label}
                </Label>
              </div>
            ))}
          </div>
        </div>

        {/* Type Filter */}
        <div className="space-y-3">
          <Label htmlFor="type-select" className="text-eggshell-white font-semibold">
            Type
          </Label>
          <Select>
            <SelectTrigger id="type-select" className="ruleiq-select-dark">
              <SelectValue placeholder="Select file type" />
            </SelectTrigger>
            <SelectContent className="bg-oxford-blue text-eggshell-white border-gold/50">
              {types.map((type) => (
                <SelectItem key={type.value} value={type.value}>
                  {type.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Date Range Filter */}
        <div className="space-y-3">
          <Label className="text-eggshell-white font-semibold">Date Range</Label>
          <Popover>
            <PopoverTrigger asChild>
              <Button
                id="date"
                variant={"outline"}
                className={cn(
                  "w-full justify-start text-left font-normal ruleiq-select-dark",
                  !date && "text-muted-foreground",
                )}
              >
                <CalendarIcon className="mr-2 h-4 w-4" />
                {date?.from ? (
                  date.to ? (
                    <>
                      {new Date(date.from).toLocaleDateString()} - {new Date(date.to).toLocaleDateString()}
                    </>
                  ) : (
                    new Date(date.from).toLocaleDateString()
                  )
                ) : (
                  <span>Pick a date</span>
                )}
              </Button>
            </PopoverTrigger>
            <PopoverContent className="w-auto p-0" align="start">
              <Calendar
                initialFocus
                mode="range"
                defaultMonth={date?.from}
                selected={date}
                onSelect={setDate}
                numberOfMonths={2}
              />
            </PopoverContent>
          </Popover>
        </div>

        {/* Framework Tags Filter */}
        <div className="space-y-3">
          <Label className="text-eggshell-white font-semibold flex items-center gap-2">
            <Tag className="h-4 w-4" />
            Framework Tags
          </Label>
          <div className="flex flex-wrap gap-2">
            {frameworks.map((framework) => (
              <Button
                key={framework.value}
                variant="secondary-ruleiq"
                size="small"
                className="bg-oxford-blue/80 text-eggshell-white/80 border-gold/30 hover:bg-gold/20"
              >
                {framework.label}
              </Button>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
