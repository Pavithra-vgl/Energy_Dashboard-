import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from dateutil import tz

from utils import get_timeseries

st.header("⚡ Energy Mix (Renewables vs Conventional)")

# ---------------- Sidebar ----------------
with st.sidebar:
    st.caption("Data Mode: API only")

    berlin = tz.gettz("Europe/Berlin")
    now = pd.Timestamp.now(tz=berlin).floor("h")
    start_default = (now - pd.Timedelta(days=7)).date()
    end_default = now.date()

    start_date = st.date_input("Start date", value=start_default, key="mix_start")
    end_date = st.date_input("End date", value=end_default, key="mix_end")

    start_ts = pd.Timestamp(start_date, tz=berlin)
    end_ts = pd.Timestamp(end_date, tz=berlin) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)

    st.divider()
    st.subheader("Highlight")
    peak_threshold = st.slider("Peak load threshold (MW)", 30000, 90000, 65000, step=500)

# ---------------- Fetch timeseries ----------------
metrics = {
    "Load": "load",
    "Wind": "wind",
    "Solar": "solar",
}

dfs = {}
missing = []

for label, metric_key in metrics.items():
    df = get_timeseries(
        region="DE",
        metric_key=metric_key,
        resolution="hour",
        start=start_ts,
        end=end_ts,
    )

    if df is None or df.empty:
        missing.append(label)
        continue

    df = df.copy()
    df["ts"] = pd.to_datetime(df["ts"])
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df = df.dropna(subset=["ts", "value"]).rename(columns={"value": label})

    dfs[label] = df[["ts", label]]

if "Load" not in dfs:
    st.error("No Load data returned for this period. Try a different date range.", icon="❌")
    st.stop()

if missing:
    st.warning(
        f"No data returned for: {', '.join(missing)}. "
        "Energy Mix will still work where possible.",
        icon="⚠️",
    )

# ---------------- Merge safely ----------------
df = dfs["Load"].copy()

# inner join ensures same timestamps across series
for col in ["Wind", "Solar"]:
    if col in dfs:
        df = df.merge(dfs[col], on="ts", how="inner")

# if wind/solar missing entirely, set 0
if "Wind" not in df.columns:
    df["Wind"] = 0.0
if "Solar" not in df.columns:
    df["Solar"] = 0.0

# ---------------- FINAL SAFETY FILTER (fixes your Jan18->Dec25 issue) ----------------
df["ts"] = pd.to_datetime(df["ts"])
df = df[(df["ts"] >= start_ts) & (df["ts"] <= end_ts)]

if df.empty:
    st.warning("No overlapping data within the selected time window. Try a wider range.", icon="⚠️")
    st.stop()

# Debug range shown (helpful + professional)
st.caption(f"Showing data from **{df['ts'].min()}** to **{df['ts'].max()}**")

# ---------------- Derived columns ----------------
df["Renewables"] = df["Wind"] + df["Solar"]
df["Conventional"] = np.clip(df["Load"] - df["Renewables"], 0, None)
df["Renewables Share (%)"] = np.where(df["Load"] > 0, 100 * df["Renewables"] / df["Load"], np.nan)
df["Peak"] = df["Load"] > peak_threshold

# ---------------- KPIs ----------------
c1, c2, c3 = st.columns(3)
c1.metric("Avg Load (MW)", f"{df['Load'].mean():.0f}")
c2.metric("Avg Renewables Share (%)", f"{df['Renewables Share (%)'].mean():.1f}")
c3.metric("Peak Hours", f"{int(df['Peak'].sum())}")

# ---------------- Stacked mix chart ----------------
mix = df.melt(
    id_vars=["ts"],
    value_vars=["Renewables", "Conventional"],
    var_name="Type",
    value_name="MW",
)

fig = px.area(mix, x="ts", y="MW", color="Type", title="Generation Mix (Stacked)")
fig.update_layout(xaxis_title="Time", yaxis_title="MW")
st.plotly_chart(fig, use_container_width=True)

# ---------------- Renewables share line ----------------
fig2 = px.line(df, x="ts", y="Renewables Share (%)", title="Renewables Share Over Time")
fig2.update_layout(xaxis_title="Time", yaxis_title="Renewables Share (%)")
st.plotly_chart(fig2, use_container_width=True)

# ---------------- Peak table ----------------
st.subheader("⏱ Peak Hours (Drill-down table)")
peaks = df[df["Peak"]].sort_values("ts", ascending=False)[["ts", "Load", "Renewables", "Renewables Share (%)"]]

if peaks.empty:
    st.success("No peak hours in this period for the chosen threshold.")
else:
    st.dataframe(peaks, use_container_width=True)
