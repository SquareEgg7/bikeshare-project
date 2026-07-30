import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide", page_title="US Bikeshare Data Explorer")

# ── HELPER FUNCTIONS ────────────────────────────────────────────
def trip_label(n):
    return f"{n:,} trip" if n == 1 else f"{n:,} trips"

def format_duration(seconds):
    if seconds < 3600:
        return f"{seconds / 60:.1f} minutes"
    else:
        return f"{seconds / 3600:,.1f} hours"

def sticky_pills(label, options, default, state_key, widget_key, **kwargs):
    """Wraps st.pills so clicking the active pill can't deselect it to None."""
    if state_key not in st.session_state:
        st.session_state[state_key] = default
    if st.session_state.get(widget_key) is None and widget_key in st.session_state:
        st.session_state[widget_key] = st.session_state[state_key]

    selection = st.pills(label, options, default=st.session_state[state_key],
                          key=widget_key, **kwargs)
    if selection is not None:
        st.session_state[state_key] = selection
    else:
        selection = st.session_state[state_key]
    return selection

def render_caveats():
    """Renders the Notes & Caveats expander. Called wherever there's spare space."""
    with st.expander("Notes & Caveats"):
        st.markdown("""
This is a rebuild of the Udacity nd104 capstone project — the dataset and analysis subject were assigned; the dashboard design, UX decisions, and interactive architecture are original.

- Optimized for desktop viewing. Mobile layout reorders content due to Streamlit's column-stacking behavior (known limitation, improvement planned for Streamlit v2.0).
- Pill selectors were used in place of dropdown menus for improved touch accessibility — larger tap targets, all options visible without scrolling.
- Charts show marginal distributions only; no cross-tabulation or causal relationships are implied between variables like month, day, and hour.
""")
        
# ── CONSTANTS ───────────────────────────────────────────────────
CITY_DATA = {
    'Chicago': 'chicago.csv',
    'New York City': 'new_york_city.csv',
    'Washington': 'washington.csv'
}

MONTHS = ["January", "February", "March", "April", "May", "June"]
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
CHART_CONFIG = {'displayModeBar': False}
SECTION_HEADER = '<p style="font-size:11px;font-weight:600;color:#2D7D7B;text-transform:uppercase;letter-spacing:0.08em;border-bottom:1.5px solid #2D7D7B;padding-bottom:4px;margin-top:1.5rem;">{}</p>'

# ── CSS ─────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="css"], p, div, span, label, input {
    font-family: 'DM Sans', sans-serif !important;
}
.stApp { background-color: #FAFAF8; }
[data-testid="stIconMaterial"] { display: none !important; }
[data-testid="stBaseButton-pillsActive"],
button[data-variant="pills"][data-selected="true"],
button[data-variant="pills"][aria-checked="true"] {
    background-color: #C4622D !important;
    border-color: #C4622D !important;
    color: white !important;
}

.stPlotlyChart {
    border-radius: 12px !important;
    overflow: hidden !important;
    background: white !important;
    padding: 8px !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06) !important;
}
[data-testid="stPillsContainer"] {
    background: #E8E4DF !important;
    border-radius: 20px !important;
    padding: 3px !important;
}

[data-testid="stToolbar"] {
    display: none !important;
}

[data-testid="stDecoration"] {
    display: none !important;
}

header[data-testid="stHeader"] {
    display: none !important;
}

