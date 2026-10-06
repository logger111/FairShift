import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="FairShift Engine v2.0 | Operational Scheduling Simulator",
    page_icon="⚖️",
    layout="wide"
)

# --- TITLE & HEADER ---
st.title("⚖️ FairShift Engine v2.0")
st.caption("Advanced B2B Operational Scheduling & Fairness Optimization Simulator")
st.markdown("---")

# --- SIDEBAR: OPERATIONAL CONFIGURATION ---
st.sidebar.header("⚙️ Operational Parameters")

# 1. Team & Skill Composition
st.sidebar.subheader("1. Workforce & Skills")
total_staff = st.sidebar.number_input("Total Workforce Size", min_value=3, max_value=150, value=12, step=1)
senior_ratio = st.sidebar.slider("Senior Staff Percentage (%)", min_value=0, max_value=100, value=25, step=5)
hard_constraint_staff = st.sidebar.number_input("Staff with Fixed Restrictions (No Weekends/Nights)", min_value=0, max_value=int(total_staff), value=3, step=1)

# Calculate Seniors
num_seniors = int(round((senior_ratio / 100) * total_staff))

# 2. Shift Demand Architecture
st.sidebar.subheader("2. Shift Structure & Demand")
shifts_per_day = st.sidebar.selectbox("Shifts per Day", options=[1, 2, 3, 4], index=2, help="1: Day only, 2: Day/Night, 3: Morning/Evening/Night, 4: 6-hour rotas")
required_staff_per_shift = st.sidebar.number_input("Required Staff per Shift Slot", min_value=1, max_value=20, value=2, step=1)
sim_weeks = st.sidebar.slider("Simulation Horizon (Weeks)", min_value=1, max_value=12, value=4)

# 3. Policy & Rest Constraints
st.sidebar.subheader("3. Labor & Safety Constraints")
max_days_per_week = st.sidebar.slider("Max Working Days per Employee/Week", min_value=3, max_value=7, value=5)
strict_skill_coverage = st.sidebar.checkbox("Enforce Strict Senior Coverage (≥1 Senior per Shift)", value=True)

# --- CALCULATE TOTAL CAPACITY VS DEMAND ---
total_days = sim_weeks * 7
total_shift_slots_needed = total_days * shifts_per_day * required_staff_per_shift
max_possible_employee_shifts = total_staff * max_days_per_week * sim_weeks

# --- HARD CAPACITY CHECK (CRITICAL OVERLOAD DETECTION) ---
is_overloaded = total_shift_slots_needed > max_possible_employee_shifts

# --- ALGORITHM ENGINE SIMULATION ---
np.random.seed(42)

# Generate Employee Database
employees = []
for i in range(1, total_staff + 1):
    emp_id = f"EMP_{i:02d}"
    is_senior = i <= num_seniors
    is_restricted = (not is_senior) and (i > (total_staff - hard_constraint_staff))
    
    tier = "Restricted (No Weekend/Night)" if is_restricted else ("Senior Flexible" if is_senior else "Standard Flexible")
    employees.append({
        "ID": emp_id,
        "Role": "Senior" if is_senior else "Junior",
        "Tier": tier,
        "Is_Restricted": is_restricted,
        "Is_Senior": is_senior,
        "Assigned_Shifts": 0,
        "Weekend_Shifts": 0,
        "Night_Shifts": 0
    })

df_staff = pd.DataFrame(employees)

# Shift Allocation Logic
if not is_overloaded:
    # Distribute shifts among flexible and restricted staff
    for day in range(total_days):
        is_weekend = (day % 7) in [5, 6]  # Fri/Sat
        for shift_idx in range(shifts_per_day):
            is_night = (shifts_per_day >= 3 and shift_idx == (shifts_per_day - 1))
            
            # Eligible workers
            eligible_mask = df_staff["Assigned_Shifts"] < (max_days_per_week * sim_weeks)
            if is_weekend or is_night:
                eligible_mask = eligible_mask & (~df_staff["Is_Restricted"])
            
            eligible_indices = df_staff[eligible_mask].index.tolist()
            
            # Fallback if constraint bottleneck occurs
            if len(eligible_indices) < required_staff_per_shift:
                eligible_indices = df_staff.index.tolist() # Forced assignment causing inequality
            
            # Prioritize least-worked staff for fairness
            sorted_indices = sorted(eligible_indices, key=lambda x: (df_staff.loc[x, "Assigned_Shifts"], np.random.rand()))
            selected = sorted_indices[:required_staff_per_shift]
            
            for idx in selected:
                df_staff.loc[idx, "Assigned_Shifts"] += 1
                if is_weekend:
                    df_staff.loc[idx, "Weekend_Shifts"] += 1
                if is_night:
                    df_staff.loc[idx, "Night_Shifts"] += 1

