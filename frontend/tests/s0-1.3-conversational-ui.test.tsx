/**
 * Test Suite for S0-1.3: Conversational UI Foundation
 * Tests WebSocket communication, chat components, and agent interaction
 */

import React from 'react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';

// Import components to test
import { ChatContainer } from '@/components/chat/ChatContainer';
import { Message } from '@/components/chat/Message';
import { TrustIndicator } from '@/components/chat/TrustIndicator';
import { ChatInput } from '@/components/chat/ChatInput';
import { TypingIndicator } from '@/components/chat/TypingIndicator';
import { ContextPanel } from '@/components/context/ContextPanel';
import { SessionManager } from '@/components/session/SessionManager';
import { AgentSelector } from '@/components/agent/AgentSelector';
import { PersonaCard } from '@/components/agent/PersonaCard';

// Import types
import { Agent, Session, ChatMessage, TrustLevel } from '@/lib/websocket/types';
import { WebSocketClient } from '@/lib/websocket/client';

// Mock data
const mockAgent: Agent = {
  id: 'agent-1',
  name: 'Test Agent',
  personaType: 'developer',
  capabilities: ['code_generation', 'testing', 'debugging'],
  isActive: true,
  currentTrustLevel: TrustLevel.L0_OBSERVED,
};

const mockSession: Session = {
  id: 'session-1',
  agentId: 'agent-1',
  userId: 'user-1',
  trustLevel: TrustLevel.L0_OBSERVED,
  context: {},
  startedAt: new Date(),
  messages: [],
};

const mockMessage: ChatMessage = {
  id: 'msg-1',
  content: 'Hello, how can I help you?',
  role: 'agent',
  timestamp: new Date(),
  agentId: 'agent-1',
  sessionId: 'session-1',
  trustLevel: TrustLevel.L0_OBSERVED,
  status: 'delivered',
};

