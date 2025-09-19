/**
 * React hook for Pusher real-time functionality.
 * Provides easy integration with Pusher channels and events in React components.
 */

import { useEffect, useState, useCallback, useRef } from 'react';
import { Channel, PresenceChannel } from 'pusher-js';
import { pusherService, PusherEvent, CostUpdateEvent, BudgetAlertEvent } from '../services/pusher.service';

export interface UsePusherOptions {
  /**
   * Automatically connect on mount.
   */
  autoConnect?: boolean;
  
  /**
   * Channel to subscribe to.
   */
  channel?: string;
  
  /**
   * Events to bind to on the channel.
   */
  events?: Record<string, (data: any) => void>;
  
  /**
   * Callback when connected.
   */
  onConnect?: () => void;
  
  /**
   * Callback when disconnected.
   */
  onDisconnect?: () => void;
  
  /**
   * Callback on connection error.
   */
  onError?: (error: any) => void;
}

export interface UsePusherReturn {
  /**
   * Current connection state.
   */
  connectionState: 'disconnected' | 'connecting' | 'connected';
  
  /**
   * Subscribe to a channel.
   */
  subscribe: (channelName: string) => Channel | PresenceChannel | null;
  
  /**
   * Unsubscribe from a channel.
   */
  unsubscribe: (channelName: string) => void;
  
  /**
   * Bind event handler to a channel.
   */
  bind: (channelName: string, eventName: string, callback: Function) => void;
  
  /**
   * Unbind event handler from a channel.
   */
  unbind: (channelName: string, eventName: string, callback?: Function) => void;
  
  /**
   * Get a subscribed channel.
   */
  getChannel: (channelName: string) => Channel | PresenceChannel | null;
  
  /**
   * Trigger event from client.
   */
  triggerEvent: (channel: string, event: string, data: any) => Promise<boolean>;
  
  /**
   * Disconnect from Pusher.
   */
  disconnect: () => void;
}

/**
 * Hook for using Pusher in React components.
 */
export function usePusher(options: UsePusherOptions = {}): UsePusherReturn {
  const {
    autoConnect = true,
    channel,
    events,
    onConnect,
    onDisconnect,
    onError,
  } = options;

  const [connectionState, setConnectionState] = useState<'disconnected' | 'connecting' | 'connected'>('disconnected');
  const subscribedChannels = useRef<Set<string>>(new Set());
  const eventCleanups = useRef<Array<() => void>>([]);

  // Initialize Pusher on mount
  useEffect(() => {
    if (autoConnect) {
      pusherService.initialize();

      // Check if Pusher is enabled
      if (!pusherService.isEnabled()) {
        setConnectionState('disconnected');
        onError?.(new Error('Pusher is not configured. Set NEXT_PUBLIC_PUSHER_KEY to enable real-time features.'));
        return;
      }

      setConnectionState('connecting');

      // Setup connection handlers
      const handleConnect = () => {
        setConnectionState('connected');
        onConnect?.();
      };

      const handleDisconnect = () => {
        setConnectionState('disconnected');
        onDisconnect?.();
      };

      const handleError = (error: any) => {
        setConnectionState('disconnected');
        onError?.(error);
      };

      // Set up a timeout for connection
      const connectionTimeout = setTimeout(() => {
        if (connectionState === 'connecting') {
          handleError(new Error('Connection timeout. Pusher may be unavailable or misconfigured.'));
        }
      }, 5000); // 5 second timeout

      // Poll connection state
      const checkConnection = setInterval(() => {
        const currentState = pusherService.getConnectionState();

        if (currentState === 'connected' && connectionState !== 'connected') {
          clearTimeout(connectionTimeout);
          handleConnect();
        } else if (currentState === 'disconnected' && connectionState !== 'disconnected') {
          clearTimeout(connectionTimeout);
          handleDisconnect();
        }
      }, 500); // Check more frequently

      return () => {
        clearInterval(checkConnection);
        clearTimeout(connectionTimeout);
      };
    }
  }, [autoConnect, onConnect, onDisconnect, onError]);

  // Subscribe to channel if provided
  useEffect(() => {
    if (channel && connectionState === 'connected') {
      const subscribedChannel = pusherService.subscribe(channel);
      if (subscribedChannel) {
        subscribedChannels.current.add(channel);

        // Bind events if provided
        if (events) {
          Object.entries(events).forEach(([eventName, handler]) => {
            pusherService.bind(channel, eventName, handler);
            eventCleanups.current.push(() => pusherService.unbind(channel, eventName, handler));
          });
        }
      }

      return () => {
        if (subscribedChannels.current.has(channel)) {
          pusherService.unsubscribe(channel);
          subscribedChannels.current.delete(channel);
        }
      };
    }
  }, [channel, events, connectionState]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      // Clean up event handlers
      eventCleanups.current.forEach(cleanup => cleanup());
      eventCleanups.current = [];

      // Unsubscribe from all channels
      subscribedChannels.current.forEach(channelName => {
        pusherService.unsubscribe(channelName);
      });
      subscribedChannels.current.clear();
    };
  }, []);

  const subscribe = useCallback((channelName: string) => {
    const channel = pusherService.subscribe(channelName);
    if (channel) {
      subscribedChannels.current.add(channelName);
    }
    return channel;
  }, []);

  const unsubscribe = useCallback((channelName: string) => {
    pusherService.unsubscribe(channelName);
    subscribedChannels.current.delete(channelName);
  }, []);

  const bind = useCallback((channelName: string, eventName: string, callback: Function) => {
    pusherService.bind(channelName, eventName, callback);
    eventCleanups.current.push(() => pusherService.unbind(channelName, eventName, callback));
  }, []);

  const unbind = useCallback((channelName: string, eventName: string, callback?: Function) => {
    pusherService.unbind(channelName, eventName, callback);
  }, []);

  const getChannel = useCallback((channelName: string) => {
    return pusherService.getChannel(channelName);
  }, []);

  const triggerEvent = useCallback(async (channel: string, event: string, data: any) => {
    return pusherService.triggerEvent(channel, event, data);
  }, []);

  const disconnect = useCallback(() => {
    pusherService.disconnect();
    setConnectionState('disconnected');
  }, []);

  return {
    connectionState,
    subscribe,
    unsubscribe,
    bind,
    unbind,
    getChannel,
    triggerEvent,
    disconnect,
  };
}

