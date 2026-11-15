"""Ocean & Biodiversity Evidence Analyzer V1.0 — first working slice."""
import json

import pandas as pd
import streamlit as st
from src.core import fetch_obis

st.set_page_config(page_title='Ocean & Biodiversity Evidence Analyzer', layout='wide')
st.title('🌊 Ocean & Biodiversity Evidence Analyzer V1.0')
st.caption('COP31 AI Solutions Lab | Day 9 | Real OBIS records — no simulated observations')
st.info('This first build supports OBIS occurrence data only. Satellite, drone, IoT and AI modules are planned, not implemented.')
size = st.slider('Maximum records to request', 10, 300, 100, step=10)
if st.button('Load real biodiversity observations'):
    try:
        with st.spinner('Fetching observations from OBIS...'):
            evidence = fetch_obis(size)
        st.session_state['evidence'] = evidence
    except Exception as exc:
        st.error(f'Data retrieval failed; no observations were generated: {exc}')
if 'evidence' in st.session_state:
    e = st.session_state['evidence']
    st.metric('Validated occurrences', len(e['records']))
    st.metric('Rejected records', e['rejected_count'])
    st.caption('Occurrence counts are not species abundance or total biodiversity estimates.')
    if e['records']:
        df = pd.DataFrame(e['records'])
        st.map(df, latitude='latitude', longitude='longitude')
        st.dataframe(df, use_container_width=True)
    st.json({k: v for k, v in e.items() if k != 'records'})
    st.download_button('Export evidence JSON', json.dumps(e, indent=2, ensure_ascii=False), 'obis_evidence.json', 'application/json')
