import os, time, uuid, requests, streamlit as st
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

MID = st.secrets.get("GA_MEASUREMENT_ID") or os.getenv("GA_MEASUREMENT_ID")
SEC = st.secrets.get("GA_API_SECRET")     or os.getenv("GA_API_SECRET")
ENDPOINT = "https://www.google-analytics.com/mp/collect"

def _cid():
    if "ga_client_id" not in st.session_state:
        st.session_state["ga_client_id"] = str(uuid.uuid4())
    return st.session_state["ga_client_id"]

def send_page_view(page_location: str | None = None, page_title: str | None = None) -> bool:
    if not (MID and SEC):
        return False
    params = {"measurement_id": MID, "api_secret": SEC}
    payload = {
        "client_id": _cid(),
        "timestamp_micros": int(time.time()*1_000_000),
        "events": [{
            "name": "page_view",
            "params": {
                "page_location": page_location or "https://optipower.streamlit.app/",
                "page_title": page_title or "OptiPower App",
            }
        }]
    }
    try:
        r = requests.post(ENDPOINT, params=params, json=payload, timeout=4)
        return r.status_code in (200, 204)
    except Exception:
        return False
