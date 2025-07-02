export const frameworkOptions = [
  { value: "iso-27001", label: "ISO 27001" },
  { value: "soc-2", label: "SOC 2" },
  { value: "gdpr", label: "GDPR" },
  { value: "hipaa", label: "HIPAA" },
  { value: "pci-dss", label: "PCI DSS" },
]

export const controlMappingOptions = {
  "iso-27001": [
    { value: "a.5.1", label: "A.5.1 - Policies for information security" },
    { value: "a.6.1", label: "A.6.1 - Information security roles and responsibilities" },
    { value: "a.8.1", label: "A.8.1 - Asset management" },
  ],
  "soc-2": [
    { value: "cc6.1", label: "CC6.1 - Risk Assessment" },
    { value: "cc7.1", label: "CC7.1 - System Operations" },
    { value: "cc8.1", label: "CC8.1 - Change Management" },
  ],
  gdpr: [
    { value: "art-30", label: "Article 30 - Records of processing activities" },
    { value: "art-32", label: "Article 32 - Security of processing" },
    { value: "art-35", label: "Article 35 - Data protection impact assessment" },
  ],
  hipaa: [
    { value: "164.308", label: "§164.308 - Administrative safeguards" },
    { value: "164.310", label: "§164.310 - Physical safeguards" },
    { value: "164.312", label: "§164.312 - Technical safeguards" },
  ],
  "pci-dss": [
    { value: "req-1", label: "Req 1: Install and maintain a firewall" },
    { value: "req-3", label: "Req 3: Protect stored cardholder data" },
    { value: "req-8", label: "Req 8: Assign a unique ID to each person with computer access" },
  ],
}
