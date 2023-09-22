from src.services.guidance_server import (
    get_companies,
    get_company_transcript_periods,
    get_company_guidance,
)
import streamlit as st
import pandas as pd
from datetime import datetime
from humanize import intword

# st.set_page_config(layout="wide")

st.divider()

st.title("Sequent")
st.subheader("Guidance")
st.divider()


# Store the initial value of widgets in session state
if "initial" not in st.session_state:
    st.session_state["initial"] = True
    st.session_state["company"] = ""
    st.session_state["guidance"] = []
    st.session_state["period"] = {"year": None, "quarter": None}


companies = get_companies()

col1, col2 = st.columns(2)

with col1:
    company_options = st.selectbox("Select a Ticker", companies, index=0, key="company")


def set_period_and_get_guidance():
    year = st.session_state.period["year"]
    quarter = st.session_state.period["quarter"]

    guidance = get_company_guidance(
        st.session_state.company, transcriptQuarter=quarter, transcriptYear=year
    )
    st.session_state.guidance = guidance

    st.session_state["guidance_grid_visible"] = True


with col2:
    if st.session_state.company != "":
        periods = get_company_transcript_periods(st.session_state.company)
        period_options = st.selectbox(
            "Select a Period",
            periods,
            key="period",
            index=0,
            on_change=set_period_and_get_guidance,
            format_func=lambda p: str(p["year"])
            + (f' Q{p.get("quarter")}' if p["quarter"] is not None else ""),
        )

if (
    st.session_state.company != ""
    and st.session_state.period["year"] is not None
    and st.session_state.period["quarter"] is not None
):
    set_period_and_get_guidance()


def iso_date_to_date(iso_timestamp):
    # return  datetime.fromisoformat(iso_timestamp).date().isoformat()
    return iso_timestamp.split("T")[0]


# actual guidance section
def sortGuidance(guidance) -> (dict, list[str]):
    reportDates = set()
    catDict = {}
    for g in guidance:
        reportDates.add(g["transcriptPeriod"]["reportDate"])
        if g["valueCategory"] not in catDict:
            catDict[g["valueCategory"]] = []
        catDict[g["valueCategory"]].append(g)
    return catDict, list(reportDates)


value_cat_to_label = {
    "unknown": "Other",
    "financial": "Financial",
    "keyMetrics": "Key Metrics",
    "nonRecurring": "Non-Recurring",
}

priority = ["financial", "keyMetrics", "nonRecurring", "unknown"]


def get_and_format_val(g: dict, type: str):
    value = g.get("value", {}).get(type, {}).get("amt", None)
    unit = g.get("value", {}).get(type, {}).get("unit", "")

    unit_format = {"percent": "%", "dollars": "$", "USD": "$"}

    is_number = isinstance(value, (int))
    if not is_number:
        return None

    value_formatted = value if value < 100 else intword(value)
    unit_formatted = unit_format.get(unit, unit)

    if unit_formatted == "$":
        return unit_formatted + str(value_formatted)
    else:
        return str(value_formatted) + f" {unit_formatted}"


if "guidance" in st.session_state and st.session_state.guidance is not None:
    sortedGuidance, reportDates = sortGuidance(st.session_state.guidance)

    guidance_categories = sorted(
        sortedGuidance.keys(),
        key=lambda x: priority.index(x) if x in priority else 1000,
    )
    for cat in guidance_categories:
        st.subheader(value_cat_to_label.get(cat, cat))

        dict_guidance = []
        for g in sortedGuidance[cat]:
            dict_guidance.append(
                {
                    "Line Item": g["lineItem"],
                    "Period": "Q"
                    + str(g["transcriptPeriod"]["fiscalQuarter"])
                    + " "
                    + str(g["transcriptPeriod"]["fiscalYear"]),
                    "Low": get_and_format_val(g, "low"),
                    "Midpoint": get_and_format_val(g, "mid"),
                    "High": get_and_format_val(g, "high"),
                    "Other": getattr(getattr(g, "qualitative", None), "value", None),
                    "Source": g["rawTranscriptSourceSentence"],
                }
            )
        guidance_df = pd.DataFrame.from_dict(dict_guidance)
        st.write(guidance_df)

        # TODO: last_revision, previous guidance

    st.write(f"Report Date(s): ", "".join(list(map(iso_date_to_date, reportDates))))
    # st.write(sortedGuidance)