# --- FAIRNESS SCORE INDEX (FSI) CALCULATION ---
if is_overloaded:
    fsi_score = 0.0
else:
    # FSI calculated based on standard deviation of workload distribution
    assigned = df_staff["Assigned_Shifts"].values
    mean_shifts = np.mean(assigned)
    std_shifts = np.std(assigned)
    
    if mean_shifts > 0:
        cv = std_shifts / mean_shifts # Coefficient of variation
        fsi_score = max(0.0, min(100.0, round((1 - cv) * 100, 1)))
    else:
        fsi_score = 100.0

# --- DASHBOARD UI DISPLAY ---

# 🚨 OVERLOAD ALERT BANNER
if is_overloaded:
    st.error(f"🚨 **CRITICAL CAPACITY ERROR: IMPOSSIBLE SCHEDULE**\n\n"
             f"• **Demand:** You need **{total_shift_slots_needed}** shift-slots to cover operations.\n"
             f"• **Supply Limit:** Your workforce of {total_staff} (working max {max_days_per_week} days/week) can only provide **{max_possible_employee_shifts}** shift-slots.\n\n"
             f"👉 **Action Required:** Increase workforce size, increase max days per week, or reduce required staff per shift.")

# Top Metrics Row
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="Total Required Slots", value=total_shift_slots_needed)

with col2:
    st.metric(label="Available Capacity", value=max_possible_employee_shifts)

with col3:
    senior_cov = f"{num_seniors} ({round(num_seniors/total_staff*100)}%)"
    st.metric(label="Senior Workforce", value=senior_cov)

with col4:
    if is_overloaded or fsi_score < 60:
        fsi_color = "🔴 Critical"
    elif fsi_score < 80:
        fsi_color = "🟡 Warning"
    else:
        fsi_color = "🟢 Optimal"
    st.metric(label="Fairness Index (FSI)", value=f"{fsi_score}%", delta=fsi_color, delta_color="normal" if fsi_score>=80 else "inverse")

st.markdown("---")

# Status Alert Box
if not is_overloaded:
    if fsi_score >= 80:
        st.success(f"🟢 **HEALTHY SCHEDULE (FSI: {fsi_score}%):** Workload is evenly distributed across eligible staff with safe skill coverage.")
    elif fsi_score >= 65:
        st.warning(f"🟡 **MODERATE INEQUALITY (FSI: {fsi_score}%):** Restricted staff preferences are forcing standard/flexible employees to bear a heavier weekend/night load.")
    else:
        st.error(f"🔴 **CRITICAL WORKLOAD BURNOUT (FSI: {fsi_score}%):** Extreme distribution imbalance! A small subset of employees is taking almost all unpopular shifts.")

# --- ANALYTICS CHARTS & TABLES ---
if not is_overloaded:
    st.subheader("📊 Workload & Shift Allocation Breakdown")
    
    col_chart, col_table = st.columns([3, 2])
    
    with col_chart:
        fig = px.bar(
            df_staff,
            x="ID",
            y=["Assigned_Shifts", "Weekend_Shifts", "Night_Shifts"],
            title="Assigned Shifts per Employee (Total vs Unpopular)",
            labels={"value": "Number of Shifts", "ID": "Employee ID", "variable": "Shift Type"},
            barmode="group",
            color_discrete_sequence=["#1f77b4", "#ff7f0e", "#d62728"]
        )
        st.plotly_chart(fig, use_container_width=True)
        
    with col_table:
        st.subheader("📋 Roster Summary Table")
        st.dataframe(
            df_staff[["ID", "Role", "Tier", "Assigned_Shifts", "Weekend_Shifts", "Night_Shifts"]],
            hide_index=True,
            use_container_width=True
        )
        
        # CSV Download Button
        csv_data = df_staff.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Roster Summary (CSV)",
            data=csv_data,
            file_name=f"FairShift_Roster_{total_staff}staff_{sim_weeks}w.csv",
            mime="text/csv"
        )