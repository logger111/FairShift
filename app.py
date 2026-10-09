import streamlit as st
import pandas as pd
import numpy as np

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="FairShift Engine v3.0 | Real-World Roster Builder",
    page_icon="📅",
    layout="wide"
)

st.title("📅 FairShift Engine v3.0 — Real-World Roster & Constraint Builder")
st.caption("Custom Staff Management, Individual Availability & Dynamic Shift Assignment")
st.markdown("---")

# --- INITIALIZE SESSION STATE FOR STAFF & RESTRICTIONS ---
if "staff_list" not in st.session_state:
    st.session_state.staff_list = [
        {"Name": "Alex Green", "Role": "Senior", "Max_Days": 5, "No_Nights": False, "Unavailable_Days": ["Sunday"]},
        {"Name": "Sarah Cole", "Role": "Senior", "Max_Days": 5, "No_Nights": False, "Unavailable_Days": []},
        {"Name": "David Miller", "Role": "Junior", "Max_Days": 4, "No_Nights": True, "Unavailable_Days": ["Saturday", "Sunday"]},
        {"Name": "Elena Rostova", "Role": "Junior", "Max_Days": 5, "No_Nights": False, "Unavailable_Days": ["Wednesday"]},
        {"Name": "Michael Scott", "Role": "Junior", "Max_Days": 5, "No_Nights": False, "Unavailable_Days": []},
        {"Name": "Rachel Adams", "Role": "Senior", "Max_Days": 5, "No_Nights": True, "Unavailable_Days": []},
    ]

# --- TABS FOR NAVIGATION ---
tab_staff, tab_roster, tab_analytics = st.tabs([
    "👥 Staff & Restrictions", 
    "🗓️ Weekly Roster Builder", 
    "📊 Diagnostics & Fairness"
])

# ==========================================
# TAB 1: STAFF MANAGEMENT & RESTRICTIONS
# ==========================================
with tab_staff:
    st.subheader("👥 Manage Staff & Individual Availability")
    st.write("Add real employee names and define their individual availability constraints.")
    
    with st.expander("➕ Add New Employee", expanded=False):
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            new_name = st.text_input("Full Name")
            new_role = st.selectbox("Role", ["Senior", "Junior"])
        with col_b:
            new_max_days = st.number_input("Max Days/Week", min_value=1, max_value=7, value=5)
            new_no_nights = st.checkbox("Cannot work Night Shifts")
        with col_c:
            new_unavail = st.multiselect("Unavailable Days", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
            submit_btn = st.button("Save Employee")
            
        if submit_btn and new_name:
            st.session_state.staff_list.append({
                "Name": new_name,
                "Role": new_role,
                "Max_Days": new_max_days,
                "No_Nights": new_no_nights,
                "Unavailable_Days": new_unavail
            })
            st.success(f"Added {new_name} to workforce!")
            st.rerun()

    df_staff_ui = pd.DataFrame(st.session_state.staff_list)
    df_staff_ui["Unavailable_Days"] = df_staff_ui["Unavailable_Days"].apply(lambda x: ", ".join(x) if x else "None")
    
    st.dataframe(df_staff_ui, use_container_width=True, hide_index=True)
    
    if st.button("🗑️ Reset to Default Team"):
        st.session_state.pop("staff_list", None)
        st.rerun()

# ==========================================
# TAB 2: WEEKLY ROSTER BUILDER ENGINE
# ==========================================
with tab_roster:
    st.subheader("🗓️ Generate Individual Shift Assignment")
    
    col_cfg1, col_cfg2, col_cfg3 = st.columns(3)
    with col_cfg1:
        req_morning = st.number_input("Morning Shift Staff Needed", min_value=1, max_value=10, value=2)
    with col_cfg2:
        req_evening = st.number_input("Evening Shift Staff Needed", min_value=1, max_value=10, value=2)
    with col_cfg3:
        req_night = st.number_input("Night Shift Staff Needed", min_value=0, max_value=10, value=1)
        
    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    shift_types = []
    if req_morning > 0: shift_types.append("Morning")
    if req_evening > 0: shift_types.append("Evening")
    if req_night > 0: shift_types.append("Night")

    staff_db = {emp["Name"]: {**emp, "Assigned_Count": 0, "Night_Count": 0, "Weekend_Count": 0} for emp in st.session_state.staff_list}
    
    roster_grid = {day: {s: [] for s in shift_types} for day in days_of_week}
    conflict_logs = []

    np.random.seed(42)

    for day in days_of_week:
        is_weekend = day in ["Saturday", "Sunday"]
        for s_type in shift_types:
            needed = req_morning if s_type == "Morning" else (req_evening if s_type == "Evening" else req_night)
            
            candidates = []
            for name, p in staff_db.items():
                if p["Assigned_Count"] >= p["Max_Days"]:
                    continue
                if day in p["Unavailable_Days"]:
                    continue
                if s_type == "Night" and p["No_Nights"]:
                    continue
                already_working_today = any(name in roster_grid[day][st_item] for st_item in shift_types)
                if already_working_today:
                    continue
                    
                candidates.append(name)
            
            # Prioritize candidates who have worked fewer shifts overall
            candidates.sort(key=lambda x: (staff_db[x]["Assigned_Count"] / staff_db[x]["Max_Days"], np.random.rand()))
            
            assigned = candidates[:needed]
            roster_grid[day][s_type] = assigned
            
            for name in assigned:
                staff_db[name]["Assigned_Count"] += 1
                if s_type == "Night":
                    staff_db[name]["Night_Count"] += 1
                if is_weekend:
                    staff_db[name]["Weekend_Count"] += 1
                    
            if len(assigned) < needed:
                conflict_logs.append(f"⚠️ **{day} ({s_type}):** Shortage! Needed {needed}, but only assigned {len(assigned)} due to constraints.")

    st.markdown("### 📋 Generated Roster Grid")
    
    roster_display = []
    for day in days_of_week:
        row = {"Day": day}
        for s_type in shift_types:
            assigned_names = roster_grid[day][s_type]
            row[s_type] = ", ".join(assigned_names) if assigned_names else "❌ SHORTAGE"
        roster_display.append(row)
        
    df_roster_view = pd.DataFrame(roster_display)
    st.dataframe(df_roster_view, use_container_width=True, hide_index=True)
    
    if conflict_logs:
        st.error("🚨 **Roster Conflicts & Unfilled Shifts Detected:**")
        for log in conflict_logs:
            st.write(log)
    else:
        st.success("✅ **100% Shift Coverage Achieved!** All individual constraints respected without coverage gaps.")

    csv_roster = df_roster_view.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Weekly Schedule (CSV)",
        data=csv_roster,
        file_name="FairShift_Weekly_Roster.csv",
        mime="text/csv"
    )

