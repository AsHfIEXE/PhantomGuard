from processor.event_scorer import EventScorer


def test_score_honeytoken():
    s = EventScorer()
    event = {"path": "/tmp/.ssh/id_rsa", "event_type": "open"}
    score, matches = s.score_event(event)
    assert score >= 50
    assert any(
        'honeytoken' in m or 'open_sensitive_honeytoken' in m for m in matches)


def test_score_fake_cron():
    s = EventScorer()
    event = {"path": "/tmp/fake_cron", "event_type": "modified"}
    score, matches = s.score_event(event)
    assert score >= 40
