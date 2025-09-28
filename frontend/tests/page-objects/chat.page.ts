/**
 * Chat Page Object Model
 * 
 * Provides interface for chat functionality during E2E testing
 */

import { type Page, type Locator } from '@playwright/test';

export class ChatPage {
  readonly page: Page;
  
  // Chat elements
  readonly messageInput: Locator;
  readonly sendButton: Locator;
  readonly messagesContainer: Locator;
  readonly chatHeader: Locator;
  
  constructor(page: Page) {
    this.page = page;
    
    this.messageInput = page.locator('[data-testid="chat-input"]');
    this.sendButton = page.locator('[data-testid="send-button"]');
    this.messagesContainer = page.locator('[data-testid="messages-container"]');
    this.chatHeader = page.locator('[data-testid="chat-header"]');
  }
  
  /**
   * Navigate to chat page
   */
  async navigateToChat() {
    await this.page.goto('/chat');
    await this.messagesContainer.waitFor({ state: 'visible' });
  }
  
  /**
   * Send a message in chat
   */
  async sendMessage(message: string) {
    await this.messageInput.fill(message);
    await this.sendButton.click();
  }
  
  /**
   * Wait for last message to appear
   */
  async waitForLastMessage(timeout = 30000) {
    await this.page.waitForFunction(
      () => {
        const messages = document.querySelectorAll('[data-testid="chat-message"]');
        return messages.length > 0;
      },
      { timeout }
    );
    
    return this.page.locator('[data-testid="chat-message"]').last();
  }
  
  /**
   * Get content of last message
   */
  async getLastMessageContent(): Promise<string> {
    const lastMessage = await this.waitForLastMessage();
    return await lastMessage.textContent() || '';
  }
  
  /**
   * Open export dialog
   */
  async openExportDialog() {
    await this.page.locator('[data-testid="export-button"]').click();
  }
  
  /**
   * Export conversation
   */
  async exportConversation() {
    await this.page.locator('[data-testid="export-confirm"]').click();
  }
}