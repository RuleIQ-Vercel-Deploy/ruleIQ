import { Plus, Download, Save, MoreVertical, Wifi, WifiOff } from "lucide-react"

import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { useToast } from "@/hooks/use-toast"

interface ChatHeaderProps {
  title: string
  isConnected?: boolean
}

export function ChatHeader({ title, isConnected = false }: ChatHeaderProps) {
  const { toast } = useToast()

  const handleExport = (format: 'pdf' | 'txt' | 'json') => {
    // TODO: Implement actual export functionality
    toast({
      title: "Export Started",
      description: `Exporting conversation as ${format.toUpperCase()}...`,
    })
  }

  const handleSave = () => {
    // TODO: Implement actual save functionality
    toast({
      title: "Conversation Saved",
      description: "Your conversation has been saved successfully.",
    })
  }

  return (
    <div className="flex items-center justify-between p-4 border-b">
      <div className="flex items-center gap-3">
        <h2 className="text-lg font-semibold text-foreground">{title}</h2>
        <Badge 
          variant={isConnected ? "success" : "secondary"} 
          className="gap-1"
        >
          {isConnected ? (
            <>
              <Wifi className="h-3 w-3" />
              Connected
            </>
          ) : (
            <>
              <WifiOff className="h-3 w-3" />
              Offline
            </>
          )}
        </Badge>
      </div>
      <div className="flex items-center gap-2">
        <Button
          variant="outline"
          size="sm"
          onClick={handleSave}
          className="flex items-center gap-2"
        >
          <Save className="h-4 w-4" />
          Save
        </Button>
        
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button
              variant="outline"
              size="sm"
              className="flex items-center gap-2"
            >
              <Download className="h-4 w-4" />
              Export
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem onClick={() => handleExport('pdf')}>
              Export as PDF
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => handleExport('txt')}>
              Export as Text
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => handleExport('json')}>
              Export as JSON
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>

        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="icon" className="h-8 w-8">
              <MoreVertical className="h-4 w-4" />
              <span className="sr-only">More options</span>
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem>
              <Plus className="h-4 w-4 mr-2" />
              New Conversation
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem className="text-destructive">
              Clear Conversation
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </div>
  )
}
