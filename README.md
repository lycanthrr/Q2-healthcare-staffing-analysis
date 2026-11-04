# Nursing Home Staffing Analysis (Q2 2024)

Analysis of daily nurse staffing at 14,564 U.S. nursing homes using CMS Payroll Based Journal (PBJ) data, plus a Streamlit dashboard to compare facilities and states.

**Tools:** Python, pandas, NumPy, Jupyter Notebook, Streamlit

## Files

| File | What it is |
| --- | --- |
| `nursing_home_staffing.ipynb` | EDA, cleaning, metrics, and analysis |
| `streamlit_app.py` | Interactive dashboard |
| `removed_outliers_log.csv` | The one outlier row removed during cleaning |

## Data

The raw CSV (~220 MB) is too large for GitHub, so it isn't included.

1. Download -|Payroll Based Journal Daily Nurse Staffing, Q2 2024|- from [data.cms.gov](https://data.cms.gov)
2. Save it in this folder as `PBJ_Daily_Nurse_Staffing_Q2_2024.csv`

## How to run

```bash
pip install pandas numpy streamlit jupyter
streamlit run streamlit_app.py
```

## Key metrics

- **HPRD (Hours Per Resident Day)** = total nurse hours ÷ residents
- **Contract ratio** = contract nurse hours ÷ total nurse hours (stand-in for overtime, which PBJ doesn't report)
- Total nurse hours, average resident census, and top facilities by hours


## Key findings

- Typical staffing is about 4 nurse hours per resident per day.
- MO (2.41), TX (2.68), and OK (2.80) have the lowest HPRD; AK (5.41) and OR (4.20) the highest.
- Vermont relies most on contract staff, at 32% of nurse hours.
- More residents means more hours (0.91 correlation), so HPRD is needed for fair comparisons.
- Some facilities report HPRD below 1 (as low as 0.07), most likely under-reporting than real staffing.