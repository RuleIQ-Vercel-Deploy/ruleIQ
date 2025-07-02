export const assessmentData = {
  id: "ASM-001",
  title: "Q1 2024 GDPR Data Protection Audit",
  sections: [
    {
      id: "data-processing",
      title: "Data Processing Activities",
      progress: 75,
      questions: [
        {
          id: "q1",
          text: "Do you maintain a record of processing activities (ROPA) as required by Article 30 of GDPR?",
          helperText:
            "This record should detail the purposes of processing, categories of data subjects, and data transfers.",
          type: "radio",
          options: ["Yes", "No", "Not Applicable"],
        },
        {
          id: "q2",
          text: "Describe the lawful basis for processing personal data for your primary business activities.",
          helperText: "e.g., Consent, Contract, Legal Obligation, Vital Interests, Public Task, Legitimate Interests.",
          type: "textarea",
          placeholder: "Provide a detailed explanation of your lawful basis...",
        },
      ],
    },
    {
      id: "data-subject-rights",
      title: "Data Subject Rights",
      progress: 50,
      questions: [
        {
          id: "q3",
          text: "What procedures are in place to handle Data Subject Access Requests (DSARs)?",
          helperText: "Select all that apply. Ensure you have a documented process.",
          type: "checkbox",
          options: [
            "Dedicated email address or portal",
            "Internal request logging system",
            "Identity verification process",
            "Standard response templates",
            "Process for data redaction",
          ],
        },
        {
          id: "q4",
          text: "How do you ensure the right to erasure (right to be forgotten) is respected?",
          helperText: "Describe the technical and organizational measures in place.",
          type: "textarea",
          placeholder: "e.g., Data deletion from production and backup systems, notification to third parties...",
        },
      ],
    },
    {
      id: "security-measures",
      title: "Security Measures",
      progress: 20,
      questions: [
        {
          id: "q5",
          text: "Is personal data encrypted at rest and in transit?",
          helperText: "Specify the encryption standards used (e.g., AES-256, TLS 1.2+).",
          type: "radio",
          options: ["Yes, both", "At rest only", "In transit only", "No"],
        },
      ],
    },
    {
      id: "data-breaches",
      title: "Data Breaches",
      progress: 0,
      questions: [
        {
          id: "q6",
          text: "Do you have a documented data breach notification procedure?",
          helperText:
            "This should include timelines for notifying supervisory authorities (e.g., ICO) and affected individuals.",
          type: "radio",
          options: ["Yes", "No"],
        },
      ],
    },
    {
      id: "third-party-risk",
      title: "Third-Party Risk",
      progress: 0,
      questions: [
        {
          id: "q7",
          text: "How do you assess the GDPR compliance of third-party vendors who process personal data on your behalf?",
          helperText: "e.g., Data Processing Agreements (DPAs), vendor security questionnaires, audits.",
          type: "textarea",
          placeholder: "Describe your vendor due diligence process...",
        },
      ],
    },
  ],
}

export type AssessmentSection = (typeof assessmentData.sections)[0]
export type AssessmentQuestion = (typeof assessmentData.sections)[0]["questions"][0]
