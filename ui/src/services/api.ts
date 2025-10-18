import { supabase } from '../lib/supabase';
import type { Event, Alert, Decoy, Label, BlockedIP, SystemStatus, EventFilter, EventSort } from '../types';

export const eventsApi = {
  async getAll(filter?: EventFilter, sort?: EventSort, limit = 100, offset = 0) {
    let query = supabase
      .from('events')
      .select('*')
      .range(offset, offset + limit - 1);

    if (filter?.eventType) {
      query = query.eq('event_type', filter.eventType);
    }

    if (filter?.minScore !== undefined) {
      query = query.gte('score', filter.minScore);
    }

    if (filter?.maxScore !== undefined) {
      query = query.lte('score', filter.maxScore);
    }

    if (filter?.searchTerm) {
      query = query.or(`decoy_path.ilike.%${filter.searchTerm}%,source_ip.ilike.%${filter.searchTerm}%`);
    }

    if (filter?.timeRange) {
      const now = new Date();
      let startDate: Date;

      switch (filter.timeRange) {
        case '1h':
          startDate = new Date(now.getTime() - 60 * 60 * 1000);
          break;
        case '6h':
          startDate = new Date(now.getTime() - 6 * 60 * 60 * 1000);
          break;
        case '24h':
          startDate = new Date(now.getTime() - 24 * 60 * 60 * 1000);
          break;
        case '7d':
          startDate = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
          break;
        default:
          startDate = new Date(now.getTime() - 24 * 60 * 60 * 1000);
      }

      query = query.gte('timestamp', startDate.toISOString());
    }

    if (filter?.startDate) {
      query = query.gte('timestamp', filter.startDate);
    }

    if (filter?.endDate) {
      query = query.lte('timestamp', filter.endDate);
    }

    if (sort) {
      query = query.order(sort.field, { ascending: sort.direction === 'asc' });
    } else {
      query = query.order('timestamp', { ascending: false });
    }

    const { data, error } = await query;
    if (error) throw error;
    return data as Event[];
  },

  async getById(id: string) {
    const { data, error } = await supabase
      .from('events')
      .select('*')
      .eq('id', id)
      .maybeSingle();
    if (error) throw error;
    return data as Event | null;
  },

  async create(event: Omit<Event, 'id' | 'created_at'>) {
    const { data, error } = await supabase
      .from('events')
      .insert(event)
      .select()
      .single();
    if (error) throw error;
    return data as Event;
  },

  async getRecent(limit = 10) {
    const { data, error } = await supabase
      .from('events')
      .select('*')
      .order('timestamp', { ascending: false })
      .limit(limit);
    if (error) throw error;
    return data as Event[];
  },
};

export const alertsApi = {
  async getAll(limit = 50) {
    const { data, error } = await supabase
      .from('alerts')
      .select('*, event:events(*)')
      .order('created_at', { ascending: false })
      .limit(limit);
    if (error) throw error;
    return data as (Alert & { event: Event })[];
  },

  async acknowledge(id: string, notes?: string) {
    const { data, error } = await supabase
      .from('alerts')
      .update({
        acknowledged: true,
        acknowledged_at: new Date().toISOString(),
        notes: notes || ''
      })
      .eq('id', id)
      .select()
      .single();
    if (error) throw error;
    return data as Alert;
  },

  async create(alert: Omit<Alert, 'id' | 'created_at'>) {
    const { data, error } = await supabase
      .from('alerts')
      .insert(alert)
      .select()
      .single();
    if (error) throw error;
    return data as Alert;
  },
};

export const decoysApi = {
  async getAll() {
    const { data, error } = await supabase
      .from('decoys')
      .select('*')
      .order('created_at', { ascending: false });
    if (error) throw error;
    return data as Decoy[];
  },

  async create(decoy: Omit<Decoy, 'id' | 'created_at' | 'access_count'>) {
    const { data, error } = await supabase
      .from('decoys')
      .insert({ ...decoy, access_count: 0 })
      .select()
      .single();
    if (error) throw error;
    return data as Decoy;
  },

  async delete(id: string) {
    const { error } = await supabase
      .from('decoys')
      .delete()
      .eq('id', id);
    if (error) throw error;
  },

  async incrementAccessCount(id: string) {
    const { data, error } = await supabase.rpc('increment_decoy_access', { decoy_id: id });
    if (error) {
      const { data: decoy } = await supabase
        .from('decoys')
        .select('access_count')
        .eq('id', id)
        .single();

      if (decoy) {
        await supabase
          .from('decoys')
          .update({
            access_count: (decoy.access_count || 0) + 1,
            last_accessed_at: new Date().toISOString()
          })
          .eq('id', id);
      }
    }
    return data;
  },
};

