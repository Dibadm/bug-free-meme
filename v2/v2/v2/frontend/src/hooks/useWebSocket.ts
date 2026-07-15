import { useEffect, useRef, useCallback, useState } from "react";

type EventHandler = (event: string, data: Record<string, unknown>) => void;

interface UseWebSocketOptions {
  url?: string;
  token?: string | null;
  onEvent?: EventHandler;
  reconnect?: boolean;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
}

interface UseWebSocketReturn {
  isConnected: boolean;
  send: (event: string, data: Record<string, unknown>) => void;
  subscribe: (roomId: string) => void;
  unsubscribe: (roomId: string) => void;
  lastEvent: { event: string; data: Record<string, unknown> } | null;
}

export function useWebSocket({
  url = (import.meta as any).env?.VITE_WS_URL || "ws://localhost:8000",
  token,
  onEvent,
  reconnect = true,
  reconnectInterval = 1000,
  maxReconnectAttempts = 10,
}: UseWebSocketOptions = {}): UseWebSocketReturn {
  const wsRef = useRef<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [lastEvent, setLastEvent] = useState<{ event: string; data: Record<string, unknown> } | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const reconnectTimerRef = useRef<ReturnType<typeof setTimeout>>();
  const onEventRef = useRef(onEvent);
  const tokenRef = useRef(token);

  onEventRef.current = onEvent;
  tokenRef.current = token;

  const connect = useCallback(() => {
    if (!token) return;
    const wsUrl = `${url}/api/v1/ws?token=${encodeURIComponent(token)}`;
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      setIsConnected(true);
      reconnectAttemptsRef.current = 0;
    };

    ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        setLastEvent({ event: message.event, data: message.data || {} });
        onEventRef.current?.(message.event, message.data || {});
      } catch {
        // ignore invalid messages
      }
    };

    ws.onclose = () => {
      setIsConnected(false);
      if (reconnect && reconnectAttemptsRef.current < maxReconnectAttempts && tokenRef.current) {
        const backoff = Math.min(reconnectInterval * Math.pow(2, reconnectAttemptsRef.current), 30000);
        reconnectAttemptsRef.current += 1;
        reconnectTimerRef.current = setTimeout(connect, backoff);
      }
    };

    ws.onerror = () => {
      ws.close();
    };
  }, [url, token, reconnect, reconnectInterval, maxReconnectAttempts]);

  useEffect(() => {
    if (!token) return;
    connect();
    return () => {
      if (reconnectTimerRef.current) {
        clearTimeout(reconnectTimerRef.current);
      }
      wsRef.current?.close();
    };
  }, [token, connect, reconnect]);

  const send = useCallback((event: string, data: Record<string, unknown>) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ event, data }));
    }
  }, []);

  const subscribe = useCallback((roomId: string) => {
    send("subscribe.room", { room_id: roomId });
  }, [send]);

  const unsubscribe = useCallback((roomId: string) => {
    send("unsubscribe.room", { room_id: roomId });
  }, [send]);

  return { isConnected, send, subscribe, unsubscribe, lastEvent };
}
