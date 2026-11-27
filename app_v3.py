"""V3 synthetic-only environmental dashboard. OBIS data is NOT merged here."""
import json
import urllib.error
import urllib.request
import pandas as pd
import streamlit as st

from src.sensors_v3 import SPECS, generate_observation
from src.evidence_v3 import export_evidence

API_URL = "http://127.0.0.1:8766"
st.set_page_config(page_title="Global Ocean Observatory — V3.0", layout="wide")
st.title("🌊 Global Ocean Observatory — V3.0")
st.subheader("Virtual Marine Sensors & HTTP Monitoring")
st.warning("SYNTHETIC DATA ONLY — Software-generated examples, not real ocean measurements or calibrated sensor readings.")
st.caption("Independent from V1.0/V2.0 OBIS occurrence observations. Local HTTP server required.")

def request_json(path, payload=None):
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        API_URL + path,
        data=data,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST" if payload is not None else "GET",
    )
    with urllib.request.urlopen(req, timeout=5) as response:
        return json.load(response)

try:
    health = request_json("/health")
    if health.get("mode") != "synthetic_only":
        st.error("Unexpected API mode; refusing to continue.")
        st.stop()
    st.success("Local HTTP API connected — synthetic-only mode")
except (urllib.error.URLError, TimeoutError, ValueError, OSError) as exc:
    st.error("Local HTTP API unavailable. Start it with: python -m src.api_v3")
    st.caption(str(exc))
    st.stop()

st.markdown("### Generate a virtual observation")
measurement = st.selectbox("Environmental parameter", list(SPECS), format_func=lambda x: x.replace("_", " ").title())
sample_index = st.number_input("Simulation index", min_value=0, max_value=1000000, value=0, step=1)
if st.button("Generate and send synthetic observation", type="primary"):
    try:
        observation = generate_observation(measurement, index=int(sample_index))
        result = request_json("/observations", observation)
        if result.get("source_type") != "synthetic_simulator":
            st.error("Unexpected provenance in API response")
        else:
            st.success("Synthetic observation stored" if result.get("stored") else "Duplicate synthetic observation already stored")
            st.json(result)
    except (urllib.error.URLError, TimeoutError, ValueError, OSError) as exc:
        st.error(f"Submission failed: {exc}")

st.markdown("### Stored synthetic observations")
try:
    response = request_json("/observations")
    if response.get("source_type") != "synthetic_simulator":
        st.error("Unexpected provenance in observations response")
        st.stop()
    records = response.get("records", [])
    if not records:
        st.info("No synthetic observations stored yet.")
    else:
        df = pd.DataFrame(records)
        df = df[df["source_type"].eq("synthetic_simulator")].copy()
        df["observed_at_utc"] = pd.to_datetime(df["observed_at_utc"], utc=True, errors="coerce")
        st.metric("Stored synthetic records (latest 100)", len(df))
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.markdown("### Historical charts by parameter")
        selected = st.selectbox("Parameter for chart", list(SPECS), key="chart_measurement",
                                format_func=lambda x: x.replace("_", " ").title())
        subset = df[df["measurement"].eq(selected)].dropna(subset=["observed_at_utc"]).sort_values("observed_at_utc")
        if not subset.empty:
            st.line_chart(subset.set_index("observed_at_utc")["value"], y_label=SPECS[selected][0])
        else:
            st.info("No stored samples for this parameter.")
        st.download_button(
            "Export synthetic records (JSON)",
            data=json.dumps(export_evidence(records), indent=2, ensure_ascii=False),
            file_name="v3_synthetic_observations.json", mime="application/json",
        )
except (urllib.error.URLError, TimeoutError, ValueError, OSError, KeyError) as exc:
    st.error(f"Could not retrieve observations: {exc}")

st.caption("Educational prototype. Values are simulated; SHA-256 is an integrity identifier, not evidence of physical accuracy.")
