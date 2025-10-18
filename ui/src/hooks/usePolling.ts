import { useEffect, useRef, useCallback } from 'react';

export const usePolling = (callback: () => void, interval: number = 5000, enabled: boolean = true) => {
  const savedCallback = useRef(callback);
  const intervalRef = useRef<NodeJS.Timeout>();

  useEffect(() => {
    savedCallback.current = callback;
  }, [callback]);

  const start = useCallback(() => {
    if (intervalRef.current) return;
    savedCallback.current();
    intervalRef.current = setInterval(() => savedCallback.current(), interval);
  }, [interval]);

  const stop = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = undefined;
    }
  }, []);

  useEffect(() => {
    if (enabled) {
      start();
    } else {
      stop();
    }

    return stop;
  }, [enabled, start, stop]);

  return { start, stop };
};
