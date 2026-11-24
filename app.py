"""Ocean & Biodiversity Evidence Analyzer V1.0 — OBIS evidence + optional taxon photos."""
import json

import pandas as pd
import streamlit as st
from src.core import fetch_obis
from src.images import reference_photo

st.set_page_config(page_title='Ocean & Biodiversity Evidence Analyzer', layout='wide')
st.title('🌊 Ocean & Biodiversity Evidence Analyzer V1.0')
st.caption('COP31 AI Solutions Lab | Day 9 | Real OBIS records — no simulated observations')
st.info('This build supports OBIS occurrence data and optional taxon reference photos. Satellite, drone, IoT and AI modules are planned, not implemented.')

size = st.slider('Maximum records to request', 10, 300, 100, step=10)
if st.button('Load real biodiversity observations'):
    try:
        with st.spinner('Fetching observations from OBIS...'):
            evidence = fetch_obis(size)
        st.session_state['evidence'] = evidence
    except Exception as exc:
        st.error(f'Data retrieval failed; no observations were generated: {exc}')

@st.cache_data(ttl=86400, show_spinner=False)
def cached_reference_photo(name):
    return reference_photo(name)

if 'evidence' in st.session_state:
    e = st.session_state['evidence']
    st.metric('Validated occurrences', len(e['records']))
    st.metric('Rejected records', e['rejected_count'])
    st.caption('Occurrence counts are not species abundance or total biodiversity estimates.')
    if e['records']:
        df = pd.DataFrame(e['records'])
        st.map(df, latitude='latitude', longitude='longitude')
        show_photos = st.checkbox('Show species reference photos (iNaturalist; optional)', value=False)
        if show_photos:
            st.caption('Photos illustrate the matched species, NOT the specific OBIS observation. '
                       'Missing or ambiguous matches remain blank. Photo credits and source links are shown below.')
            unique_names = df['scientific_name'].dropna().unique().tolist()
            photos = {}
            with st.spinner('Looking up taxon reference photos (may take a moment)...'):
                for name in unique_names:
                    photos[name] = cached_reference_photo(name)
            df.insert(0, 'reference_photo', df['scientific_name'].map(
                lambda name: (photos.get(name) or {}).get('image_url')))
            st.dataframe(df, use_container_width=True, column_config={
                'reference_photo': st.column_config.ImageColumn('Species reference photo', help='Taxon illustration; not the OBIS observation')
            })
            credits = [
                {'scientific_name': name, 'photo_source': info['taxon_url'],
                 'attribution': info['attribution'], 'license': info['license_code']}
                for name, info in photos.items() if info
            ]
            st.caption(f'Reference photos found for {len(credits)} of {len(unique_names)} distinct taxon names.')
            if credits:
                with st.expander('Photo sources, credits and licenses'):
                    st.dataframe(pd.DataFrame(credits), use_container_width=True,
                                 column_config={'photo_source': st.column_config.LinkColumn('iNaturalist taxon page')})
        else:
            st.dataframe(df, use_container_width=True)
    st.json({k: v for k, v in e.items() if k != 'records'})
    st.download_button('Export evidence JSON', json.dumps(e, indent=2, ensure_ascii=False),
                       'obis_evidence.json', 'application/json')
