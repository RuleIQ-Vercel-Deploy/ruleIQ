export const editorData = {
  metadata: {
    author: "Jane Doe",
    createdAt: "2024-06-15T10:30:00Z",
    lastModified: "2024-06-28T14:00:00Z",
    status: "In Review",
  },
  versions: [
    { id: 5, author: "Jane Doe", timestamp: "2024-06-28T14:00:00Z", summary: "Final review edits." },
    { id: 4, author: "John Smith", timestamp: "2024-06-28T11:20:00Z", summary: "Added legal section." },
    { id: 3, author: "Jane Doe", timestamp: "2024-06-27T18:05:00Z", summary: "Revised introduction." },
    { id: 2, author: "Jane Doe", timestamp: "2024-06-26T15:45:00Z", summary: "Initial draft." },
    { id: 1, author: "System", timestamp: "2024-06-26T15:00:00Z", summary: "Document created." },
  ],
  comments: [
    {
      id: "c1",
      author: "John Smith",
      avatar: "/placeholder.svg?height=32&width=32",
      timestamp: "2024-06-28T11:22:00Z",
      text: "Can we clarify the compliance requirements in this section?",
      replies: [
        {
          id: "r1",
          author: "Jane Doe",
          avatar: "/placeholder.svg?height=32&width=32",
          timestamp: "2024-06-28T12:15:00Z",
          text: "Good point. I'll add a reference to the ISO 27001 standard.",
        },
      ],
    },
    {
      id: "c2",
      author: "Alice Johnson",
      avatar: "/placeholder.svg?height=32&width=32",
      timestamp: "2024-06-28T09:30:00Z",
      text: "This paragraph looks great. No changes needed from my end.",
      replies: [],
    },
  ],
  initialContent: `
    <h1>Policy Document: Data Handling</h1>
    <p>This document outlines the official policy for handling sensitive company and customer data.</p>
    <h2>1. Introduction</h2>
    <p>Data is one of our most valuable assets. This policy ensures that we handle it with the utmost care and in compliance with all relevant regulations.</p>
    <h3>1.1. Scope</h3>
    <p>This policy applies to all employees, contractors, and partners who have access to company data.</p>
    <h2>2. Data Classification</h2>
    <p>Data is classified into three levels: Public, Internal, and Confidential.</p>
    <ul>
      <li><strong>Public:</strong> Information that can be freely shared.</li>
      <li><strong>Internal:</strong> Information for company-wide use.</li>
      <li><strong>Confidential:</strong> Information restricted to specific individuals or teams.</li>
    </ul>
    <h2>3. Security Measures</h2>
    <p>All confidential data must be encrypted both at rest and in transit.</p>
  `,
}
