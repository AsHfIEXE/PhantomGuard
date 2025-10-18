import { create } from 'zustand';
import type { Event, Alert, Decoy, Label, SystemStatus, DashboardMetrics } from '../types';

interface AppState {
  events: Event[];
  alerts: Alert[];
  decoys: Decoy[];
  labels: Label[];
  systemStatus: SystemStatus | null;
  metrics: DashboardMetrics | null;
  setEvents: (events: Event[]) => void;
  setAlerts: (alerts: Alert[]) => void;
  setDecoys: (decoys: Decoy[]) => void;
  setLabels: (labels: Label[]) => void;
  setSystemStatus: (status: SystemStatus) => void;
  setMetrics: (metrics: DashboardMetrics) => void;
  addEvent: (event: Event) => void;
  addAlert: (alert: Alert) => void;
  updateAlert: (id: string, updates: Partial<Alert>) => void;
  deleteDecoy: (id: string) => void;
  deleteLabel: (id: string) => void;
}

export const useStore = create<AppState>((set) => ({
  events: [],
  alerts: [],
  decoys: [],
  labels: [],
  systemStatus: null,
  metrics: null,

  setEvents: (events) => set({ events }),
  setAlerts: (alerts) => set({ alerts }),
  setDecoys: (decoys) => set({ decoys }),
  setLabels: (labels) => set({ labels }),
  setSystemStatus: (systemStatus) => set({ systemStatus }),
  setMetrics: (metrics) => set({ metrics }),

  addEvent: (event) => set((state) => ({ events: [event, ...state.events] })),
  addAlert: (alert) => set((state) => ({ alerts: [alert, ...state.alerts] })),

  updateAlert: (id, updates) =>
    set((state) => ({
      alerts: state.alerts.map((alert) =>
        alert.id === id ? { ...alert, ...updates } : alert
      ),
    })),

  deleteDecoy: (id) =>
    set((state) => ({
      decoys: state.decoys.filter((decoy) => decoy.id !== id),
    })),

  deleteLabel: (id) =>
    set((state) => ({
      labels: state.labels.filter((label) => label.id !== id),
    })),
}));
