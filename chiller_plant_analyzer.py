import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="ASHRAE Chiller Plant Analyzer", layout="wide")
st.title("🏭 ASHRAE Chiller Plant Performance Analyzer")
st.markdown("Analyze chillers, pumps, and cooling towers using ASHRAE formulas in SI & I-P units. Export results and visualize performance.")

# --- Unit System ---
unit_system = st.sidebar.radio("Select Unit System", ["SI", "I-P"])

# --- Chiller Performance ---
st.header("🌬️ Chiller Performance")
cooling_capacity = st.number_input("Cooling Capacity", value=100.0, help="RT (I-P) or kW (SI)")
power_input = st.number_input("Power Input", value=60.0, help="kW")

if unit_system == "I-P":
    kw_per_ton = power_input / cooling_capacity
    eer = (cooling_capacity * 12000) / (power_input * 1000)
    cop = eer / 3.412
else:
    cop = cooling_capacity / power_input
    eer = cop * 3.412
    kw_per_ton = 3.5 / cop

st.success(f"COP: {round(cop, 2)} | EER: {round(eer, 2)} | kW/Ton: {round(kw_per_ton, 2)}")

# --- Pump Performance ---
st.header("🚰 Chilled Water Pump")
flow = st.number_input("Flow Rate", value=0.02, help="m³/s or ft³/s")
head = st.number_input("Head", value=30.0, help="m or ft")
pump_power = st.number_input("Pump Power Input", value=6.0, help="kW")

density = 1000 if unit_system == "SI" else 62.4 * 1.3558
g = 9.81 if unit_system == "SI" else 32.174
hydraulic_power = flow * head * density * g / 1000
efficiency = (hydraulic_power / pump_power) * 100
st.success(f"Pump Efficiency: {round(efficiency, 2)}%")

# --- Cooling Tower Performance ---
st.header("🌫️ Cooling Tower")
cw_in = st.number_input("CW Inlet Temp", value=35.0)
cw_out = st.number_input("CW Outlet Temp", value=30.0)
wet_bulb = st.number_input("Ambient Wet Bulb Temp", value=28.0)

range = cw_in - cw_out
approach = cw_out - wet_bulb
effectiveness = range / (range + approach)
st.success(f"Range: {range}° | Approach: {approach}° | Effectiveness: {round(effectiveness * 100, 2)}%")

# --- IPLV/NPLV Calculation ---
st.header("📉 Chiller Part-Load Performance")
kw_100 = st.number_input("kW/Ton @ 100% Load", value=0.6)
kw_75 = st.number_input("kW/Ton @ 75% Load", value=0.65)
kw_50 = st.number_input("kW/Ton @ 50% Load", value=0.72)
kw_25 = st.number_input("kW/Ton @ 25% Load", value=0.85)

def calc_iplv(values):
    weights = [0.01, 0.42, 0.45, 0.12]
    return round(1 / sum(w / e for w, e in zip(weights, values)), 3)

iplv = calc_iplv([kw_100, kw_75, kw_50, kw_25])
st.success(f"IPLV/NPLV = {iplv} kW/Ton")

# --- Delta-T Optimization ---
st.header("🧊 Chilled Water Flow Optimization")
capacity_kw = st.number_input("Cooling Capacity (kW)", value=1000.0)
delta_T = st.slider("Chilled Water ΔT (°C)", min_value=4.0, max_value=16.0, value=6.0)
cp = 4.187
density_si = 997
flow_rate = capacity_kw / (cp * density_si * delta_T)
st.info(f"Required Flow Rate = {round(flow_rate, 3)} m³/s")

# --- COP vs Load Chart ---
st.header("📊 COP vs Load")
loads = [25, 50, 75, 100]
cop_values = [cop * (1 - 0.1 * (1 - l / 100)) for l in loads]
fig, ax = plt.subplots()
ax.plot(loads, cop_values, marker='o')
ax.set_xlabel("Load (%)")
ax.set_ylabel("COP")
ax.set_title("Chiller COP vs Load")
st.pyplot(fig)

# --- CSV Export ---
st.header("📁 Export Report")
data = {
    "Cooling Capacity": [cooling_capacity],
    "Power Input": [power_input],
    "COP": [cop],
    "EER": [eer],
    "kW/Ton": [kw_per_ton],
    "Pump Efficiency (%)": [efficiency],
    "Tower Range": [range],
    "Tower Approach": [approach],
    "Tower Effectiveness (%)": [effectiveness * 100],
    "IPLV/NPLV (kW/Ton)": [iplv],
    "Chilled Water ΔT (°C)": [delta_T],
    "Flow Rate (m³/s)": [flow_rate]
}
df = pd.DataFrame(data)
csv = df.to_csv(index=False).encode("utf-8")
st.download_button("📥 Download CSV Report", csv, "chiller_plant_report.csv", "text/csv")