# ==========================================
# TAB 3: DIAGNOSTICS & FAIRNESS SCORE
# ==========================================
with tab_analytics:
    st.subheader("📊 Individual Workload & Fairness Diagnostics")
    
    df_final_stats = pd.DataFrame(list(staff_db.values()))
    df_final_stats["Workload_%"] = (df_final_stats["Assigned_Count"] / df_final_stats["Max_Days"] * 100).round(1)
    
    # Calculate FSI based on WORKLOAD PERCENTAGE variance instead of simple raw count
    workload_ratios = df_final_stats["Assigned_Count"] / df_final_stats["Max_Days"]
    mean_w = np.mean(workload_ratios)
    std_w = np.std(workload_ratios)
    
    fsi = round((1 - (std_w / mean_w if mean_w > 0 else 0)) * 100, 1) if mean_w > 0 else 100.0
    fsi = max(0.0, min(100.0, fsi))
    
    # Identify Overworked Staff
    overworked = df_final_stats[df_final_stats["Workload_%"] >= 100]["Name"].tolist()
    
    col_m1, col_m2, col_m3 = st.columns(3)
    col_m1.metric("Fairness Score Index (FSI)", f"{fsi}%")
    col_m2.metric("Total Workforce", len(df_final_stats))
    col_m3.metric("Overworked Staff (100% Capacity)", f"{len(overworked)}")
    
    st.markdown("---")
    
    if fsi < 75 or len(overworked) > 0:
        st.warning(f"🟡 **WORKLOAD INEQUALITY ALERT:** {', '.join(overworked)} is working at 100% capacity due to strict availability constraints placed by other team members!")
    
    st.subheader("Individual Shift Load & Capacity Utilization")
    
    # Display table with workload status
    st.dataframe(
        df_final_stats[["Name", "Role", "Max_Days", "Assigned_Count", "Workload_%", "Weekend_Count", "Night_Count"]],
        use_container_width=True,
        hide_index=True
    )