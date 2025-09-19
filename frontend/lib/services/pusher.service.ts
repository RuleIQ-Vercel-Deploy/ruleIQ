/**
 * Pusher service for real-time communication.
 * Manages Pusher client initialization, channel subscriptions, and event handling.
 */

import Pusher, { Channel, PresenceChannel } from 'pusher-js';

export interface PusherConfig {
  appKey: string;
  cluster: string;
  authEndpoint?: string;
  auth?: {
    headers?: Record<string, string>;
    params?: Record<string, string>;
  };
  forceTLS?: boolean;
  enabledTransports?: string[];
  disabledTransports?: string[];
}

export interface ChannelSubscription {
  channel: Channel | PresenceChannel;
  unsubscribe: () => void;
}

export interface PusherEvent<T = any> {
  type: string;
  timestamp: string;
  data: T;
}

export interface CostUpdateEvent {
  total_cost: string;
  total_requests: number;
  total_tokens?: number;
  period: 'daily' | 'weekly' | 'monthly';
  service_breakdown?: Record<string, {
    cost: string;
    requests: number;
  }>;
}

export interface BudgetAlertEvent {
  severity: 'info' | 'warning' | 'error' | 'critical';
  message: string;
  current_usage: string;
  limit: string;
  percentage_used: number;
  alert_type: 'daily' | 'monthly';
}

export interface ConnectionStats {
  user_channel: string;
  available_channels: string[];
  connected: boolean;
}

class PusherService {
  private static instance: PusherService;
  private pusher: Pusher | null = null;
  private config: PusherConfig | null = null;
  private subscriptions: Map<string, ChannelSubscription> = new Map();
  private connectionState: 'disconnected' | 'connecting' | 'connected' = 'disconnected';
  private eventHandlers: Map<string, Set<Function>> = new Map();

  private constructor() {
    // Private constructor for singleton
  }

  /**
   * Get singleton instance of PusherService.
   */
  public static getInstance(): PusherService {
    if (!PusherService.instance) {
      PusherService.instance = new PusherService();
    }
    return PusherService.instance;
  }

  /**
   * Initialize Pusher client with configuration.
   */
  public initialize(config: Partial<PusherConfig> = {}): void {
    if (this.pusher) {
      console.warn('Pusher already initialized. Disconnecting existing connection.');
      this.disconnect();
    }

    // Get config from environment or use provided config
    this.config = {
      appKey: config.appKey || process.env.NEXT_PUBLIC_PUSHER_KEY || '',
      cluster: config.cluster || process.env.NEXT_PUBLIC_PUSHER_CLUSTER || 'eu',
      authEndpoint: config.authEndpoint || '/api/pusher/auth',
      auth: config.auth || {
        headers: {
          'Content-Type': 'application/json',
        },
      },
      forceTLS: config.forceTLS !== undefined ? config.forceTLS : true,
      enabledTransports: config.enabledTransports || ['ws', 'wss'],
      disabledTransports: config.disabledTransports || [],
    };

    if (!this.config.appKey) {
      console.warn('Pusher app key not provided. Real-time features disabled.');
      this.connectionState = 'disconnected';
      // Emit error event so hooks can handle it properly
      setTimeout(() => {
        this.emit('connection:error', new Error('Pusher key not configured'));
        this.emit('connection:disconnected');
      }, 0);
      return;
    }

    // Initialize Pusher client
    this.pusher = new Pusher(this.config.appKey, {
      cluster: this.config.cluster,
      authEndpoint: this.config.authEndpoint,
      auth: this.config.auth,
      forceTLS: this.config.forceTLS,
      enabledTransports: this.config.enabledTransports as any,
      disabledTransports: this.config.disabledTransports as any,
    });

    this.setupConnectionHandlers();
    this.connectionState = 'connecting';
  }

  /**
   * Setup connection state handlers.
   */
  private setupConnectionHandlers(): void {
    if (!this.pusher) return;

    this.pusher.connection.bind('connected', () => {
      console.log('Pusher connected');
      this.connectionState = 'connected';
      this.emit('connection:connected');
    });

    this.pusher.connection.bind('disconnected', () => {
      console.log('Pusher disconnected');
      this.connectionState = 'disconnected';
      this.emit('connection:disconnected');
    });

    this.pusher.connection.bind('error', (error: any) => {
      console.error('Pusher connection error:', error);
      this.emit('connection:error', error);
    });

    this.pusher.connection.bind('state_change', (states: any) => {
      console.log('Pusher state change:', states);
      this.emit('connection:state_change', states);
    });
  }

