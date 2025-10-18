import json


def test_label_append_and_load(tmp_path):
    p = tmp_path / 'ui'
    p.mkdir()
    labels_file = p / 'labels.jsonl'
    # Append a label
    entry = {
        'sig': 'abc123',
        'label': 'benign',
        'timestamp': '2025-10-18T00:00:00'}
    with labels_file.open('a', encoding='utf-8') as f:
        f.write(json.dumps(entry) + '\n')
    # Read back
    lines = labels_file.read_text().splitlines()
    assert len(lines) == 1
    loaded = json.loads(lines[0])
    assert loaded['sig'] == 'abc123'
    assert loaded['label'] == 'benign'
