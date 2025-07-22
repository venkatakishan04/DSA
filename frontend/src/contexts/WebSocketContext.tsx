import React, { createContext, useContext, useState, useEffect, useRef, ReactNode } from 'react';
import { toast } from 'react-toastify';
import { useAuth } from './AuthContext';

// Types
interface WebSocketMessage {
  type: string;
  session_id?: string;
  timestamp: number;
  data?: any;
  feedback?: any;
  result?: any;
  question?: any;
}

interface WebSocketContextType {
  isConnected: boolean;
  connectionStatus: 'connecting' | 'connected' | 'disconnected' | 'error';
  connect: (sessionId: string, sessionType: 'interview' | 'coding') => void;
  disconnect: () => void;
  sendMessage: (message: any) => void;
  sendBinaryData: (data: ArrayBuffer) => void;
  lastMessage: WebSocketMessage | null;
  messages: WebSocketMessage[];
  clearMessages: () => void;
}

interface WebSocketProviderProps {
  children: ReactNode;
}

// Create context
const WebSocketContext = createContext<WebSocketContextType | undefined>(undefined);

// WebSocket provider component
export const WebSocketProvider: React.FC<WebSocketProviderProps> = ({ children }) => {
  const { token, isAuthenticated } = useAuth();
  const [isConnected, setIsConnected] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<'connecting' | 'connected' | 'disconnected' | 'error'>('disconnected');
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);
  const [messages, setMessages] = useState<WebSocketMessage[]>([]);
  
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const maxReconnectAttempts = 5;

  const connect = (sessionId: string, sessionType: 'interview' | 'coding') => {
    if (!isAuthenticated || !token) {
      console.error('Cannot connect WebSocket: User not authenticated');
      return;
    }

    if (wsRef.current?.readyState === WebSocket.OPEN) {
      console.log('WebSocket already connected');
      return;
    }

    try {
      setConnectionStatus('connecting');
      
      // Determine WebSocket URL based on session type
      const wsUrl = sessionType === 'interview' 
        ? `${process.env.REACT_APP_WS_URL}/ws/interview/${sessionId}`
        : `${process.env.REACT_APP_WS_URL}/ws/coding/${sessionId}`;

      // Create WebSocket connection
      wsRef.current = new WebSocket(wsUrl);

      wsRef.current.onopen = () => {
        console.log('WebSocket connected');
        setIsConnected(true);
        setConnectionStatus('connected');
        reconnectAttemptsRef.current = 0;
        
        // Send authentication token
        if (wsRef.current) {
          wsRef.current.send(JSON.stringify({
            type: 'auth',
            token: token
          }));
        }
      };

      wsRef.current.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          setLastMessage(message);
          setMessages(prev => [...prev, message]);
          
          // Handle different message types
          handleWebSocketMessage(message);
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      wsRef.current.onclose = (event) => {
        console.log('WebSocket disconnected:', event.code, event.reason);
        setIsConnected(false);
        setConnectionStatus('disconnected');
        
        // Attempt to reconnect if not a normal closure
        if (event.code !== 1000 && reconnectAttemptsRef.current < maxReconnectAttempts) {
          attemptReconnect(sessionId, sessionType);
        }
      };

      wsRef.current.onerror = (error) => {
        console.error('WebSocket error:', error);
        setConnectionStatus('error');
        toast.error('Connection error. Please check your internet connection.');
      };

    } catch (error) {
      console.error('Error creating WebSocket connection:', error);
      setConnectionStatus('error');
    }
  };

  const disconnect = () => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    if (wsRef.current) {
      wsRef.current.close(1000, 'User disconnected');
      wsRef.current = null;
    }

    setIsConnected(false);
    setConnectionStatus('disconnected');
    reconnectAttemptsRef.current = 0;
  };

  const attemptReconnect = (sessionId: string, sessionType: 'interview' | 'coding') => {
    if (reconnectAttemptsRef.current >= maxReconnectAttempts) {
      toast.error('Unable to reconnect. Please refresh the page.');
      return;
    }

    reconnectAttemptsRef.current++;
    const delay = Math.min(1000 * Math.pow(2, reconnectAttemptsRef.current), 30000);

    console.log(`Attempting to reconnect in ${delay}ms (attempt ${reconnectAttemptsRef.current})`);
    
    reconnectTimeoutRef.current = setTimeout(() => {
      connect(sessionId, sessionType);
    }, delay);
  };

  const sendMessage = (message: any) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    } else {
      console.error('WebSocket is not connected');
      toast.error('Connection lost. Please reconnect.');
    }
  };

  const sendBinaryData = (data: ArrayBuffer) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(data);
    } else {
      console.error('WebSocket is not connected');
      toast.error('Connection lost. Please reconnect.');
    }
  };

  const clearMessages = () => {
    setMessages([]);
    setLastMessage(null);
  };

  const handleWebSocketMessage = (message: WebSocketMessage) => {
    switch (message.type) {
      case 'connection_established':
        toast.success('Connected to HireSmart AI');
        break;
        
      case 'real_time_feedback':
        // Handle real-time feedback during interview
        if (message.feedback) {
          // This would trigger UI updates for real-time coaching
          console.log('Real-time feedback:', message.feedback);
        }
        break;
        
      case 'coding_execution_result':
        // Handle coding execution results
        if (message.result) {
          console.log('Code execution result:', message.result);
        }
        break;
        
      case 'interview_question':
        // Handle new interview question
        if (message.question) {
          console.log('New interview question:', message.question);
        }
        break;
        
      case 'error':
        toast.error(message.data?.message || 'An error occurred');
        break;
        
      default:
        console.log('Unhandled message type:', message.type);
    }
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      disconnect();
    };
  }, []);

  // Disconnect when user logs out
  useEffect(() => {
    if (!isAuthenticated) {
      disconnect();
    }
  }, [isAuthenticated]);

  const value: WebSocketContextType = {
    isConnected,
    connectionStatus,
    connect,
    disconnect,
    sendMessage,
    sendBinaryData,
    lastMessage,
    messages,
    clearMessages,
  };

  return (
    <WebSocketContext.Provider value={value}>
      {children}
    </WebSocketContext.Provider>
  );
};

// Custom hook to use WebSocket context
export const useWebSocket = (): WebSocketContextType => {
  const context = useContext(WebSocketContext);
  if (context === undefined) {
    throw new Error('useWebSocket must be used within a WebSocketProvider');
  }
  return context;
};
