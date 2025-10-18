import { supabase } from '../lib/supabase';
import { generateMockEvents, generateMockDecoys, generateMockAlerts, generateMockLabels } from './mockData';

export const seedDatabase = async () => {
  try {
    const { count: eventCount } = await supabase
      .from('events')
      .select('*', { count: 'exact', head: true });

    if (eventCount && eventCount > 0) {
      console.log('Database already seeded, skipping...');
      return;
    }

    console.log('Seeding database with mock data...');

    const mockDecoys = generateMockDecoys();
    const { error: decoysError } = await supabase
      .from('decoys')
      .insert(mockDecoys.map(d => ({
        name: d.name,
        path: d.path,
        type: d.type,
        size_bytes: d.size_bytes,
        content_preview: d.content_preview,
        access_count: d.access_count,
        last_accessed_at: d.last_accessed_at,
      })));

    if (decoysError) {
      console.error('Error seeding decoys:', decoysError);
    } else {
      console.log('Decoys seeded successfully');
    }

    const mockEvents = generateMockEvents(50);
    const { error: eventsError } = await supabase
      .from('events')
      .insert(mockEvents.map(e => ({
        timestamp: e.timestamp,
        event_type: e.event_type,
        decoy_path: e.decoy_path,
        score: e.score,
        source_ip: e.source_ip,
        process_info: e.process_info,
        matched_rules: e.matched_rules,
        payload: e.payload,
      })));

    if (eventsError) {
      console.error('Error seeding events:', eventsError);
    } else {
      console.log('Events seeded successfully');
    }

    const { data: insertedEvents } = await supabase
      .from('events')
      .select('*')
      .order('timestamp', { ascending: false })
      .limit(50);

    if (insertedEvents && insertedEvents.length > 0) {
      const highScoreEvents = insertedEvents.filter(e => e.score >= 60);

      if (highScoreEvents.length > 0) {
        const alerts = highScoreEvents.map(event => ({
          event_id: event.id,
          severity: event.score >= 80 ? 'critical' : event.score >= 70 ? 'high' : 'medium',
          acknowledged: Math.random() > 0.5,
          acknowledged_at: Math.random() > 0.5 ? new Date().toISOString() : null,
          response_actions: [
            {
              action: 'alert_sent',
              timestamp: event.timestamp,
              status: 'completed',
            },
          ],
          notes: '',
        }));

        const { error: alertsError } = await supabase
          .from('alerts')
          .insert(alerts);

        if (alertsError) {
          console.error('Error seeding alerts:', alertsError);
        } else {
          console.log('Alerts seeded successfully');
        }
      }

      const labelsData = insertedEvents.slice(0, 20).map(event => ({
        event_id: event.id,
        signature: `${event.event_type}_${event.decoy_path}`,
        label: event.score > 70 ? 'attack' : event.score > 40 ? 'benign' : 'false_positive',
        notes: '',
        labeled_by: 'admin',
      }));

      const { error: labelsError } = await supabase
        .from('labels')
        .insert(labelsData);

      if (labelsError) {
        console.error('Error seeding labels:', labelsError);
      } else {
        console.log('Labels seeded successfully');
      }
    }

    console.log('Database seeding complete!');
  } catch (error) {
    console.error('Error seeding database:', error);
  }
};
