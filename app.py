import streamlit as st
import random
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# -----------------------------
# Configuration from internship code
# -----------------------------
MAX_USAGE_PER_MIN = 5.0
LEAK_DETECTION_THRESHOLD = 0.5


def get_water_flow():
    """Simulate a water-flow sensor reading."""
    rand = random.random()

    if rand < 0.7:
        return round(random.uniform(0, 5), 2)
    elif rand < 0.9:
        return round(random.uniform(0.1, 0.8), 2)
    else:
        return round(random.uniform(5, 10), 2)


def check_alert(flow_rate):
    """Classify the reading using the thresholds in the original project."""
    if flow_rate > MAX_USAGE_PER_MIN:
        return "High Usage"
    elif 0 < flow_rate < LEAK_DETECTION_THRESHOLD:
        return "Possible Leakage"
    return "Normal"


def generate_readings(num_readings):
    rows = []

    for i in range(num_readings):
        flow = get_water_flow()
        rows.append(
            {
                "Reading": i + 1,
                "Timestamp": datetime.now().strftime("%H:%M:%S"),
                "Flow Rate (L/min)": flow,
                "Status": check_alert(flow),
            }
        )

    return pd.DataFrame(rows)


# -----------------------------
# Page configuration
# -----------------------------
st.set_page_config(
    page_title="Smart Water Monitoring Dashboard",
    page_icon="💧",
    layout="wide",
)

st.title("💧 Smart Water Monitoring Dashboard")
st.caption("Water Resource Management — simulation and threshold-based anomaly detection")

# Sidebar
st.sidebar.header("⚙️ Dashboard Controls")
num_readings = st.sidebar.slider(
    "Number of sensor readings",
    min_value=5,
    max_value=50,
    value=20,
)

st.sidebar.markdown("### Detection thresholds")
st.sidebar.info(
    f"High usage: > {MAX_USAGE_PER_MIN} L/min\n\n"
    f"Possible leakage: < {LEAK_DETECTION_THRESHOLD} L/min"
)

if "df" not in st.session_state:
    st.session_state.df = None

if st.sidebar.button("🔄 Generate New Readings", use_container_width=True):
    st.session_state.df = generate_readings(num_readings)

# Generate initial data
if st.session_state.df is None:
    st.session_state.df = generate_readings(num_readings)

df = st.session_state.df

# -----------------------------
# KPI calculations
# -----------------------------
normal_count = int((df["Status"] == "Normal").sum())
leak_count = int((df["Status"] == "Possible Leakage").sum())
high_count = int((df["Status"] == "High Usage").sum())

average_flow = df["Flow Rate (L/min)"].mean()
maximum_flow = df["Flow Rate (L/min)"].max()

# -----------------------------
# KPI cards
# -----------------------------
c1, c2, c3, c4 = st.columns(4)

c1.metric("📊 Average Flow", f"{average_flow:.2f} L/min")
c2.metric("💧 Normal", normal_count)
c3.metric("⚠️ High Usage", high_count)
c4.metric("🚨 Possible Leakage", leak_count)

st.divider()

# -----------------------------
# Alerts
# -----------------------------
st.subheader("🚨 Current Alerts")

alerts = df[df["Status"] != "Normal"]

if alerts.empty:
    st.success("✅ No abnormal readings detected.")
else:
    for _, row in alerts.iterrows():
        if row["Status"] == "Possible Leakage":
            st.warning(
                f"💧 Reading {int(row['Reading'])}: "
                f"{row['Flow Rate (L/min)']:.2f} L/min — Possible leakage detected."
            )
        else:
            st.error(
                f"⚠️ Reading {int(row['Reading'])}: "
                f"{row['Flow Rate (L/min)']:.2f} L/min — Abnormally high water usage."
            )

# -----------------------------
# Main chart
# -----------------------------
st.subheader("📈 Water Flow Monitoring")

fig, ax = plt.subplots(figsize=(12, 5))

ax.plot(
    df["Reading"],
    df["Flow Rate (L/min)"],
    marker="o",
    label="Flow Rate",
)

ax.axhline(
    MAX_USAGE_PER_MIN,
    linestyle="--",
    label="High Usage Threshold",
)

ax.axhline(
    LEAK_DETECTION_THRESHOLD,
    linestyle="--",
    label="Leak Threshold",
)

ax.set_xlabel("Reading Number")
ax.set_ylabel("Flow Rate (L/min)")
ax.set_title("Water Flow Rate Over Readings")
ax.grid(True, alpha=0.25)
ax.legend()

st.pyplot(fig, use_container_width=True)

# -----------------------------
# Status distribution
# -----------------------------
st.subheader("📊 Status Distribution")

status_counts = df["Status"].value_counts()

fig2, ax2 = plt.subplots(figsize=(8, 4))
ax2.bar(status_counts.index, status_counts.values)
ax2.set_xlabel("Status")
ax2.set_ylabel("Number of Readings")
ax2.set_title("Water Monitoring Status")
ax2.tick_params(axis="x", rotation=15)
st.pyplot(fig2, use_container_width=True)

# -----------------------------
# Readings table
# -----------------------------
st.subheader("📋 Sensor Readings")

display_df = df.copy()
display_df["Flow Rate (L/min)"] = display_df["Flow Rate (L/min)"].round(2)

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True,
)

# -----------------------------
# Download report
# -----------------------------
csv_data = df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="⬇️ Download Water Usage Report",
    data=csv_data,
    file_name="water_usage_report.csv",
    mime="text/csv",
)

st.caption(
    "Note: Readings are simulated using the same threshold-based logic as the internship notebook."
)