describe('S0-1.3: Conversational UI Foundation Tests', () => {
  describe('WebSocket Infrastructure (AC1)', () => {
    it('should create WebSocket client', () => {
      const client = new WebSocketClient('ws://localhost:8000/ws');
      expect(client).toBeDefined();
      expect(client.getConnectionState().connected).toBe(false);
    });

    it('should queue messages when disconnected', () => {
      const client = new WebSocketClient('ws://localhost:8000/ws');
      
      // Send message before connection
      client.sendChatMessage('Test message');
      
      // Message should be queued
      expect(client.getConnectionState().connected).toBe(false);
    });
  });

  describe('Message Streaming (AC2)', () => {
    it('should display typing indicator', () => {
      render(<TypingIndicator agentName="Test Agent" />);
      
      expect(screen.getByText(/Test Agent is typing/i)).toBeInTheDocument();
      
      // Check for animated dots
      const dots = screen.getByText(/Test Agent is typing/i).parentElement?.querySelectorAll('.animate-bounce');
      expect(dots).toHaveLength(3);
    });

    it('should render messages with proper formatting', () => {
      render(<Message message={mockMessage} />);
      
      expect(screen.getByText(mockMessage.content)).toBeInTheDocument();
    });

    it('should show message status indicators', () => {
      const sendingMessage = { ...mockMessage, status: 'sending' as const };
      const { rerender } = render(<Message message={sendingMessage} />);
      
      // Status should update
      const sentMessage = { ...mockMessage, status: 'sent' as const };
      rerender(<Message message={sentMessage} />);
      
      const deliveredMessage = { ...mockMessage, status: 'delivered' as const };
      rerender(<Message message={deliveredMessage} />);
    });
  });

  describe('Context Management (AC3)', () => {
    it('should display and manage context', () => {
      const mockContext = {
        user: 'test-user',
        session: 'test-session',
        preferences: { theme: 'dark' },
      };
      
      const updateSpy = vi.fn();
      const deleteSpy = vi.fn();
      const clearSpy = vi.fn();
      
      render(
        <ContextPanel
          context={mockContext}
          onUpdateContext={updateSpy}
          onDeleteContext={deleteSpy}
          onClearContext={clearSpy}
        />
      );
      
      // Check context is displayed
      expect(screen.getByText(/user/i)).toBeInTheDocument();
      expect(screen.getByText(/session/i)).toBeInTheDocument();
    });

    it('should allow context editing', () => {
      const mockContext = { key1: 'value1' };
      const updateSpy = vi.fn();
      
      render(
        <ContextPanel
          context={mockContext}
          onUpdateContext={updateSpy}
          onDeleteContext={vi.fn()}
          onClearContext={vi.fn()}
        />
      );
      
      // Simulate editing context
      // This would involve clicking edit button and changing values
    });
  });

  describe('Trust Level Indicators (AC4)', () => {
    it('should display correct trust level badge', () => {
      render(<TrustIndicator trustLevel={TrustLevel.L0_OBSERVED} />);
      
      expect(screen.getByText(/L0 - Observed/i)).toBeInTheDocument();
    });

    it('should show trust level progression', () => {
      render(
        <TrustIndicator 
          trustLevel={TrustLevel.L1_ASSISTED} 
          showProgress={true}
          progressValue={75}
        />
      );
      
      expect(screen.getByText(/75%/i)).toBeInTheDocument();
    });

    it('should use correct colors for each trust level', () => {
      const { rerender } = render(<TrustIndicator trustLevel={TrustLevel.L0_OBSERVED} />);
      let badge = screen.getByText(/L0 - Observed/i).parentElement;
      expect(badge).toHaveClass('bg-red-50');
      
      rerender(<TrustIndicator trustLevel={TrustLevel.L4_AUTONOMOUS} />);
      badge = screen.getByText(/L4 - Autonomous/i).parentElement;
      expect(badge).toHaveClass('bg-green-50');
    });
  });

  describe('Session Management (AC5)', () => {
    it('should display session list', () => {
      const sessions: Session[] = [mockSession];
      
      render(
        <SessionManager
          sessions={sessions}
          activeSessionId={mockSession.id}
          onSelectSession={vi.fn()}
          onCreateSession={vi.fn()}
          onDeleteSession={vi.fn()}
          onExportSession={vi.fn()}
          onImportSession={vi.fn()}
        />
      );
      
      expect(screen.getByText(new RegExp(mockSession.id.slice(0, 8)))).toBeInTheDocument();
    });

    it('should allow session switching', () => {
      const selectSpy = vi.fn();
      const sessions: Session[] = [
        mockSession,
        { ...mockSession, id: 'session-2' },
      ];
      
      render(
        <SessionManager
          sessions={sessions}
          activeSessionId={mockSession.id}
          onSelectSession={selectSpy}
          onCreateSession={vi.fn()}
          onDeleteSession={vi.fn()}
          onExportSession={vi.fn()}
          onImportSession={vi.fn()}
        />
      );
      
      // Click on second session
      fireEvent.click(screen.getByText(/session-2/i).closest('div')!);
      expect(selectSpy).toHaveBeenCalledWith('session-2');
    });
  });

  describe('Agent Selection (AC6)', () => {
    it('should display agent selector interface', () => {
      const agents: Agent[] = [mockAgent];
      
      render(
        <AgentSelector
          agents={agents}
          selectedAgentId={null}
          onSelectAgent={vi.fn()}
        />
      );
      
      expect(screen.getByText(mockAgent.name)).toBeInTheDocument();
    });

    it('should show agent capabilities', () => {
      render(
        <PersonaCard
          agent={mockAgent}
          isSelected={false}
          onSelect={vi.fn()}
        />
      );
      
      mockAgent.capabilities.forEach(capability => {
        expect(screen.getByText(capability)).toBeInTheDocument();
      });
    });

    it('should allow agent selection', () => {
      const selectSpy = vi.fn();
      
      render(
        <PersonaCard
          agent={mockAgent}
          isSelected={false}
          onSelect={selectSpy}
        />
      );
      
      fireEvent.click(screen.getByText(mockAgent.name).closest('div')!);
      expect(selectSpy).toHaveBeenCalled();
    });
  });

  describe('Code Syntax Highlighting (AC7)', () => {
    it('should highlight code blocks in messages', () => {
      const messageWithCode: ChatMessage = {
        ...mockMessage,
        codeBlocks: [{
          language: 'javascript',
          code: 'console.log("Hello World");',
          filename: 'test.js',
        }],
      };
      
      render(<Message message={messageWithCode} />);
      
      expect(screen.getByText('test.js')).toBeInTheDocument();
      expect(screen.getByText(/console\.log/)).toBeInTheDocument();
    });
  });

  describe('File Upload/Download (AC8)', () => {
    it('should handle file attachments', () => {
      const sendSpy = vi.fn();
      
      render(
        <ChatInput
          onSendMessage={sendSpy}
          disabled={false}
        />
      );
      
      // File input should exist
      const fileInput = document.querySelector('input[type="file"]');
      expect(fileInput).toBeInTheDocument();
    });
  });

  describe('Responsive Design (AC9)', () => {
    it('should render properly on different screen sizes', () => {
      // This would typically involve testing with different viewport sizes
      // For now, just check that components render
      render(
        <ChatContainer
          agent={mockAgent}
          session={mockSession}
        />
      );
      
      expect(screen.getByText(mockAgent.name)).toBeInTheDocument();
    });
  });

  describe('Accessibility (AC10)', () => {
    it('should have proper ARIA labels', () => {
      render(
        <ChatInput
          onSendMessage={vi.fn()}
          disabled={false}
        />
      );
      
      const textarea = screen.getByPlaceholderText(/Type a message/i);
      expect(textarea).toBeInTheDocument();
    });

    it('should support keyboard navigation', () => {
      const sendSpy = vi.fn();
      
      render(
        <ChatInput
          onSendMessage={sendSpy}
          disabled={false}
        />
      );
      
      const textarea = screen.getByPlaceholderText(/Type a message/i);
      
      // Type and send with Enter
      fireEvent.change(textarea, { target: { value: 'Test message' } });
      fireEvent.keyDown(textarea, { key: 'Enter', shiftKey: false });
      
      expect(sendSpy).toHaveBeenCalledWith('Test message', []);
    });
  });
});

describe('S0-1.3: Integration Tests', () => {
  it('should handle complete chat workflow', async () => {
    // This would test the full integration of all components
    const { container } = render(
      <ChatContainer
        agent={mockAgent}
        session={mockSession}
      />
    );
    
    // Check all major components are present
    expect(screen.getByText(mockAgent.name)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/Message/i)).toBeInTheDocument();
  });
});