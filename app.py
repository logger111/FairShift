import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="FairShift Simulator", layout="wide", page_icon="⚖️")

st.title("⚖️ FairShift: Fairness & Skill-Aware Scheduling Engine")
st.caption("ავტომატური, სამართლიანი და უსაფრთხო გრაფიკის გენერატორი B2B/Operations-ისთვის")

# --- SIDEBAR ---
st.sidebar.header("⚙️ გუნდის პარამეტრები")
num_employees = st.sidebar.number_input("თანამშრომლების რაოდენობა", min_value=6, max_value=20, value=10)
num_weeks = st.sidebar.slider("სიმულაციის პერიოდი (კვირები)", min_value=1, max_value=4, value=4)

st.sidebar.subheader("🛡️ გამოცდილება & შეზღუდვები")
senior_count = st.sidebar.number_input("Senior (გამოცდილი) კადრები", min_value=2, max_value=5, value=3)
strict_weekend_off = st.sidebar.number_input("მყარი უქმეების (Hard Off) კადრები", min_value=0, max_value=4, value=2)

# --- MONTE CARLO DATA GENERATION ---
@st.cache_data
def generate_team(n_total, n_senior, n_strict):
    team = []
    for i in range(1, n_total + 1):
        emp_id = f"EMP_{i:02d}"
        
        # Skill level
        skill = "Senior" if i <= n_senior else "Junior"
        
        # Constraints
        if i > n_senior and i <= n_senior + n_strict:
            c_type = "Hard_No_Weekend"
        else:
            c_type = "Full_Flexible"
            
        team.append({
            "emp_id": emp_id,
            "name": f"თანამშრომელი #{i}",
            "skill_level": skill,
            "constraint_type": c_type,
            "morning_shifts": 0,
            "mid_shifts": 0,
            "evening_shifts": 0,
            "weekend_shifts": 0,
            "total_hours": 0
        })
    return pd.DataFrame(team)

df_emp = generate_team(num_employees, senior_count, strict_weekend_off)

# --- ENGINE SIMULATION ---
def run_engine(df, weeks):
    df_res = df.copy()
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    
    for w in range(weeks):
        for d in days:
            is_weekend = d in ["Fri", "Sat"]
            
            for idx, row in df_res.iterrows():
                if is_weekend and row["constraint_type"] == "Hard_No_Weekend":
                    continue
                    
                # Rotation logic
                if is_weekend:
                    df_res.at[idx, "weekend_shifts"] += 1
                    
                ev, m, md = row["evening_shifts"], row["morning_shifts"], row["mid_shifts"]
                if ev <= m and ev <= md:
                    df_res.at[idx, "evening_shifts"] += 1
                elif md <= m:
                    df_res.at[idx, "mid_shifts"] += 1
                else:
                    df_res.at[idx, "morning_shifts"] += 1
                    
                df_res.at[idx, "total_hours"] += 8

    # FSI Calculation
    std_dev = np.std(df_res["evening_shifts"])
    mean_val = np.mean(df_res["evening_shifts"])
    fsi_score = max(0, round(100 - (std_dev / (mean_val + 1e-5) * 100), 1))
    
    return df_res, fsi_score

df_sim, fsi = run_engine(df_emp, num_weeks)

# --- DASHBOARD METRICS ---
col1, col2, col3 = st.columns(3)
col1.metric("📊 Fairness Score Index (FSI)", f"{fsi}%", delta="High Equity" if fsi > 80 else "Needs Balance")
col2.metric("👥 სულ პერსონალი", f"{num_employees} კაცი")
col3.metric("⭐ Senior Skill Coverage", f"{senior_count} კადრი (Safe Skill Mix)")

st.markdown("---")
st.subheader("📋 თვის ჭრილში დაბალანსებული გრაფიკი")
st.dataframe(df_sim, use_container_width=True)

st.subheader("📈 ცვლების ბალანსის ვიზუალიზაცია")
st.bar_chart(df_sim.set_index("name")[["morning_shifts", "mid_shifts", "evening_shifts", "weekend_shifts"]])