"""
PhantomGuard Streamlit Dashboard (production-ready)
Displays events, scores, block actions, and allows FP marking. Config-driven, robust, minimal.
"""
import streamlit as st
from pathlib import Path
import json
from datetime import datetime

# Paths
LOG_PATH = Path('/var/log/phantomguard/alerts.log')
BLOCK_LOG_PATH = Path('/var/log/phantomguard/block.log')
FP_STATE_PATH = Path('ui/fp_state.json')
LABELS_PATH = Path('ui/labels.jsonl')

# Fallback to local logs if /var/log is not writable
if not LOG_PATH.parent.exists():
    LOG_PATH = Path('logs/phantomguard/alerts.log')
    BLOCK_LOG_PATH = Path('logs/phantomguard/block.log')

# FP state helpers
def load_fp_state():
    """Load false positive state from JSON file."""
    if FP_STATE_PATH.exists():
        try:
            return json.loads(FP_STATE_PATH.read_text())
        except Exception:
            return []
    return []


def save_fp_state(fp_list):
    """Save false positive state to JSON file."""
    FP_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    FP_STATE_PATH.write_text(json.dumps(fp_list, indent=2))


def append_label(entry: dict):
    """Append a label entry to the labels file."""
    LABELS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LABELS_PATH.open('a', encoding='utf-8') as f:
        f.write(json.dumps(entry) + '\n')


def load_labels():
    """Load all labels from the labels file."""
    if not LABELS_PATH.exists():
        return []
    labels = []
    for line in LABELS_PATH.read_text().splitlines():
        try:
            labels.append(json.loads(line))
        except Exception:
            continue
    return labels


# Page config
st.set_page_config(page_title="PhantomGuard Dashboard", layout="wide", page_icon="👻")

# Header
st.title('👻 PhantomGuard Dashboard')
st.markdown("*Deception-based threat detection system*")

# Sidebar
st.sidebar.header('🎛️ Controls')
if st.sidebar.button('🔄 Reload Data'):
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 System Status")
alerts_exist = LOG_PATH.exists()
blocks_exist = BLOCK_LOG_PATH.exists()
st.sidebar.markdown(f"**Alerts Log:** {'✅' if alerts_exist else '❌'}")
st.sidebar.markdown(f"**Block Log:** {'✅' if blocks_exist else '❌'}")

# Main content
tab1, tab2, tab3 = st.tabs(["🚨 Recent Alerts", "🚫 Block Actions", "🏷️ Labels"])

