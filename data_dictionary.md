# Data Dictionary — PBJ Daily Nurse Staffing, Q2 2024

**Source:** CMS (Centers for Medicare & Medicaid Services) Payroll Based Journal (PBJ) Daily Nurse Staffing
**Grain:** One row per nursing home per day (Apr 1 – Jun 30, 2024)
**Size:** 1,325,324 raw rows, 33 columns, 14,564 facilities (1,322,064 rows after cleaning)

## Facility and date columns

| Column | Type | Description | Example |
| --- | --- | --- | --- |
| PROVNUM | text | CMS provider number, the unique ID for each facility. Loaded as text to keep leading zeros and letters. | 015009, 26A378 |
| PROVNAME | text | Facility name. Not unique: different facilities can share a name. | BURNS NURSING HOME, INC. |
| CITY | text | City where the facility is located | RUSSELLVILLE |
| STATE | text | Two-letter state code | AL |
| COUNTY_NAME | text | County name | Franklin |
| COUNTY_FIPS | integer | County FIPS code (federal county ID, unique within a state) | 59 |
| CY_Qtr | text | Calendar year and quarter | 2024Q2 |
| WorkDate | date | Day the hours were worked. Stored as a number in the raw file, converted to a date. | 2024-04-01 |
| MDScensus | integer | Number of residents in the facility that day, from MDS (Minimum Data Set) records | 51 |

## Staffing hours columns

Each role has **3 columns**: the total, plus the split between employees and contract staff.

- `Hrs_<role>` = total hours worked that day
- `Hrs_<role>_emp` = hours worked by the facility's own employees
- `Hrs_<role>_ctr` = hours worked by contract (agency) staff

So `Hrs_<role>` = `Hrs_<role>_emp` + `Hrs_<role>_ctr`. All hour columns are decimals.

| Role columns | Role | Used in analysis |
| --- | --- | --- |
| Hrs_RNDON, _emp, _ctr | RN Director of Nursing | No |
| Hrs_RNadmin, _emp, _ctr | RN with administrative duties | No |
| Hrs_RN, _emp, _ctr | Registered Nurse | Yes |
| Hrs_LPNadmin, _emp, _ctr | LPN with administrative duties | No |
| Hrs_LPN, _emp, _ctr | Licensed Practical Nurse | Yes |
| Hrs_CNA, _emp, _ctr | Certified Nursing Assistant | Yes |
| Hrs_NAtrn, _emp, _ctr | Nurse aide in training | No |
| Hrs_MedAide, _emp, _ctr | Medication aide/technician | No |

## Calculated columns (added in this project)

| Column | Type | Formula | Description |
| --- | --- | --- | --- |
| MONTH | integer | Month of WorkDate | 4 = Apr, 5 = May, 6 = Jun |
| total_nurse_hours | decimal | Hrs_RN + Hrs_LPN + Hrs_CNA | Total direct-care nurse hours that day |
| ctr_staff_hours | decimal | Hrs_RN_ctr + Hrs_LPN_ctr + Hrs_CNA_ctr | Nurse hours worked by contract staff |
| nurse_hprd | decimal | total_nurse_hours ÷ MDScensus | Hours Per Resident Day: nursing care hours per resident. Used to compare facilities of different sizes fairly. |
| contract_ratio | decimal | ctr_staff_hours ÷ total_nurse_hours | Share of nurse hours from contract staff (0 to 1). Used as a stand-in for overtime, which PBJ doesn't report. |

## Cleaning notes

| Rows removed | Reason |
| --- | --- |
| 1 | Outlier: 13,801.5 contract LPN hours in one day (PROVNUM 145446, 2024-05-25). Logged in `removed_outliers_log.csv`. |
| 320 | 0 residents that day (HPRD would divide by 0) |
| 2,939 | Residents but 0 nurse hours (likely missing reports) |
