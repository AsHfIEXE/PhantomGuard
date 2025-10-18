"""
PhantomGuard Streamlit Dashboard (production-ready)
Displays events, scores, block actions, and allows FP marking. Config-driven, robust, minimal.
"""
from importlib import import_module
from pathlib import Path
from typing import Any
import json

st: Any
try:
    st = import_module('streamlit')
except Exception:
    # Lightweight fallback so module can be imported without streamlit
    # installed.
    class _FakeSt:
        def set_page_config(self, *args, **kwargs):
            pass

        def title(self, *args, **kwargs):
            pass

        def sidebar(self):
            return self

        def header(self, *args, **kwargs):
            pass

        def button(self, *args, **kwargs):
            return False

        def info(self, *args, **kwargs):
            pass

        def success(self, *args, **kwargs):
            pass

        def experimental_rerun(self):
            pass

        def expander(self, *args, **kwargs):
            class _Ctx:
                def __enter__(self):
                    return self

                def __exit__(self, *a):
                    return False
            return _Ctx()

        def json(self, *args, **kwargs):
            pass

        def columns(self, *args, **kwargs):
            return [self, self, self, self]

        def code(self, *args, **kwargs):
            pass
    st = _FakeSt()

LOG_PATH = Path('/var/log/phantomguard/alerts.log')
BLOCK_LOG_PATH = Path('/var/log/phantomguard/block.log')
FP_STATE_PATH = Path('ui/fp_state.json')
LABELS_PATH = Path('ui/labels.jsonl')

# FP state helpers


def load_fp_state():
    if FP_STATE_PATH.exists():
        return json.loads(FP_STATE_PATH.read_text())
    return []


def save_fp_state(fp_list):
    FP_STATE_PATH.write_text(json.dumps(fp_list))

# Label helpers


def append_label(entry: dict):
    LABELS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LABELS_PATH.open('a', encoding='utf-8') as f:
        f.write(json.dumps(entry) + '\n')

st.set_page_config(page_title="PhantomGuard Dashboard", layout="wide")
st.title('PhantomGuard Dashboard')

st.sidebar.header('Controls')
if st.sidebar.button('Reload'):
    st.experimental_rerun()

st.header('Recent Alerts')
if LOG_PATH.exists():
    lines = LOG_PATH.read_text().strip().splitlines()[-200:]
    data = []
    for line in lines:
        try:
            _, sig, payload = line.split(' ', 2)
            e = json.loads(payload)
            e['sig'] = sig
            data.append(e)
        except Exception:
            continue
    for ev in reversed(data):
        with st.expander(f"{ev.get('event_type')} {ev.get('path')} (score={ev.get('score', 0)})"):
            st.json(ev)
            fp_list = load_fp_state()
            is_fp = ev.get('sig') in fp_list
            cols = st.columns([1, 1, 1, 2])
            if cols[0].button('Mark Attack', key=ev.get('sig') + ':attack'):
                append_label(
                    {'sig': ev.get('sig'), 'label': 'attack', 'timestamp': ev.get('ts')})
                st.success('Marked as attack.')
            if cols[1].button('Mark Benign', key=ev.get('sig') + ':benign'):
                append_label(
                    {'sig': ev.get('sig'), 'label': 'benign', 'timestamp': ev.get('ts')})
                st.success('Marked as benign.')
            if cols[2].button('Mark as FP', key=ev.get('sig') + ':fp'):
                if ev.get('sig') not in fp_list:
                    fp_list.append(ev.get('sig'))
                    save_fp_state(fp_list)
                append_label({'sig': ev.get('sig'), 'label': 'fp',
                             'timestamp': ev.get('ts')})
                st.success('Marked as false positive.')
            if is_fp:
                st.info('Suppressed: Marked as false positive.')
else:
    st.info('No alerts.log found. Start PhantomGuard or run demo.')

st.header('Block Actions')
if BLOCK_LOG_PATH.exists():
    st.code(BLOCK_LOG_PATH.read_text(), language='text')
else:
    st.info('No block.log found.')

st.header('Label Management')
if LABELS_PATH.exists():
    labels = []
    for line in LABELS_PATH.read_text().splitlines():
        try:
            labels.append(json.loads(line))
        except Exception:
            continue
    for i, lab in enumerate(labels):
        cols = st.columns([4, 1])
        cols[0].write(lab)
        if cols[1].button('Delete', key=f'del_{i}'):
            # rewrite file without this label
            new_labels = [label_entry for j, label_entry in enumerate(labels) if j != i]
            LABELS_PATH.write_text('\n'.join(json.dumps(x) for x in new_labels) + ("\n" if new_labels else ""))
            st.experimental_rerun()
else:
    st.info('No labels recorded yet.')
