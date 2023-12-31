from src.services.guidance_server import (
    get_companies,
    get_company_transcript_periods,
    get_company_guidance,
)
from src.formatters import (
    fmt_guidance_period,
    get_value,
    sortGuidance,
)
import streamlit as st
import pandas as pd
from datetime import datetime


st.set_page_config(layout="wide")

st.divider()

st.title("Sequent")
st.subheader("Guidance")
st.divider()

# Store the initial value of widgets in session state
if "tickers" not in st.session_state:
    st.session_state.tickers = get_companies()


col1, col2 = st.columns(2)

with col1:
    if st.session_state.tickers is not None:
        st.selectbox(
            label="Select a Ticker",
            options=st.session_state["tickers"],
            key="company",
        )


def set_period_and_get_guidance():
    year = st.session_state.period["year"]
    quarter = st.session_state.period["quarter"]

    st.session_state.guidance = get_company_guidance(
        st.session_state.company, transcriptQuarter=quarter, transcriptYear=year
    )


with col2:
    if st.session_state.company:
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
    return iso_timestamp.split("T")[0]


value_cat_to_label = {
    "unknown": "Other",
    "financial": "Financial",
    "keyMetrics": "Key Metrics",
    "nonRecurring": "Non-Recurring",
}


priority = ["financial", "keyMetrics", "nonRecurring", "unknown"]

if "guidance" in st.session_state:
    sortedGuidance, reportDates = sortGuidance(st.session_state.guidance)

    st.write(f"Earnings Call Date: ", "".join(list(map(iso_date_to_date, reportDates))))

    guidance_categories = sorted(
        sortedGuidance.keys(),
        key=lambda x: priority.index(x) if x in priority else 1000,
    )
    for cat in guidance_categories:
        st.subheader(value_cat_to_label.get(cat, cat))

        dict_guidance = []
        for g in sortedGuidance[cat]:
            formatted_values = get_value(g['value'])
            dict_guidance.append(
                {
                    "Line Item": g["lineItem"],
                    "Period": fmt_guidance_period(g),
                    "Low": formatted_values.get("low", None),
                    "Midpoint": formatted_values.get("mid", None),
                    "High": formatted_values.get("high", None),
                    "Source": g["rawTranscriptSourceSentence"],
                    "Source Paragraph": g["rawTranscriptSourceParagraph"],
                }
            )

        col_config = {
            "Line Item": st.column_config.TextColumn(
                "Line Item",
                help="",
                default="st.",
                max_chars=50
            ),
            "Source": st.column_config.TextColumn(
                "Source",
                help="Double click to expand",
                default="st.",
                width=None
            ),
            "Source Paragraph": st.column_config.TextColumn(
                "Source Paragraph",
                help="Double click to expand",
                default="st.",
                width=None
            )
        }
        guidance_df = pd.DataFrame.from_dict(dict_guidance)
        guidance_df.set_index("Line Item", inplace=True)
        # guidance_df_styled = guidance_df.style.set_properties(**{
        #     'width': '50px',
        #     'white-space': 'normal'
        # })
        st.dataframe(guidance_df, column_config=col_config)

        # TODO: last_revision, previous guidance
