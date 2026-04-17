"use client";
import { useSyncExternalStore } from 'react';

interface ClientOnlyProps {
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

function subscribe() {
  return () => {};
}

export default function ClientOnly({ children, fallback = null }: ClientOnlyProps) {
  const isClient = useSyncExternalStore(
    subscribe,
    () => true,
    () => false
  );

  return isClient ? <>{children}</> : <>{fallback}</>;
}