/**
 * Hook for cost dashboard real-time updates.
 */
export function useCostDashboard() {
  const [costData, setCostData] = useState<CostUpdateEvent | null>(null);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);

  const handleCostUpdate = useCallback((event: PusherEvent<CostUpdateEvent>) => {
    setCostData(event.data);
    setLastUpdate(new Date(event.timestamp));
  }, []);

  const { connectionState } = usePusher({
    channel: 'private-cost-dashboard',
    events: {
      'cost-update': handleCostUpdate,
    },
  });

  return {
    connectionState,
    costData,
    lastUpdate,
  };
}

/**
 * Hook for budget alerts.
 */
export function useBudgetAlerts() {
  const [alerts, setAlerts] = useState<BudgetAlertEvent[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);

  const handleBudgetAlert = useCallback((event: PusherEvent<BudgetAlertEvent>) => {
    setAlerts(prev => [event.data, ...prev]);
    setUnreadCount(prev => prev + 1);
  }, []);

  const { connectionState } = usePusher({
    channel: 'private-budget-alerts',
    events: {
      'budget-alert': handleBudgetAlert,
    },
  });

  const markAsRead = useCallback(() => {
    setUnreadCount(0);
  }, []);

  const clearAlerts = useCallback(() => {
    setAlerts([]);
    setUnreadCount(0);
  }, []);

  return {
    connectionState,
    alerts,
    unreadCount,
    markAsRead,
    clearAlerts,
  };
}

/**
 * Hook for user-specific real-time updates.
 */
export function useUserChannel(userId: string) {
  const [userData, setUserData] = useState<any>(null);

  const handleUserData = useCallback((data: any) => {
    setUserData(data);
  }, []);

  const { connectionState } = usePusher({
    channel: `private-user-${userId}`,
    events: {
      'initial-data': handleUserData,
      'user-update': handleUserData,
    },
  });

  return {
    connectionState,
    userData,
  };
}

/**
 * Hook for presence channel (who's online).
 */
export function usePresenceChannel() {
  const [members, setMembers] = useState<any[]>([]);
  const [myInfo, setMyInfo] = useState<any>(null);

  const { connectionState, getChannel } = usePusher({
    channel: 'presence-dashboard',
  });

  useEffect(() => {
    if (connectionState === 'connected') {
      const channel = getChannel('presence-dashboard') as PresenceChannel;
      if (channel) {
        // Handle member added
        channel.bind('pusher:member_added', (member: any) => {
          setMembers(prev => [...prev, member]);
        });

        // Handle member removed
        channel.bind('pusher:member_removed', (member: any) => {
          setMembers(prev => prev.filter(m => m.id !== member.id));
        });

        // Handle subscription success
        channel.bind('pusher:subscription_succeeded', (members: any) => {
          setMembers(Object.values(members.members));
          setMyInfo(members.myInfo);
        });
      }
    }
  }, [connectionState, getChannel]);

  return {
    connectionState,
    members,
    myInfo,
    onlineCount: members.length,
  };
}