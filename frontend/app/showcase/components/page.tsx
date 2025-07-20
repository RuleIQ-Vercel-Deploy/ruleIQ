"use client"

import { useState } from "react"

import { AssessmentCard } from "@/components/ui/assessment-card"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Checkbox } from "@/components/ui/checkbox"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { ResponsiveTable } from "@/components/ui/responsive-table"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { Typography } from "@/components/ui/typography"

export default function ComponentShowcasePage() {
  const [selectedRow, setSelectedRow] = useState<number | null>(null)
  
  // Sample data for tables
  const tableData = [
    { id: 1, name: "John Doe", email: "john@example.com", role: "Admin", status: "Active" },
    { id: 2, name: "Jane Smith", email: "jane@example.com", role: "User", status: "Active" },
    { id: 3, name: "Bob Johnson", email: "bob@example.com", role: "User", status: "Inactive" },
    { id: 4, name: "Alice Brown", email: "alice@example.com", role: "Manager", status: "Active" },
  ]

  const responsiveColumns = [
    {
      key: "name",
      header: "Name",
      accessor: (row: any) => row.name,
      priority: "high" as const,
    },
    {
      key: "email",
      header: "Email",
      accessor: (row: any) => row.email,
      priority: "high" as const,
    },
    {
      key: "role",
      header: "Role",
      accessor: (row: any) => row.role,
      priority: "medium" as const,
    },
    {
      key: "status",
      header: "Status",
      accessor: (row: any) => (
        <span className={row.status === "Active" ? "text-success-600" : "text-neutral-500"}>
          {row.status}
        </span>
      ),
      priority: "low" as const,
    },
  ]

  return (
    <div className="min-h-screen bg-neutral-50 p-8">
      <div className="mx-auto max-w-7xl space-y-12">
        <Typography variant="h1">Component Showcase</Typography>

        {/* Form Controls Section */}
        <section className="space-y-6">
          <Typography variant="h2">Form Controls</Typography>
          
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {/* Input States */}
            <Card>
              <CardHeader>
                <CardTitle>Input States</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label htmlFor="input-default">Default</Label>
                  <Input id="input-default" data-testid="input-default" placeholder="Enter text" />
                </div>
                <div>
                  <Label htmlFor="input-error">Error</Label>
                  <Input id="input-error" data-testid="input-error" error placeholder="Error state" />
                </div>
                <div>
                  <Label htmlFor="input-success">Success</Label>
                  <Input id="input-success" data-testid="input-success" success placeholder="Success state" />
                </div>
                <div>
                  <Label htmlFor="input-disabled">Disabled</Label>
                  <Input id="input-disabled" data-testid="input-disabled" disabled placeholder="Disabled" />
                </div>
              </CardContent>
            </Card>

            {/* Select States */}
            <Card>
              <CardHeader>
                <CardTitle>Select States</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label htmlFor="select-default">Default</Label>
                  <Select>
                    <SelectTrigger id="select-default" data-testid="select-default">
                      <SelectValue placeholder="Select option" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="1">Option 1</SelectItem>
                      <SelectItem value="2">Option 2</SelectItem>
                      <SelectItem value="3">Option 3</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label htmlFor="select-error">Error</Label>
                  <Select>
                    <SelectTrigger id="select-error" data-testid="select-error" error>
                      <SelectValue placeholder="Error state" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="1">Option 1</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </CardContent>
            </Card>

            {/* Checkbox & Radio */}
            <Card>
              <CardHeader>
                <CardTitle>Checkbox & Radio</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <div className="flex items-center space-x-2">
                    <Checkbox id="checkbox-default" data-testid="checkbox-default" />
                    <Label htmlFor="checkbox-default">Default checkbox</Label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Checkbox id="checkbox-focus" data-testid="checkbox-focus" />
                    <Label htmlFor="checkbox-focus">Focus me</Label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Checkbox id="checkbox-error" data-testid="checkbox-error" error defaultChecked />
                    <Label htmlFor="checkbox-error">Error state</Label>
                  </div>
                </div>
                
                <RadioGroup data-testid="radio-group" defaultValue="1">
                  <div className="flex items-center space-x-2">
                    <RadioGroupItem value="1" id="r1" data-testid="radio-option-1" />
                    <Label htmlFor="r1">Option 1</Label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <RadioGroupItem value="2" id="r2" data-testid="radio-option-2" />
                    <Label htmlFor="r2">Option 2</Label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <RadioGroupItem value="3" id="r3" data-testid="radio-option-3" />
                    <Label htmlFor="r3">Option 3</Label>
                  </div>
                </RadioGroup>
              </CardContent>
            </Card>
          </div>
        </section>

        {/* Cards Section */}
        <section className="space-y-6">
          <Typography variant="h2">Cards</Typography>
          
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            <Card data-testid="card-default">
              <CardHeader>
                <CardTitle>Default Card</CardTitle>
                <CardDescription>This is a simple card with minimal content</CardDescription>
              </CardHeader>
              <CardContent>
                <p>Card content goes here.</p>
              </CardContent>
            </Card>

            <Card data-testid="card-hover" className="cursor-pointer">
              <CardHeader>
                <CardTitle>Hover Me</CardTitle>
                <CardDescription>This card has hover effects</CardDescription>
              </CardHeader>
              <CardContent>
                <p>Hover to see the shadow change.</p>
              </CardContent>
            </Card>

            <Card data-testid="card-complete">
              <CardHeader>
                <CardTitle>Complete Card</CardTitle>
                <CardDescription>All card sections are used</CardDescription>
              </CardHeader>
              <CardContent>
                <p>This card demonstrates all available sections.</p>
              </CardContent>
              <CardFooter className="flex justify-between">
                <Button variant="ghost">Cancel</Button>
                <Button>Save</Button>
              </CardFooter>
            </Card>
          </div>

          {/* Assessment Cards */}
          <div className="grid gap-6 md:grid-cols-2">
            <AssessmentCard
              data-testid="assessment-not-started"
              title="ISO 27001 Compliance"
              description="Information security management assessment"
              status="not-started"
              framework="ISO 27001:2022"
              dueDate="Dec 31, 2024"
              progress={0}
            />
            
            <AssessmentCard
              data-testid="assessment-in-progress"
              title="GDPR Readiness"
              description="General Data Protection Regulation compliance check"
              status="in-progress"
              framework="GDPR"
              dueDate="Nov 15, 2024"
              progress={45}
            />
            
            <AssessmentCard
              data-testid="assessment-completed"
              title="SOC 2 Type II"
              description="Service Organization Control audit"
              status="completed"
              framework="SOC 2"
              progress={100}
            />
            
            <AssessmentCard
              data-testid="assessment-expired"
              title="HIPAA Assessment"
              description="Health Insurance Portability and Accountability Act"
              status="expired"
              framework="HIPAA"
              dueDate="Sep 30, 2024"
              progress={72}
            />
          </div>
        </section>

        {/* Tables Section */}
        <section className="space-y-6">
          <Typography variant="h2">Tables</Typography>
          
          <Card>
            <CardHeader>
              <CardTitle>Standard Table</CardTitle>
            </CardHeader>
            <CardContent>
              <Table data-testid="table-default">
                <TableHeader>
                  <TableRow>
                    <TableHead>Name</TableHead>
                    <TableHead>Email</TableHead>
                    <TableHead>Role</TableHead>
                    <TableHead>Status</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {tableData.map((row) => (
                    <TableRow
                      key={row.id}
                      data-state={selectedRow === row.id ? "selected" : undefined}
                      onClick={() => setSelectedRow(row.id)}
                      className="cursor-pointer"
                    >
                      <TableCell>{row.name}</TableCell>
                      <TableCell>{row.email}</TableCell>
                      <TableCell>{row.role}</TableCell>
                      <TableCell>
                        <span className={row.status === "Active" ? "text-success-600" : "text-neutral-500"}>
                          {row.status}
                        </span>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Responsive Table - Horizontal Scroll</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveTable
                data-testid="table-scroll"
                columns={responsiveColumns}
                data={tableData}
                mobileLayout="scroll"
              />
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Responsive Table - Stacked Layout</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveTable
                data-testid="table-stacked"
                columns={responsiveColumns}
                data={tableData}
                mobileLayout="stack"
              />
            </CardContent>
          </Card>
        </section>

        {/* All Components Together */}
        <section data-testid="all-components" className="space-y-6">
          <Typography variant="h2">All Components</Typography>
          <div className="grid gap-6 md:grid-cols-2">
            <Card data-testid="dark-form-controls">
              <CardHeader>
                <CardTitle>Form Controls</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <Input placeholder="Sample input" />
                <Select>
                  <SelectTrigger>
                    <SelectValue placeholder="Select option" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="1">Option 1</SelectItem>
                  </SelectContent>
                </Select>
                <div className="flex items-center space-x-2">
                  <Checkbox id="terms" />
                  <Label htmlFor="terms">Accept terms</Label>
                </div>
                <Button>Submit</Button>
              </CardContent>
            </Card>

            <Card data-testid="dark-cards">
              <CardHeader>
                <CardTitle>Sample Card</CardTitle>
                <CardDescription>Card description text</CardDescription>
              </CardHeader>
              <CardContent>
                <p>Card content with some text.</p>
              </CardContent>
            </Card>
          </div>

          <Card data-testid="dark-table">
            <CardContent className="p-0">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Column 1</TableHead>
                    <TableHead>Column 2</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  <TableRow>
                    <TableCell>Data 1</TableCell>
                    <TableCell>Data 2</TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </section>

        {/* Responsive Showcase */}
        <section data-testid="responsive-showcase" className="space-y-6">
          <Typography variant="h2">Responsive Showcase</Typography>
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <Card key={i}>
                <CardHeader>
                  <CardTitle>Card {i}</CardTitle>
                </CardHeader>
                <CardContent>
                  <p>Responsive grid item</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </section>

        {/* Theme Toggle (for dark mode testing) */}
        <Button
          data-testid="theme-toggle"
          variant="outline"
          className="fixed bottom-4 right-4"
          onClick={() => document.documentElement.classList.toggle("dark")}
        >
          Toggle Theme
        </Button>
      </div>
    </div>
  )
}