declare module 'jspdf-autotable' {
  import { jsPDF } from 'jspdf'

  export interface AutoTableOptions {
    head?: any[][]
    body?: any[][]
    startY?: number
    margin?: { horizontal?: number; top?: number; bottom?: number }
    headStyles?: any
    alternateRowStyles?: any
    styles?: any
    columnStyles?: any
    theme?: 'striped' | 'grid' | 'plain'
  }

  export default function autoTable(doc: jsPDF, options: AutoTableOptions): void
}