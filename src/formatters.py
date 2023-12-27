"""Formatters for streamlit app
"""
from humanize import intword


def sortGuidance(guidance) -> (dict, list[str]):
    reportDates = set()
    catDict = {}
    for g in guidance:
        reportDates.add(g["transcriptPeriod"]["reportDate"])
        if g["valueCategory"] not in catDict:
            catDict[g["valueCategory"]] = []
        catDict[g["valueCategory"]].append(g)
    return catDict, list(reportDates)


def fmt_value(value, unit):
    unit = unit.lower()
    unit_format = {"percent": "%", "percentage": "%", "dollars": "$", "USD": "$"}
    if value == "None" or value is None:
        return None

    is_number = isinstance(value, (int, float))
    if not is_number:
        return str(value)

    value_formatted = value if value < 100 else intword(value)
    unit_formatted = unit_format.get(unit, unit)

    if unit_formatted == "$":
        return unit_formatted + str(value_formatted)
    else:
        return str(value_formatted) + f" {unit_formatted}"


def get_value(value_dict: dict):
    formatted_values = {"low": None, "mid": None, "high": None}
    low_value = value_dict.get("low", None)
    mid_value = value_dict.get("mid", None)
    high_value = value_dict.get("high", None)
    if low_value is not None:
        formatted_values["low"] = fmt_value(value_dict['low']['amt'], value_dict['low']['unit'])
    else:
        formatted_values["low"] = fmt_value(value_dict["raw"].get("low", None), value_dict["raw"].get("unit", None))
    if high_value is not None:
        formatted_values["high"] = fmt_value(value_dict['high']['amt'], value_dict['high']['unit'])
    else:
        formatted_values["high"] = fmt_value(value_dict["raw"].get("high", None), value_dict["raw"].get("unit", None))
    if mid_value is not None:
        formatted_values["mid"] = fmt_value(value_dict['mid']['amt'], value_dict['mid']['unit'])
    else:
        formatted_values["mid"] = fmt_value(value_dict["raw"].get("mid", None), value_dict["raw"].get("unit", None))
    return formatted_values


def fmt_guidance_period(g: dict):
    if g["guidancePeriod"]["fiscalQuarter"] is not None:
        return f'Q{g["guidancePeriod"]["fiscalQuarter"]} {g["guidancePeriod"]["fiscalYear"]}'
    elif g["guidancePeriod"]["fiscalYear"] is not None:
        return f'{g["guidancePeriod"]["fiscalYear"]}'
    else:
        return g["guidancePeriod"]["raw"]