.block-container {
    padding-top: 0.0rem !important;
}
</style>
""", unsafe_allow_html=True)

# ── TITLE (with back link tucked above, compact) ─────────────────
title_col, toggle_col = st.columns([3, 1])
with title_col:
    st.markdown(
        "<div style='line-height:1.1;'>"
        "<a href='https://edward-chen.com' style='font-size:0.75rem;color:#888;text-decoration:none;'>&larr; Back to Homepage</a>"
        "<h1 style='font-size:1.9rem;margin-top:-8px;margin-bottom:0;line-height:1.1;'>US Bikeshare Data Explorer</h1>"
        "</div>",
        unsafe_allow_html=True
    )
with toggle_col:
    st.markdown("<div style='padding-top:1.1rem;'>", unsafe_allow_html=True)
    view = sticky_pills("", ["Trips", "Users"], "Trips",
                         "active_view", "view_pills_widget", label_visibility="collapsed")
    st.markdown("</div>", unsafe_allow_html=True)

# ── FILTERS ─────────────────────────────────────────────────────
city = sticky_pills("City", list(CITY_DATA.keys()), "Chicago",
                     "active_city", "city_pills_widget", label_visibility="collapsed")

pill_col1, pill_col2 = st.columns([5, 7])
with pill_col1:
    month = sticky_pills("Month", ["All"] + MONTHS, "All",
                          "active_month", "month_pills_widget", label_visibility="collapsed")
with pill_col2:
    day = sticky_pills("Day", ["All"] + DAYS, "All",
                        "active_day", "day_pills_widget", label_visibility="collapsed")

# ── DATA LOADING & FILTERING ─────────────────────────────────────
df = pd.read_csv(CITY_DATA[city])
df['Start Time'] = pd.to_datetime(df['Start Time'])
df['Month'] = df['Start Time'].dt.month_name()
df['Day of Week'] = df['Start Time'].dt.day_name()
df['Hour'] = df['Start Time'].dt.hour

if month != "All":
    df = df[df['Month'] == month]
if day != "All":
    df = df[df['Day of Week'] == day]

month_label = month if month != "All" else "All Months"
day_label = day + "s" if day != "All" else "All Days"

total_trips = pd.read_csv(CITY_DATA[city]).shape[0]
filtered_trips = len(df)
pct = filtered_trips / total_trips * 100

# ── TRIP ANALYSIS DATA ───────────────────────────────────────────
month_order = ['January', 'February', 'March', 'April', 'May', 'June']
month_counts = df['Month'].value_counts().reindex(month_order).reset_index()
month_counts.columns = ['Month', 'Rides']
popular_month = month_counts.loc[month_counts['Rides'].idxmax(), 'Month']
month_counts['Color'] = month_counts['Month'].apply(lambda x: '#C4622D' if x == popular_month else '#DBA088')

day_counts = df['Day of Week'].value_counts().reindex(DAYS).reset_index()
day_counts.columns = ['Day', 'Rides']
popular_day = day_counts.loc[day_counts['Rides'].idxmax(), 'Day']
day_counts['Color'] = day_counts['Day'].apply(lambda x: '#C4622D' if x == popular_day else '#DBA088')

hour_counts = df['Hour'].value_counts().sort_index().reset_index()
hour_counts.columns = ['Hour', 'Rides']
popular_hour = hour_counts.loc[hour_counts['Rides'].idxmax(), 'Hour']
hour_counts['Hour Label'] = hour_counts['Hour'].apply(lambda h: f"{h % 12 or 12}{'am' if h < 12 else 'pm'}")
hour_counts['Color'] = hour_counts['Hour'].apply(lambda x: '#C4622D' if x == popular_hour else '#DBA088')

max_rides = max(month_counts['Rides'].max(), day_counts['Rides'].max(), hour_counts['Rides'].max()) * 1.1

start_station = df['Start Station'].value_counts().index[0]
end_station = df['End Station'].value_counts().index[0]
trip_start = df.groupby(['Start Station', 'End Station']).size().idxmax()[0]
trip_end = df.groupby(['Start Station', 'End Station']).size().idxmax()[1]

total_seconds = df['Trip Duration'].sum()
mean_seconds = df['Trip Duration'].mean()

 #Trip Stats
st.markdown(f"<p style='font-size:0.85rem;color:#888;margin-top:-10px;margin-bottom:-10px;'><strong>{filtered_trips:,}</strong> trips ({pct:.1f}% of {city} dataset)</p>", unsafe_allow_html=True)

# ── VIEWS ────────────────────────────────────────────────────────
if view == "Trips":
    col1, col2, col3 = st.columns(3)

    with col1:
        #Most popular month
        st.markdown(SECTION_HEADER.format("Most Popular Month (by Trips)"), unsafe_allow_html=True)
        fig_month = px.bar(month_counts, x='Month', y='Rides', color='Color',
                           color_discrete_map='identity', category_orders={'Month': month_order})
        fig_month.update_xaxes(tickangle=-60, title_text="", automargin=False)
        fig_month.update_yaxes(title_text="", range=[0, max_rides])
        fig_month.update_layout(height=250, yaxis=dict(range=[0, max_rides], domain=[0.15, 1.0]), showlegend=False, plot_bgcolor='rgba(0,0,0,0)',
                                paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=10, r=10, t=10, b=80),
                                font=dict(family='DM Sans'))
        fig_month.update_traces(hovertemplate='%{x}<br>%{y:,} trips<extra></extra>')
        st.plotly_chart(fig_month, use_container_width=True, config=CHART_CONFIG)

        # Most popular stations
        st.markdown(SECTION_HEADER.format("Most Popular Stations"), unsafe_allow_html=True)
        st.markdown("**Most Popular Start Station:**")
        st.markdown(f"<p style='margin-top:-20px;color:#555;'>{start_station}</p>", unsafe_allow_html=True)
        st.markdown("**Most Popular End Station:**")
        st.markdown(f"<p style='margin-top:-20px;color:#555;'>{end_station}</p>", unsafe_allow_html=True)
        st.markdown("**Most Popular Trip:**")
        st.markdown(f"<p style='margin-top:-20px;color:#555;'>{trip_start}</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='margin-top:-20px;color:#555;font-style:italic;'>to:</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='margin-top:-20px;color:#555;'>{trip_end}</p>", unsafe_allow_html=True)

    with col2:
        # Most popular day
        st.markdown(SECTION_HEADER.format("Most Popular Day of Week (by Trips)"), unsafe_allow_html=True)
        fig_day = px.bar(day_counts, x='Day', y='Rides', color='Color',
                         color_discrete_map='identity', category_orders={'Day': DAYS})
        fig_day.update_xaxes(tickangle=-60, title_text="", automargin=False)
        fig_day.update_yaxes(title_text="", range=[0, max_rides])
        fig_day.update_layout(height=250, yaxis=dict(range=[0, max_rides], domain=[0.15, 1.0]), showlegend=False, plot_bgcolor='rgba(0,0,0,0)',
                              paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=10, r=10, t=10, b=80),
                              font=dict(family='DM Sans'))
        fig_day.update_traces(hovertemplate='%{x}<br>%{y:,} trips<extra></extra>')
        st.plotly_chart(fig_day, use_container_width=True, config=CHART_CONFIG)

        # Trip duration
        st.markdown(SECTION_HEADER.format("Trip Duration"), unsafe_allow_html=True)
        st.markdown("**Total Travel Time:**")
        st.markdown(f"<p style='margin-top:-20px;color:#555;'>{format_duration(total_seconds)}</p>", unsafe_allow_html=True)
        st.markdown("**Average Trip Duration:**")
        st.markdown(f"<p style='margin-top:-20px;color:#555;'>{format_duration(mean_seconds)}</p>", unsafe_allow_html=True)


    with col3:
        # Most popular hour
        st.markdown(SECTION_HEADER.format("Most Popular Hour (by Trips)"), unsafe_allow_html=True)
        fig_hour = px.bar(hour_counts, x='Hour Label', y='Rides', color='Color',
                          color_discrete_map='identity',
                          category_orders={'Hour Label': hour_counts['Hour Label'].tolist()})
        fig_hour.update_xaxes(tickangle=-60, title_text="", dtick=2, automargin=False)
        fig_hour.update_yaxes(title_text="", range=[0, max_rides])
        fig_hour.update_layout(height=250, yaxis=dict(range=[0, max_rides], domain=[0.15, 1.0]), showlegend=False, plot_bgcolor='rgba(0,0,0,0)',
                               paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=10, r=10, t=10, b=80),
                               font=dict(family='DM Sans'))
        fig_hour.update_traces(hovertemplate='%{x}<br>%{y:,} trips<extra></extra>')
        st.plotly_chart(fig_hour, use_container_width=True, config=CHART_CONFIG)
        st.markdown("<div style='padding-top:2.9rem;'>", unsafe_allow_html=True)
        render_caveats()
        st.markdown("</div>", unsafe_allow_html=True)

elif view == "Users":
    
    # User Types pie chart
    user_type_data = df['User Type'].fillna('Not Specified').value_counts().reset_index()
    user_type_data.columns = ['User Type', 'Trips']
    user_type_data['Label'] = user_type_data.apply(lambda row: f"{row['User Type']} — {trip_label(row['Trips'])}", axis=1)

    fig_user = px.pie(user_type_data, values='Trips', names='Label',
                      color_discrete_sequence=['#C4622D', '#DBA088', '#E8C4B0'])
    fig_user.update_layout(height=250,
                           showlegend=True,
                           legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5, entrywidth=300),
                           plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                           margin=dict(l=10, r=10, t=10, b=10), font=dict(family='DM Sans'))
    fig_user.update_traces(textposition='inside', texttemplate='%{percent:.1%}',
                           hovertemplate='%{label}<br>%{value:,} trips<br>%{percent:.1%}<extra></extra>')

    has_gender = 'Gender' in df.columns
    has_birth_year = 'Birth Year' in df.columns

    # User Type + Gender pie charts
    if has_gender:
        gender_order = ['Male', 'Female', 'Not Specified']
        gender_data = df['Gender'].fillna('Not Specified').value_counts().reindex(gender_order).reset_index()
        gender_data.columns = ['Gender', 'Trips']
        gender_data['Label'] = gender_data.apply(lambda row: f"{row['Gender']} — {trip_label(row['Trips'])}", axis=1)

        fig_gender = px.pie(gender_data, values='Trips', names='Label',
                            color_discrete_sequence=['#C4622D', '#DBA088', '#E8C4B0'])
        fig_gender.update_layout(height=250,
                                 showlegend=True,
                                 legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5, entrywidth=300),
                                 plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                                 margin=dict(l=10, r=10, t=10, b=10), font=dict(family='DM Sans'))
        fig_gender.update_traces(textposition='inside', texttemplate='%{percent:.1%}',
                                 hovertemplate='%{label}<br>%{value:,} trips<br>%{percent:.1%}<extra></extra>')

        pie_col1, pie_col2 = st.columns(2)
        with pie_col1:
            st.markdown(SECTION_HEADER.format("User Types"), unsafe_allow_html=True)
            st.plotly_chart(fig_user, use_container_width=True, config=CHART_CONFIG)
        with pie_col2:
            st.markdown(SECTION_HEADER.format("Gender"), unsafe_allow_html=True)
            st.plotly_chart(fig_gender, use_container_width=True, config=CHART_CONFIG)
    else:
        st.markdown(SECTION_HEADER.format("User Types"), unsafe_allow_html=True)
        st.plotly_chart(fig_user, use_container_width=True, config=CHART_CONFIG)

    # Birth year chart
    if has_birth_year:
        birth_col1, birth_col2 = st.columns(2)
        with birth_col1:
            st.markdown(SECTION_HEADER.format("Birth Year (By Trips)"), unsafe_allow_html=True)
            earliest = int(df['Birth Year'].min())
            most_recent = int(df['Birth Year'].max())
            most_common = int(df['Birth Year'].mode()[0])
            no_birth_year = df['Birth Year'].isnull().sum()

            birth_counts = df['Birth Year'].dropna().astype(int).value_counts().sort_index().reset_index()
            birth_counts.columns = ['Year', 'Rides']
            birth_counts['Color'] = birth_counts['Year'].apply(lambda x: '#C4622D' if x == most_common else '#DBA088')

            fig_birth = px.bar(birth_counts, x='Year', y='Rides', color='Color', color_discrete_map='identity')
            fig_birth.update_xaxes(tickangle=-60, title_text="")
            fig_birth.update_yaxes(title_text="", range=[0, birth_counts['Rides'].max() * 1.2])
            fig_birth.update_layout(height=200, showlegend=False, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                                    margin=dict(l=10, r=10, t=30, b=10), font=dict(family='DM Sans'))
            fig_birth.update_traces(hovertemplate='%{x}<br>%{y:,} trips<extra></extra>')
            most_common_count = birth_counts.loc[birth_counts['Year'] == most_common, 'Rides'].values[0]
            fig_birth.add_annotation(
                x=0.0, y=-0.75,
                xref='paper', yref='paper',
                text=f"Earliest: {earliest}  ·  Most Recent: {most_recent}  ·  Not specified: {no_birth_year:,} trips",
                showarrow=False,
                xanchor='left', yanchor='top',
                font=dict(size=10, color='#888', family='DM Sans'),
                align='left'
            )
            fig_birth.add_annotation(x=most_common, y=most_common_count, text=str(most_common),
                                     showarrow=False, yanchor='bottom', yshift=8,
                                     font=dict(size=10, color='#C4622D', family='DM Sans'))
            st.plotly_chart(fig_birth, config=CHART_CONFIG)
        with birth_col2:
            st.markdown("<div style='padding-top:2.9rem;'>", unsafe_allow_html=True)
            render_caveats()
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown("<p style='color:#888;font-style:italic;'>Gender and birth year data not available for this city.</p>", unsafe_allow_html=True)
        render_caveats()