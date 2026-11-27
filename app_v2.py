"""V2 experimental interface; V1.0 app.py remains unchanged."""
import json
import pandas as pd
import streamlit as st
from src.geospatial import REGIONS, fetch_region
from src.images import reference_photo

st.set_page_config(page_title="Global Geospatial Explorer V2.0", layout="wide")
st.title("🌊 Global Geospatial Explorer — V2.0 (Development)")
st.caption("OBIS real occurrence samples | Approximate region windows | Not ocean-wide abundance estimates")
st.warning("V2.0 is under development. Region rectangles are approximate, not official ocean boundaries.")
region = st.selectbox("Ocean search region", list(REGIONS))
size = st.slider("Maximum records per geographic window", 10, 300, 100, 10)
name = st.text_input("Scientific name contains (optional; filters returned sample)", max_chars=120)
if st.button("Query OBIS region"):
    try:
        with st.spinner("Requesting real OBIS records..."):
            st.session_state["v2_evidence"] = fetch_region(region, size, name)
    except Exception as exc:
        st.error(f"OBIS request failed. No records were generated: {exc}")
if "v2_evidence" in st.session_state:
    evidence = st.session_state["v2_evidence"]
    if evidence["region"] != region or evidence["requested_per_window"] != size or evidence["scientific_name_filter"] != name.strip():
        st.info("Displayed results belong to the previous query. Click Query OBIS region to update.")
    quality = evidence["quality"]
    a, b, c = st.columns(3)
    a.metric("Validated sampled occurrences", quality["records"])
    b.metric("Rejected / outside selected window", evidence["rejected_count"])
    c.metric("Distinct scientific names in sample", quality["distinct_scientific_names"])
    st.caption("Missing fields in validated sample: event date {0}, dataset ID {1}, occurrence ID {2}.".format(
        quality["missing_event_date"], quality["missing_dataset_id"], quality["missing_occurrence_id"]))
    if evidence["records"]:
        df = pd.DataFrame(evidence["records"])
        st.map(df, latitude="latitude", longitude="longitude")
        if st.checkbox("Show optional species reference photos (iNaturalist)"):
            @st.cache_data(ttl=86400, show_spinner=False)
            def photo(name):
                return reference_photo(name)
            with st.spinner("Finding reference photographs..."):
                photos = {taxon: photo(taxon) for taxon in df["scientific_name"].dropna().unique()}
            df.insert(0, "reference_photo", df["scientific_name"].map(
                lambda taxon: (photos.get(taxon) or {}).get("image_url")))
            st.dataframe(df, use_container_width=True, column_config={
                "reference_photo": st.column_config.ImageColumn("Taxon reference photo")})
            credits = [{"scientific_name": taxon, "taxon_page": item["taxon_url"],
                        "attribution": item["attribution"], "license": item["license_code"]}
                       for taxon, item in photos.items() if item]
            with st.expander("Photo credits and licenses"):
                if credits:
                    st.dataframe(pd.DataFrame(credits), use_container_width=True,
                                 column_config={"taxon_page": st.column_config.LinkColumn("iNaturalist")})
                else:
                    st.write("No matched reference photographs.")
        else:
            st.dataframe(df, use_container_width=True)
    else:
        st.info("No matching records in the returned sample. This does not imply absence of species.")
    st.json({k: v for k, v in evidence.items() if k != "records"})
    st.download_button("Export V2 evidence JSON", json.dumps(evidence, ensure_ascii=False, indent=2),
                       file_name="obis_geospatial_evidence.json", mime="application/json")
