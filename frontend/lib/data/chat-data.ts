export type Message = {
  id: string
  text: string
  sender: "user" | "ai"
  timestamp: string
  suggestions?: string[]
}

export type Conversation = {
  id: string
  title: string
  messages: Message[]
}

export const conversations: Conversation[] = [
  {
    id: "conv-1",
    title: "SOC 2 Compliance Requirements",
    messages: [
      {
        id: "msg-1",
        text: "What are the main requirements for SOC 2 compliance?",
        sender: "user",
        timestamp: "10:30 AM",
      },
      {
        id: "msg-2",
        text: 'SOC 2 compliance is based on five Trust Services Criteria: Security, Availability, Processing Integrity, Confidentiality, and Privacy. The "Security" criterion is mandatory for all SOC 2 reports.',
        sender: "ai",
        timestamp: "10:31 AM",
        suggestions: [
          "Tell me more about the Security criterion.",
          "What is the difference between SOC 2 Type 1 and Type 2?",
          "How long does it take to get SOC 2 certified?",
        ],
      },
    ],
  },
  {
    id: "conv-2",
    title: "Data Encryption Policies",
    messages: [
      {
        id: "msg-3",
        text: "Can you help me draft a data encryption policy?",
        sender: "user",
        timestamp: "Yesterday",
      },
    ],
  },
  {
    id: "conv-3",
    title: "GDPR Data Subject Rights",
    messages: [
      {
        id: "msg-4",
        text: "What are the data subject rights under GDPR?",
        sender: "user",
        timestamp: "2 days ago",
      },
    ],
  },
]
