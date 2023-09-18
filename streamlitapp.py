from src.services.guidance_server import get_companies, get_company_guidance_periods, get_company_guidance 
import streamlit as st
import pandas as pd
from datetime import datetime
st.set_page_config(layout="wide")

st.title('Sequent')
st.subheader('Guidance')
st.divider()



# Store the initial value of widgets in session state
if "initial" not in st.session_state:
    st.session_state["companies"] = get_companies()
    st.session_state["initial"] = True
    st.session_state['company'] = None
    st.session_state['guidance'] = None



col1, col2 = st.columns(2)

with col1:
    print(f'companies:::::: {st.session_state["companies"]}')
    if st.session_state["companies"] is not None and len(st.session_state["companies"]) > 0:
        company_options = st.selectbox(
                'Select a Ticker',
                st.session_state["companies"],
                key='company'
            )

def set_period():
    year= st.session_state.period['year']
    quarter = st.session_state.period['quarter']

    guidance = get_company_guidance(st.session_state.company, year, quarter)
    st.session_state.guidance = guidance

    st.session_state['guidance_grid_visible'] = True

with col2:
    if st.session_state.company is not None :
        periods = get_company_guidance_periods(st.session_state.company)
        period_options = st.selectbox(
            'Select a Period',
            periods,
            key='period',
            on_change=set_period,
            format_func=lambda p: str(p["year"]) + (f' Q{p.get("quarter")}' if p["quarter"] is not None else "")
        )
        

def iso_date_to_date(iso_timestamp):
    # return  datetime.fromisoformat(iso_timestamp).date().isoformat()
    return iso_timestamp.split('T')[0]

# actual guidance section
def sortGuidance(guidance)-> (dict, list[str]):
    reportDates = set()
    catDict = {}
    for g in guidance:
        reportDates.add(g['reportDate'])
        if g['valueCategory'] not in catDict:
            catDict[g['valueCategory']] = []
        catDict[g['valueCategory']].append(g)
    return catDict, list(reportDates)


import math
millnames = ['','',' Million',' Billion',' Trillion']
def millify(n):
    n = float(n)
    millidx = max(0,min(len(millnames)-1,
                        int(math.floor(0 if n == 0 else math.log10(abs(n))/3))))
    return '{:.0f}{}'.format(n / 10**(3 * millidx), millnames[millidx])

value_cat_to_label = {
    'unknown': 'Other',
    'financial': 'Financial',
    'keyMetrics': 'Key Metrics',
    'nonRecurring': 'Non-Recurring',
}
def get_and_format_val(g: dict, type: str):
    value = g.get('value', {}).get(type, {}).get('amt', None)
    unit = g.get('value', {}).get(type, {}).get('unit', '')

    unit_format = {
        'percent':'%',
        'dollars':'$',
        'USD': '$'
    }
    
    is_number = isinstance(value, (int))
    if not is_number:
        return None

    value_formatted = value if value < 10000 else millify(value)
    unit_formatted = unit_format.get(unit, unit)

    if unit_formatted == '$':
        return unit_formatted + str(value_formatted)
    else: 
        return str(value_formatted) + f' {unit_formatted}'

if st.session_state.guidance:
    sortedGuidance, reportDates = sortGuidance(st.session_state.guidance)

    for cat in sortedGuidance.keys():
        st.subheader(value_cat_to_label.get(cat, cat))

        dict_guidance = []
        for g in sortedGuidance[cat]:
            dict_guidance.append({
                'Line Item' : g['lineItem'],
                'Low' : get_and_format_val(g, 'low'),
                'Midpoint' : get_and_format_val(g, 'mid'),
                'High' : get_and_format_val(g, 'high'),
                'Other' : getattr(getattr(g, 'qualitative', None), 'value', None),
                'Source' : g['rawTranscriptSourceSentence'],
            })
        guidance_df = pd.DataFrame.from_dict(dict_guidance)
        st.write(guidance_df)

            # TODO: last_revision, previous guidance

           

    st.write(f'Report Date(s): ', ''.join(list(map( iso_date_to_date, reportDates))) )
    # st.write(sortedGuidance) 