  /**
   * Subscribe to a channel.
   */
  public subscribe(channelName: string): Channel | PresenceChannel | null {
    if (!this.pusher) {
      console.error('Pusher not initialized');
      return null;
    }

    // Check if already subscribed
    if (this.subscriptions.has(channelName)) {
      return this.subscriptions.get(channelName)!.channel;
    }

    try {
      const channel = this.pusher.subscribe(channelName);
      
      const subscription: ChannelSubscription = {
        channel,
        unsubscribe: () => this.unsubscribe(channelName),
      };

      this.subscriptions.set(channelName, subscription);

      // Handle subscription success/error
      channel.bind('pusher:subscription_succeeded', () => {
        console.log(`Successfully subscribed to ${channelName}`);
        this.emit(`subscription:${channelName}:succeeded`);
      });

      channel.bind('pusher:subscription_error', (error: any) => {
        console.error(`Failed to subscribe to ${channelName}:`, error);
        this.emit(`subscription:${channelName}:error`, error);
      });

      return channel;
    } catch (error) {
      console.error(`Error subscribing to ${channelName}:`, error);
      return null;
    }
  }

  /**
   * Unsubscribe from a channel.
   */
  public unsubscribe(channelName: string): void {
    if (!this.pusher) return;

    const subscription = this.subscriptions.get(channelName);
    if (subscription) {
      this.pusher.unsubscribe(channelName);
      this.subscriptions.delete(channelName);
      console.log(`Unsubscribed from ${channelName}`);
    }
  }

  /**
   * Bind event handler to a channel.
   */
  public bind(channelName: string, eventName: string, callback: Function): void {
    const channel = this.getChannel(channelName);
    if (channel) {
      channel.bind(eventName, callback);
      
      // Track handler for cleanup
      const key = `${channelName}:${eventName}`;
      if (!this.eventHandlers.has(key)) {
        this.eventHandlers.set(key, new Set());
      }
      this.eventHandlers.get(key)!.add(callback);
    }
  }

  /**
   * Unbind event handler from a channel.
   */
  public unbind(channelName: string, eventName: string, callback?: Function): void {
    const channel = this.getChannel(channelName);
    if (channel) {
      if (callback) {
        channel.unbind(eventName, callback);
        
        const key = `${channelName}:${eventName}`;
        this.eventHandlers.get(key)?.delete(callback);
      } else {
        channel.unbind(eventName);
        
        const key = `${channelName}:${eventName}`;
        this.eventHandlers.delete(key);
      }
    }
  }

  /**
   * Get a subscribed channel.
   */
  public getChannel(channelName: string): Channel | PresenceChannel | null {
    const subscription = this.subscriptions.get(channelName);
    return subscription ? subscription.channel : null;
  }

  /**
   * Get connection state.
   */
  public getConnectionState(): 'disconnected' | 'connecting' | 'connected' {
    return this.connectionState;
  }

  /**
   * Check if connected.
   */
  public isConnected(): boolean {
    return this.connectionState === 'connected';
  }

  /**
   * Check if Pusher is enabled (has valid configuration).
   */
  public isEnabled(): boolean {
    return !!this.config?.appKey && this.config.appKey !== '';
  }

  /**
   * Disconnect from Pusher.
   */
  public disconnect(): void {
    if (!this.pusher) return;

    // Unsubscribe from all channels
    this.subscriptions.forEach((_, channelName) => {
      this.unsubscribe(channelName);
    });

    // Clear event handlers
    this.eventHandlers.clear();

    // Disconnect
    this.pusher.disconnect();
    this.pusher = null;
    this.connectionState = 'disconnected';
    console.log('Pusher disconnected');
  }

  /**
   * Emit internal event.
   */
  private emit(event: string, data?: any): void {
    // This would integrate with your app's event system
    // For now, just log
    console.log(`PusherService event: ${event}`, data);
  }

  /**
   * Subscribe to cost dashboard channel.
   */
  public subscribeToCostDashboard(): Channel | null {
    return this.subscribe('private-cost-dashboard');
  }

  /**
   * Subscribe to budget alerts channel.
   */
  public subscribeToBudgetAlerts(): Channel | null {
    return this.subscribe('private-budget-alerts');
  }

  /**
   * Subscribe to user's private channel.
   */
  public subscribeToUserChannel(userId: string): Channel | null {
    return this.subscribe(`private-user-${userId}`);
  }

  /**
   * Subscribe to presence dashboard.
   */
  public subscribeToPresenceDashboard(): PresenceChannel | null {
    return this.subscribe('presence-dashboard') as PresenceChannel;
  }

  /**
   * Trigger event from client (requires server endpoint).
   */
  public async triggerEvent(
    channel: string,
    event: string,
    data: any
  ): Promise<boolean> {
    try {
      const response = await fetch('/api/pusher/trigger', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          channel,
          event,
          data,
        }),
      });

      const result = await response.json();
      return result.success;
    } catch (error) {
      console.error('Failed to trigger event:', error);
      return false;
    }
  }
}

// Export singleton instance
export const pusherService = PusherService.getInstance();

// Export types
export type { PusherService };