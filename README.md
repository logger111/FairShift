# ⚖️ FairShift — Automated & Fair Workforce Scheduling Engine

> An intelligent, constraint-aware workforce scheduling and rotation engine designed for fast-paced retail, Dark Stores, and Shift-based operations.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28%2B-FF4B4B)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 🎯 The Problem

In shift-based environments (like Wolt Market, convenience stores, and retail operations), manual weekly shift scheduling is a major operational headache:
* **Inequity & Friction:** Employees feel unfairness when assigned undesirable shifts (e.g., Friday/Saturday night closures).
* **Complex Constraints:** Balancing student schedules, religious observements (e.g., Shabbat), full-time/part-time limits, and mandatory rest periods takes hours of manual effort.
* **Understaffing Risk:** Inability to dynamically calculate real-time headcount needs leads to operational bottlenecks.

## 💡 The Solution: FairShift Engine

**FairShift** treats scheduling as a **Constraint Satisfaction & Optimization Problem**. Instead of subjective manager choices, it uses an automated **Fair-Share Mathematical Algorithm** to achieve arithmetic equity across the team over a 30-day window (`Variance → 0`).

### Key Features
* 🔒 **Hierarchical Constraint Solver:** Respects Hard Constraints (religious/academic rules) without compromise while optimizing Soft Constraints (employee preferences).
* ⚖️ **Fairness Score Index (FSI):** Real-time mathematical metric calculating equity variance across the workforce.
* 🔄 **Cyclic Shift Equalization:** Automatically balances morning, mid, and evening shifts across flexible staff so no employee suffers consecutive heavy shifts.
* 🏖️ **Holiday & Overtime Split:** Fairly distributes high-pay/overtime shifts among eligible team members.
* 🤖 **1 Free Choice Rule:** Gives workers personal autonomy without disrupting operational coverage.

---

## 📐 Mathematical Model & FSI Score

The system evaluates the fairness of generated schedules using the **Fairness Score Index (FSI)**:

$$\text{FSI} = 100 - \left( \frac{\sigma_{\text{shifts}}}{\mu_{\text{shifts}}} \times 100 \right)$$

* $\sigma$ = Standard deviation of shift distribution among flexible employees.
* $\mu$ = Mean shift allocation.
* **Target:** `FSI > 85%` indicates an arithmetically balanced, conflict-free schedule.

---

## 🛠️ Architecture & Data Schema

The system supports seamless integration with Google Sheets, Airtable, or SQL databases via a 4-tab relational structure:

1. **`Employees`**: Profile data, contract types, and hard constraint rules.
2. **`Shift_Rules`**: Hourly coverage requirements, headcount minimums, and break windows.
3. **`Weekly_Requests`**: Employee submissions for their weekly preferences.
4. **`Generated_Schedule`**: Final balanced schedule output with automated system flags.

---

## 🚀 Quick Start & Interactive Simulator

### 1. Clone the Repository
```bash
git clone [https://github.com/YOUR_USERNAME/FairShift.git](https://github.com/YOUR_USERNAME/FairShift.git)
cd FairShift