with tab1:
    st.header('🚨 Recent Alerts')
    
    if LOG_PATH.exists():
        try:
            lines = LOG_PATH.read_text().strip().splitlines()[-200:]
            data = []
            
            for line in lines:
                try:
                    parts = line.split(' ', 2)
                    if len(parts) >= 3:
                        timestamp, sig, payload = parts
                        e = json.loads(payload)
                        e['sig'] = sig
                        e['timestamp'] = float(timestamp)
                        data.append(e)
                except Exception:
                    continue
            
            if data:
                st.success(f"**{len(data)} alerts** in log (showing last 200)")
                
                for ev in reversed(data):
                    score = ev.get('score', 0)
                    event_type = ev.get('event_type', 'unknown')
                    path = ev.get('path', 'N/A')
                    
                    # Color code by severity
                    if score >= 80:
                        severity_color = "🔴"
                    elif score >= 60:
                        severity_color = "🟠"
                    elif score >= 40:
                        severity_color = "🟡"
                    else:
                        severity_color = "🟢"
                    
                    with st.expander(f"{severity_color} {event_type} | {path} | Score: {score}"):
                        # Display timestamp
                        if 'timestamp' in ev:
                            dt = datetime.fromtimestamp(ev['timestamp'])
                            st.caption(f"⏰ {dt.strftime('%Y-%m-%d %H:%M:%S')}")
                        
                        # Display event details
                        st.json(ev)
                        
                        # Check FP status
                        fp_list = load_fp_state()
                        is_fp = ev.get('sig') in fp_list
                        
                        # Action buttons
                        col1, col2, col3, col4 = st.columns([1, 1, 1, 2])
                        
                        if col1.button('✅ Benign', key=f"{ev.get('sig')}_benign"):
                            append_label({
                                'sig': ev.get('sig'),
                                'label': 'benign',
                                'timestamp': ev.get('timestamp', '')
                            })
                            st.success('Marked as benign')
                            st.rerun()
                        
                        if col2.button('⚠️ Attack', key=f"{ev.get('sig')}_attack"):
                            append_label({
                                'sig': ev.get('sig'),
                                'label': 'attack',
                                'timestamp': ev.get('timestamp', '')
                            })
                            st.success('Marked as attack')
                            st.rerun()
                        
                        if col3.button('❌ False Positive', key=f"{ev.get('sig')}_fp"):
                            if ev.get('sig') not in fp_list:
                                fp_list.append(ev.get('sig'))
                                save_fp_state(fp_list)
                            append_label({
                                'sig': ev.get('sig'),
                                'label': 'fp',
                                'timestamp': ev.get('timestamp', '')
                            })
                            st.success('Marked as false positive')
                            st.rerun()
                        
                        if is_fp:
                            st.info('🔕 This event is suppressed (marked as FP)')
            else:
                st.info('📭 No alerts parsed from log file')
        except Exception as e:
            st.error(f"Error reading alerts: {e}")
    else:
        st.info(f'📭 No alerts.log found at {LOG_PATH}')
        st.markdown("**Start PhantomGuard or run the demo:**")
        st.code("python3 phantomguard.py", language="bash")

with tab2:
    st.header('🚫 Block Actions')
    
    if BLOCK_LOG_PATH.exists():
        try:
            content = BLOCK_LOG_PATH.read_text()
            if content.strip():
                st.code(content, language='text')
                
                # Parse and summarize
                lines = content.strip().splitlines()
                st.info(f"**Total block actions:** {len(lines)}")
            else:
                st.info('No block actions recorded yet')
        except Exception as e:
            st.error(f"Error reading block log: {e}")
    else:
        st.info(f'No block.log found at {BLOCK_LOG_PATH}')

with tab3:
    st.header('🏷️ Label Management')
    
    labels = load_labels()
    
    if labels:
        st.success(f"**{len(labels)} labels** recorded")
        
        # Summary stats
        label_counts = {}
        for lab in labels:
            lbl = lab.get('label', 'unknown')
            label_counts[lbl] = label_counts.get(lbl, 0) + 1
        
        st.markdown("### Label Summary")
        cols = st.columns(len(label_counts))
        for i, (label, count) in enumerate(label_counts.items()):
            cols[i].metric(label.capitalize(), count)
        
        st.markdown("---")
        st.markdown("### All Labels")
        
        for i, lab in enumerate(labels):
            col1, col2 = st.columns([5, 1])
            
            with col1:
                label_type = lab.get('label', 'unknown')
                sig = lab.get('sig', 'N/A')
                timestamp = lab.get('timestamp', 'N/A')
                
                if label_type == 'benign':
                    emoji = "✅"
                elif label_type == 'attack':
                    emoji = "⚠️"
                elif label_type == 'fp':
                    emoji = "❌"
                else:
                    emoji = "❓"
                
                st.text(f"{emoji} {label_type.upper()} | Sig: {sig[:16]}... | Time: {timestamp}")
            
            with col2:
                if st.button('🗑️', key=f'del_{i}'):
                    # Rewrite file without this label
                    new_labels = [label_entry for j, label_entry in enumerate(labels) if j != i]
                    LABELS_PATH.write_text('\n'.join(json.dumps(x) for x in new_labels) + ("\n" if new_labels else ""))
                    st.success('Label deleted')
                    st.rerun()
    else:
        st.info('📭 No labels recorded yet. Mark some alerts above!')

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("### ℹ️ About")
st.sidebar.markdown("**PhantomGuard** v0.1")
st.sidebar.markdown("Lightweight deception system")