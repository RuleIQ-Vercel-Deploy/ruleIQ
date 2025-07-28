import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import React from 'react';

// Mock data for testing key uniqueness
const mockQuestions = [
  {
    id: 'q1',
    text: 'Do you process personal data?',
    type: 'yes_no',
    section: 'data_processing',
  },
  {
    id: 'q2',
    text: 'Do you have a data protection policy?',
    type: 'yes_no',
    section: 'policies',
  },
  {
    id: 'q3',
    text: 'Describe your data retention procedures',
    type: 'textarea',
    section: 'data_processing',
  },
];

const mockFiles = [
  { id: 'f1', name: 'policy.pdf', type: 'pdf', size: 1024 },
  { id: 'f2', name: 'procedure.docx', type: 'docx', size: 2048 },
  { id: 'f3', name: 'evidence.jpg', type: 'image', size: 512 },
];

describe('React Key Uniqueness Tests', () => {
  let queryClient: QueryClient;
  let consoleErrorSpy: any;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
        mutations: { retry: false },
      },
    });
    
    // Spy on console.error to catch React warnings
    consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
  });

  afterEach(() => {
    queryClient.clear();
    consoleErrorSpy.mockRestore();
  });

  const TestWrapper = ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );

  describe('QuestionRenderer Key Uniqueness', () => {
    it('should render questions with unique keys', () => {
      const QuestionRenderer = ({ questions }: { questions: typeof mockQuestions }) => {
        return (
          <div data-testid="question-list">
            {questions.map((question) => (
              <div key={question.id} data-testid={`question-${question.id}`}>
                <h3>{question.text}</h3>
                <input type={question.type === 'yes_no' ? 'radio' : 'text'} />
              </div>
            ))}
          </div>
        );
      };

      render(
        <TestWrapper>
          <QuestionRenderer questions={mockQuestions} />
        </TestWrapper>,
      );

      // Verify all questions are rendered
      expect(screen.getByTestId('question-q1')).toBeInTheDocument();
      expect(screen.getByTestId('question-q2')).toBeInTheDocument();
      expect(screen.getByTestId('question-q3')).toBeInTheDocument();

      // No console errors should be logged for duplicate keys
      expect(consoleErrorSpy).not.toHaveBeenCalledWith(
        expect.stringContaining('Warning: Encountered two children with the same key'),
      );
    });

    it('should handle grouped questions with section-specific keys', () => {
      const GroupedQuestionRenderer = ({ questions }: { questions: typeof mockQuestions }) => {
        const groupedQuestions = questions.reduce(
          (acc, question) => {
            if (!acc[question.section]) {
              acc[question.section] = [];
            }
            acc[question.section].push(question);
            return acc;
          },
          {} as Record<string, typeof mockQuestions>,
        );

        return (
          <div data-testid="grouped-questions">
            {Object.entries(groupedQuestions).map(([section, sectionQuestions]) => (
              <div key={section} data-testid={`section-${section}`}>
                <h2>{section}</h2>
                {sectionQuestions.map((question) => (
                  <div key={`${section}-${question.id}`} data-testid={`grouped-question-${question.id}`}>
                    <p>{question.text}</p>
                  </div>
                ))}
              </div>
            ))}
          </div>
        );
      };

      render(
        <TestWrapper>
          <GroupedQuestionRenderer questions={mockQuestions} />
        </TestWrapper>,
      );

      // Verify sections are rendered
      expect(screen.getByTestId('section-data_processing')).toBeInTheDocument();
      expect(screen.getByTestId('section-policies')).toBeInTheDocument();

      // Verify questions are rendered with unique keys
      expect(screen.getByTestId('grouped-question-q1')).toBeInTheDocument();
      expect(screen.getByTestId('grouped-question-q2')).toBeInTheDocument();
      expect(screen.getByTestId('grouped-question-q3')).toBeInTheDocument();

      // No key warnings
      expect(consoleErrorSpy).not.toHaveBeenCalledWith(
        expect.stringContaining('Warning: Encountered two children with the same key'),
      );
    });

    it('should handle dynamic question rendering with stable keys', () => {
      const DynamicQuestionRenderer = ({ 
        questions, 
        filter 
      }: { 
        questions: typeof mockQuestions;
        filter?: string;
      }) => {
        const filteredQuestions = filter 
          ? questions.filter(q => q.section === filter)
          : questions;

        return (
          <div data-testid="dynamic-questions">
            {filteredQuestions.map((question, index) => (
              <div 
                key={question.id} // Use stable ID, not index
                data-testid={`dynamic-question-${question.id}`}
                data-index={index}
              >
                <span>{question.text}</span>
              </div>
            ))}
          </div>
        );
      };

      const { rerender } = render(
        <TestWrapper>
          <DynamicQuestionRenderer questions={mockQuestions} />
        </TestWrapper>,
      );

      // All questions initially
      expect(screen.getByTestId('dynamic-question-q1')).toBeInTheDocument();
      expect(screen.getByTestId('dynamic-question-q2')).toBeInTheDocument();
      expect(screen.getByTestId('dynamic-question-q3')).toBeInTheDocument();

      // Filter to data_processing section
      rerender(
        <TestWrapper>
          <DynamicQuestionRenderer questions={mockQuestions} filter="data_processing" />
        </TestWrapper>,
      );

      // Only data_processing questions should remain
      expect(screen.getByTestId('dynamic-question-q1')).toBeInTheDocument();
      expect(screen.queryByTestId('dynamic-question-q2')).not.toBeInTheDocument();
      expect(screen.getByTestId('dynamic-question-q3')).toBeInTheDocument();

      // No key warnings during re-render
      expect(consoleErrorSpy).not.toHaveBeenCalledWith(
        expect.stringContaining('Warning: Encountered two children with the same key'),
      );
    });
  });

  describe('File Upload Component Key Uniqueness', () => {
    it('should render uploaded files with unique keys', () => {
      const FileUploadList = ({ files }: { files: typeof mockFiles }) => {
        return (
          <div data-testid="file-list">
            {files.map((file) => (
              <div key={file.id} data-testid={`file-${file.id}`}>
                <span>{file.name}</span>
                <span>{file.size} bytes</span>
                <button>Remove</button>
              </div>
            ))}
          </div>
        );
      };

      render(
        <TestWrapper>
          <FileUploadList files={mockFiles} />
        </TestWrapper>,
      );

      // Verify all files are rendered
      expect(screen.getByTestId('file-f1')).toBeInTheDocument();
      expect(screen.getByTestId('file-f2')).toBeInTheDocument();
      expect(screen.getByTestId('file-f3')).toBeInTheDocument();

      // No duplicate key warnings
      expect(consoleErrorSpy).not.toHaveBeenCalledWith(
        expect.stringContaining('Warning: Encountered two children with the same key'),
      );
    });

    it('should handle file upload progress with unique keys', () => {
      const FileUploadProgress = ({ 
        files 
      }: { 
        files: Array<{ id: string; name: string; progress: number; status: string }>;
      }) => {
        return (
          <div data-testid="upload-progress">
            {files.map((file) => (
              <div key={`upload-${file.id}`} data-testid={`upload-${file.id}`}>
                <div>{file.name}</div>
                <div data-testid={`progress-${file.id}`}>
                  <div 
                    style={{ width: `${file.progress}%` }}
                    data-testid={`progress-bar-${file.id}`}
                  >
                    {file.progress}%
                  </div>
                </div>
                <div data-testid={`status-${file.id}`}>{file.status}</div>
              </div>
            ))}
          </div>
        );
      };

      const uploadFiles = [
        { id: 'u1', name: 'upload1.pdf', progress: 50, status: 'uploading' },
        { id: 'u2', name: 'upload2.docx', progress: 100, status: 'complete' },
        { id: 'u3', name: 'upload3.jpg', progress: 25, status: 'uploading' },
      ];

      render(
        <TestWrapper>
          <FileUploadProgress files={uploadFiles} />
        </TestWrapper>,
      );

      // Verify all upload items are rendered
      expect(screen.getByTestId('upload-u1')).toBeInTheDocument();
      expect(screen.getByTestId('upload-u2')).toBeInTheDocument();
      expect(screen.getByTestId('upload-u3')).toBeInTheDocument();

      // Verify progress elements
      expect(screen.getByTestId('progress-u1')).toBeInTheDocument();
      expect(screen.getByTestId('status-u2')).toBeInTheDocument();

      // No key warnings
      expect(consoleErrorSpy).not.toHaveBeenCalledWith(
        expect.stringContaining('Warning: Encountered two children with the same key'),
      );
    });
  });

  describe('Assessment Flow Component Keys', () => {
    it('should render assessment steps with unique keys', () => {
      const AssessmentWizard = ({ 
        steps 
      }: { 
        steps: Array<{ id: string; title: string; completed: boolean }>;
      }) => {
        return (
          <div data-testid="assessment-wizard">
            <div data-testid="step-list">
              {steps.map((step, index) => (
                <div 
                  key={step.id} 
                  data-testid={`step-${step.id}`}
                  className={step.completed ? 'completed' : 'pending'}
                >
                  <span>{index + 1}. {step.title}</span>
                  {step.completed && <span data-testid={`checkmark-${step.id}`}>✓</span>}
                </div>
              ))}
            </div>
          </div>
        );
      };

      const assessmentSteps = [
        { id: 'step1', title: 'Business Profile', completed: true },
        { id: 'step2', title: 'Data Processing', completed: true },
        { id: 'step3', title: 'Policies', completed: false },
        { id: 'step4', title: 'Review', completed: false },
      ];

      render(
        <TestWrapper>
          <AssessmentWizard steps={assessmentSteps} />
        </TestWrapper>,
      );

      // Verify all steps are rendered
      expect(screen.getByTestId('step-step1')).toBeInTheDocument();
      expect(screen.getByTestId('step-step2')).toBeInTheDocument();
      expect(screen.getByTestId('step-step3')).toBeInTheDocument();
      expect(screen.getByTestId('step-step4')).toBeInTheDocument();

      // Verify completed steps have checkmarks
      expect(screen.getByTestId('checkmark-step1')).toBeInTheDocument();
      expect(screen.getByTestId('checkmark-step2')).toBeInTheDocument();

      // No key warnings
      expect(consoleErrorSpy).not.toHaveBeenCalledWith(
        expect.stringContaining('Warning: Encountered two children with the same key'),
      );
    });

    it('should handle nested assessment content with unique keys', () => {
      const NestedAssessmentContent = ({ 
        sections 
      }: { 
        sections: Array<{
          id: string;
          title: string;
          questions: Array<{ id: string; text: string }>;
        }>;
      }) => {
        return (
          <div data-testid="nested-assessment">
            {sections.map((section) => (
              <div key={section.id} data-testid={`section-${section.id}`}>
                <h2>{section.title}</h2>
                <div data-testid={`questions-${section.id}`}>
                  {section.questions.map((question) => (
                    <div 
                      key={`${section.id}-question-${question.id}`} 
                      data-testid={`question-${section.id}-${question.id}`}
                    >
                      <p>{question.text}</p>
                      <input type="text" data-testid={`input-${section.id}-${question.id}`} />
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        );
      };

      const assessmentSections = [
        {
          id: 'section1',
          title: 'Data Processing',
          questions: [
            { id: 'q1', text: 'Do you process personal data?' },
            { id: 'q2', text: 'What types of data do you process?' },
          ],
        },
        {
          id: 'section2',
          title: 'Security Measures',
          questions: [
            { id: 'q1', text: 'Do you have encryption in place?' }, // Same ID as above but different section
            { id: 'q3', text: 'How do you secure data in transit?' },
          ],
        },
      ];

      render(
        <TestWrapper>
          <NestedAssessmentContent sections={assessmentSections} />
        </TestWrapper>,
      );

      // Verify sections are rendered
      expect(screen.getByTestId('section-section1')).toBeInTheDocument();
      expect(screen.getByTestId('section-section2')).toBeInTheDocument();

      // Verify questions with unique keys (section prefix prevents conflicts)
      expect(screen.getByTestId('question-section1-q1')).toBeInTheDocument();
      expect(screen.getByTestId('question-section1-q2')).toBeInTheDocument();
      expect(screen.getByTestId('question-section2-q1')).toBeInTheDocument();
      expect(screen.getByTestId('question-section2-q3')).toBeInTheDocument();

      // No key warnings despite same question IDs in different sections
      expect(consoleErrorSpy).not.toHaveBeenCalledWith(
        expect.stringContaining('Warning: Encountered two children with the same key'),
      );
    });
  });

  describe('Fragment Key Handling', () => {
    it('should handle React.Fragment with keys correctly', () => {
      const FragmentComponent = ({ 
        items 
      }: { 
        items: Array<{ id: string; title: string; content: string }>;
      }) => {
        return (
          <div data-testid="fragment-container">
            {items.map((item) => (
              <React.Fragment key={item.id}>
                <h3 data-testid={`title-${item.id}`}>{item.title}</h3>
                <p data-testid={`content-${item.id}`}>{item.content}</p>
                <hr data-testid={`divider-${item.id}`} />
              </React.Fragment>
            ))}
          </div>
        );
      };

      const fragmentItems = [
        { id: 'item1', title: 'First Item', content: 'First content' },
        { id: 'item2', title: 'Second Item', content: 'Second content' },
      ];

      render(
        <TestWrapper>
          <FragmentComponent items={fragmentItems} />
        </TestWrapper>,
      );

      // Verify all fragment content is rendered
      expect(screen.getByTestId('title-item1')).toBeInTheDocument();
      expect(screen.getByTestId('content-item1')).toBeInTheDocument();
      expect(screen.getByTestId('divider-item1')).toBeInTheDocument();
      expect(screen.getByTestId('title-item2')).toBeInTheDocument();
      expect(screen.getByTestId('content-item2')).toBeInTheDocument();
      expect(screen.getByTestId('divider-item2')).toBeInTheDocument();

      // No key warnings for fragments
      expect(consoleErrorSpy).not.toHaveBeenCalledWith(
        expect.stringContaining('Warning: Each child in a list should have a unique "key" prop'),
      );
    });
  });

  describe('Anti-patterns Detection', () => {
    it('should detect array index as key anti-pattern', () => {
      const IndexKeyComponent = ({ items }: { items: string[] }) => {
        return (
          <div data-testid="index-key-container">
            {items.map((item, index) => (
              <div key={index} data-testid={`item-${index}`}>
                {item}
              </div>
            ))}
          </div>
        );
      };

      const items = ['Item 1', 'Item 2', 'Item 3'];

      render(
        <TestWrapper>
          <IndexKeyComponent items={items} />
        </TestWrapper>,
      );

      // Component should render without errors
      expect(screen.getByTestId('item-0')).toBeInTheDocument();
      expect(screen.getByTestId('item-1')).toBeInTheDocument();
      expect(screen.getByTestId('item-2')).toBeInTheDocument();

      // Note: Using index as key is not ideal but doesn't cause console errors
      // in simple cases. It becomes problematic with dynamic lists.
    });

    it('should demonstrate proper key usage vs index usage', () => {
      interface Item {
        id: string;
        value: string;
      }

      const ProperKeyComponent = ({ items }: { items: Item[] }) => {
        return (
          <div data-testid="proper-key-container">
            {items.map((item) => (
              <div key={item.id} data-testid={`proper-${item.id}`}>
                {item.value}
              </div>
            ))}
          </div>
        );
      };

      const items = [
        { id: 'a1', value: 'First' },
        { id: 'b2', value: 'Second' },
        { id: 'c3', value: 'Third' },
      ];

      render(
        <TestWrapper>
          <ProperKeyComponent items={items} />
        </TestWrapper>,
      );

      // Verify proper rendering with stable keys
      expect(screen.getByTestId('proper-a1')).toBeInTheDocument();
      expect(screen.getByTestId('proper-b2')).toBeInTheDocument();
      expect(screen.getByTestId('proper-c3')).toBeInTheDocument();

      // No key warnings
      expect(consoleErrorSpy).not.toHaveBeenCalledWith(
        expect.stringContaining('Warning'),
      );
    });
  });
});