import React from "react";
import "../../../../styles/globals.css";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";

export default function CreateWireframePage() {
  return (
    <div className="min-h-[900px] w-full max-w-[1440px] mx-auto px-6 py-8 text-white">
      <header className="mb-6">
        <h1 className="text-3xl font-light tracking-tight">Create Wireframe</h1>
        <p className="opacity-75">High-level wireframe view rendered with vetted layout primitives.</p>
      </header>

      <div className="flex gap-4 mb-6">
        <Button className="btn-primary">Primary CTA</Button>
        <Button variant="outline" className="btn-secondary">Secondary CTA</Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="md:col-span-2 card">
          <CardHeader>
            <CardTitle>Card List</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <Card className="card"><CardContent>Item A</CardContent></Card>
              <Card className="card"><CardContent>Item B</CardContent></Card>
              <Card className="card"><CardContent>Item C</CardContent></Card>
              <Card className="card"><CardContent>Item D</CardContent></Card>
            </div>
          </CardContent>
        </Card>

        <Card className="card">
          <CardHeader>
            <CardTitle>Form Section</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <Input placeholder="Name" className="input" />
              <Textarea placeholder="Description" className="input" />
              <Button className="btn-primary">Submit</Button>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card className="mt-6 card">
        <CardHeader>
          <CardTitle>Data Table</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Column A</TableHead>
                <TableHead>Column B</TableHead>
                <TableHead>Column C</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              <TableRow>
                <TableCell>Alpha</TableCell>
                <TableCell>Beta</TableCell>
                <TableCell>Gamma</TableCell>
              </TableRow>
              <TableRow>
                <TableCell>Delta</TableCell>
                <TableCell>Epsilon</TableCell>
                <TableCell>Zeta</TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}