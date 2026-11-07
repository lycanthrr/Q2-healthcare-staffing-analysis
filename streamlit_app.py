import streamlit as st
import pandas as pd
import plotly.express as px

st.title("Nursing Home Staffing Dashboard — Q2 2024")

@st.cache_data
def load_data():
    df = pd.read_csv(
        'PBJ_Daily_Nurse_Staffing_Q2_2024.csv',
        encoding='latin1',
        dtype={'PROVNUM': str}
    )
    df['WorkDate'] = pd.to_datetime(df['WorkDate'], format='%Y%m%d')
    df['total_nurse_hours'] = df['Hrs_RN'] + df['Hrs_LPN'] + df['Hrs_CNA']
    df['ctr_staff_hours'] = df['Hrs_RN_ctr'] + df['Hrs_LPN_ctr'] + df['Hrs_CNA_ctr']
    df['MONTH'] = df['WorkDate'].dt.month

    # remove the known outlier by exact facility + date (not max(),
    # which could delete a valid row if the data changes)
    outlier_mask = (df['PROVNUM'] == '145446') & (df['WorkDate'] == '2024-05-25')
    df = df[~outlier_mask]

    # same cleaning as the notebook (0 residents or 0 nurse hours)
    df = df[(df['MDScensus'] > 0) & (df['total_nurse_hours'] > 0)]

    return df

df = load_data()

hprd_by_state = df.groupby('STATE')[['total_nurse_hours', 'MDScensus']].sum().reset_index()
hprd_by_state['nurse_hprd'] = hprd_by_state['total_nurse_hours'] / hprd_by_state['MDScensus']

fig = px.choropleth(
    hprd_by_state,
    locations='STATE',
    locationmode='USA-states',
    color='nurse_hprd',
    scope='usa',
    title='Nurse Hours per Resident Day by State',
    labels={'nurse_hprd': 'HPRD'}
)

st.plotly_chart(fig, config={'scrollZoom': False})

# naming (hospital -> facility)
total_nurse_hours_facility = df.groupby(['PROVNUM', 'STATE', 'MONTH'])['total_nurse_hours'].sum().reset_index()

st.header("Total Nurse Hours by Facility")

st.subheader("All Facilities, All States")
st.dataframe(total_nurse_hours_facility)
# removed the all-facilities bar chart (~43K bars, slow and unreadable)

st.subheader("Filter by State")
selected_state = st.selectbox("Select State", options=sorted(df['STATE'].unique()))
filtered = total_nurse_hours_facility[total_nurse_hours_facility['STATE'] == selected_state]

st.subheader("Filter by Specific Facility(s)")
available_facilities = sorted(filtered['PROVNUM'].unique())
selected_facilities = st.multiselect(
    "Select specific facilities (leave blank to show all)",
    options=available_facilities
)

if selected_facilities:
    facility_filtered = filtered[filtered['PROVNUM'].isin(selected_facilities)]
else:
    facility_filtered = filtered

chart_df = facility_filtered.copy()
chart_df['MONTH'] = chart_df['MONTH'].map({4: '4-Apr', 5: '5-May', 6: '6-Jun'})
st.bar_chart(chart_df, x='PROVNUM', y='total_nurse_hours', color='MONTH')

# ranks whole facilities for the quarter (old version ranked facility-MONTH rows,
# so one facility could fill up to 3 spots and its months stacked into one bar)
st.subheader("Top Facilities by Nurse Hours (Q2 total)")
top_n = st.slider("Number of facilities to show", 5, 50, 20)

state_df = df[df['STATE'] == selected_state]
facility_totals = state_df.groupby(['PROVNUM', 'PROVNAME'])['total_nurse_hours'].sum().reset_index()
facility_totals['facility'] = facility_totals['PROVNAME'] + ' (' + facility_totals['PROVNUM'] + ')'
top = facility_totals.set_index('facility')['total_nurse_hours'].sort_values(ascending=False).head(top_n)

fig_top = px.bar(top.reset_index(), x='total_nurse_hours', y='facility', orientation='h')
fig_top.update_layout(yaxis={'categoryorder': 'total ascending'})
st.plotly_chart(fig_top)
st.dataframe(top)

st.subheader("Distribution of Monthly Nurse Hours")
dist = facility_filtered['total_nurse_hours'].value_counts(bins=20).sort_index()
dist.index = dist.index.left.round(0)   # use the start of each range as the label
st.bar_chart(dist)

# Shortages: lowest staffing per resident in the selected state
st.subheader("Facilities with Lowest Staffing per Resident")
fac = state_df.groupby(['PROVNUM', 'PROVNAME'])[['total_nurse_hours', 'MDScensus']].sum().reset_index()
fac['HPRD'] = fac['total_nurse_hours'] / fac['MDScensus']
fac['facility'] = fac['PROVNAME'] + ' (' + fac['PROVNUM'] + ')'
st.dataframe(fac.sort_values('HPRD').head(10)[['facility', 'HPRD']], hide_index=True)
st.caption("Very low HPRD (under ~1) is more likely under-reporting than real staffing.")

# Staffing vs. patient load
st.subheader("Staffing vs. Patient Load")
daily = state_df.groupby(['PROVNUM', 'PROVNAME'])[['total_nurse_hours', 'MDScensus']].mean().reset_index()
fig_sc = px.scatter(daily, x='MDScensus', y='total_nurse_hours', hover_name='PROVNAME',
                    trendline='ols',
                    labels={'MDScensus': 'Avg residents per day', 'total_nurse_hours': 'Avg nurse hours per day'})
st.plotly_chart(fig_sc)

# Contract reliance (closest stand-in for overtime)
st.subheader("Contract Staff Reliance by State (Top 15)")
ctr = df.groupby('STATE')[['ctr_staff_hours', 'total_nurse_hours']].sum().reset_index()
ctr['contract_ratio'] = ctr['ctr_staff_hours'] / ctr['total_nurse_hours']
fig_ctr = px.bar(ctr.sort_values('contract_ratio', ascending=False).head(15), x='STATE', y='contract_ratio',
                 labels={'contract_ratio': 'Share of nurse hours from contract staff'})
fig_ctr.update_layout(yaxis_tickformat='.0%')
st.plotly_chart(fig_ctr)