/**
 * WebSocket type definitions for agent communication
 */

export enum MessageType {
  CHAT = 'chat',
  SYSTEM = 'system',
  STATUS = 'status',
  CONTROL = 'control',
  TYPING = 'typing',
  ERROR = 'error',
  HEARTBEAT = 'heartbeat'
}

export enum TrustLevel {
  L0_OBSERVED = 0,
  L1_ASSISTED = 1,
  L2_SUPERVISED = 2,
  L3_DELEGATED = 3,
  L4_AUTONOMOUS = 4
}

export interface WSMessage {
  id: string;
  type: MessageType;
  timestamp: string; // ISO string for JSON serialization
  payload: MessagePayload;
}

export interface MessagePayload {
  content?: string;
  context?: Record<string, any>;
  metadata?: MessageMetadata;
  error?: ErrorInfo;
  // Streaming fields
  delta?: string;
  isFinal?: boolean;
  sequence?: number;
  messageId?: string;
}

export interface MessageMetadata {
  agentId?: string;
  sessionId?: string;
  trustLevel?: TrustLevel;
  userId?: string;
  role?: 'user' | 'agent' | 'system';
}

export interface ErrorInfo {
  code: string;
  message: string;
  details?: any;
}

export interface ConnectionState {
  connected: boolean;
  connecting: boolean;
  error: Error | null;
  retryCount: number;
  lastConnectedAt?: Date;
}

export interface ChatMessage {
  id: string;
  content: string;
  role: 'user' | 'agent' | 'system';
  timestamp: Date;
  agentId?: string;
  sessionId?: string;
  trustLevel?: TrustLevel;
  attachments?: Attachment[];
  codeBlocks?: CodeBlock[];
  status?: 'sending' | 'sent' | 'failed' | 'delivered';
  isStreaming?: boolean;
}

export interface Attachment {
  id: string;
  name: string;
  type: string;
  size: number;
  url?: string;
}

export interface CodeBlock {
  language: string;
  code: string;
  filename?: string;
}

export interface Session {
  id: string;
  agentId: string;
  userId: string;
  trustLevel: TrustLevel;
  context: Record<string, any>;
  startedAt: Date;
  endedAt?: Date;
  messages: ChatMessage[];
}

export interface Agent {
  id: string;
  name: string;
  personaType: string;
  capabilities: string[];
  isActive: boolean;
  currentTrustLevel?: TrustLevel;
  config?: Record<string, any>;
}

export interface TypingIndicator {
  agentId: string;
  sessionId: string;
  isTyping: boolean;
}

export interface WSEventHandlers {
  onOpen?: () => void;
  onClose?: (event: CloseEvent) => void;
  onError?: (error: Error) => void;
  onMessage?: (message: WSMessage) => void;
  onReconnect?: (attempt: number) => void;
  onTyping?: (indicator: TypingIndicator) => void;
  onStreamChunk?: (chunk: StreamingMessagePayload) => void;
}

// Streaming-specific interfaces
export interface StreamingMessagePayload {
  delta: string;
  isFinal?: boolean;
  sequence?: number;
  messageId: string;
  trustLevel?: TrustLevel;
  sessionId: string;
  agentId: string;
}

export interface StreamingState {
  messageId: string;
  content: string;
  sequence: number;
  isComplete: boolean;
  startTime: number;
}