export const labelsApi = {
  async getAll() {
    const { data, error } = await supabase
      .from('labels')
      .select('*, event:events(*)')
      .order('created_at', { ascending: false });
    if (error) throw error;
    return data as (Label & { event: Event })[];
  },

  async create(label: Omit<Label, 'id' | 'created_at'>) {
    const { data, error } = await supabase
      .from('labels')
      .insert(label)
      .select()
      .single();
    if (error) throw error;
    return data as Label;
  },

  async delete(id: string) {
    const { error } = await supabase
      .from('labels')
      .delete()
      .eq('id', id);
    if (error) throw error;
  },
};

export const blockedIPsApi = {
  async getAll() {
    const { data, error } = await supabase
      .from('blocked_ips')
      .select('*')
      .order('blocked_at', { ascending: false });
    if (error) throw error;
    return data as BlockedIP[];
  },

  async block(ipAddress: string, reason: string) {
    const { data, error } = await supabase
      .from('blocked_ips')
      .insert({ ip_address: ipAddress, reason, event_count: 1 })
      .select()
      .single();
    if (error) throw error;
    return data as BlockedIP;
  },

  async unblock(id: string) {
    const { data, error } = await supabase
      .from('blocked_ips')
      .update({ unblocked_at: new Date().toISOString() })
      .eq('id', id)
      .select()
      .single();
    if (error) throw error;
    return data as BlockedIP;
  },
};

export const systemApi = {
  async getStatus() {
    const { data, error } = await supabase
      .from('system_status')
      .select('*')
      .limit(1)
      .maybeSingle();
    if (error) throw error;
    return data as SystemStatus | null;
  },

  async updateStatus(status: Partial<SystemStatus>) {
    const existing = await this.getStatus();
    if (existing) {
      const { data, error } = await supabase
        .from('system_status')
        .update({ ...status, updated_at: new Date().toISOString() })
        .eq('id', existing.id)
        .select()
        .single();
      if (error) throw error;
      return data as SystemStatus;
    } else {
      const { data, error } = await supabase
        .from('system_status')
        .insert({ ...status, updated_at: new Date().toISOString() })
        .select()
        .single();
      if (error) throw error;
      return data as SystemStatus;
    }
  },

  async getMetrics() {
    const now = new Date();
    const todayStart = new Date(now.getFullYear(), now.getMonth(), now.getDate());

    const [events, eventsToday, alerts, blockedIPs, decoys] = await Promise.all([
      supabase.from('events').select('*', { count: 'exact', head: true }),
      supabase.from('events').select('*', { count: 'exact', head: true }).gte('timestamp', todayStart.toISOString()),
      supabase.from('alerts').select('*', { count: 'exact', head: true }),
      supabase.from('blocked_ips').select('*', { count: 'exact', head: true }).is('unblocked_at', null),
      supabase.from('decoys').select('*', { count: 'exact', head: true }),
    ]);

    const recentEvents = await supabase
      .from('events')
      .select('score')
      .gte('timestamp', new Date(now.getTime() - 60 * 60 * 1000).toISOString());

    let threatLevel: 'low' | 'medium' | 'high' | 'critical' = 'low';
    if (recentEvents.data && recentEvents.data.length > 0) {
      const avgScore = recentEvents.data.reduce((sum, e) => sum + e.score, 0) / recentEvents.data.length;
      if (avgScore >= 80) threatLevel = 'critical';
      else if (avgScore >= 60) threatLevel = 'high';
      else if (avgScore >= 40) threatLevel = 'medium';
    }

    return {
      totalEvents: events.count || 0,
      totalEventsToday: eventsToday.count || 0,
      alertsTriggered: alerts.count || 0,
      ipsBlocked: blockedIPs.count || 0,
      activeDecoys: decoys.count || 0,
      threatLevel,
    };
  },
};
