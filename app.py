import streamlit as st
import pandas as pd
import plotly.express as px

# Global CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="css"], p, div, span, label, input {
    font-family: 'DM Sans', sans-serif !important;
}

.stApp {
    background-color: #FAFAF8;
}

h1 {
    font-family: 'DM Sans', sans-serif;
    font-weight: 600;
    color: #2C3A2E;
    letter-spacing: -0.3px;
}

h2, h3 {
    font-family: 'DM Sans', sans-serif;
    font-weight: 500;
    color: #2C3A2E;
}

[data-testid="stIconMaterial"] {
    display: none !important;
}

[data-testid="stExpander"] [data-testid="stMarkdownContainer"] {
    text-align: left !important;
    padding-left: 0 !important;
}

</style>
""", unsafe_allow_html=True)

CITY_DATA = {
    'Chicago': 'chicago.csv',
    'New York City': 'new_york_city.csv',
    'Washington': 'washington.csv'
}

st.title("US Bikeshare Data Explorer")
st.write("Explore bikeshare usage patterns across Chicago, New York City, or Washington DC.")

# Filters
col1, col2, col3 = st.columns(3)

with col1:
    city = st.selectbox("Select a city:", list(CITY_DATA.keys()))

with col2:
    month = st.selectbox("Select a month:", 
        ["All", "January", "February", "March", "April", "May", "June"])

with col3:
    day = st.selectbox("Select a day:", 
        ["All", "Monday", "Tuesday", "Wednesday", 
         "Thursday", "Friday", "Saturday", "Sunday"])

# Load data
df = pd.read_csv(CITY_DATA[city])
df['Start Time'] = pd.to_datetime(df['Start Time'])
df['Month'] = df['Start Time'].dt.month_name()
df['Day of Week'] = df['Start Time'].dt.day_name()
df['Hour'] = df['Start Time'].dt.hour

# Apply filters
if month != "All":
    df = df[df['Month'] == month]
if day != "All":
    df = df[df['Day of Week'] == day]

# Summary line
total_trips = pd.read_csv(CITY_DATA[city]).shape[0]
filtered_trips = len(df)
pct = filtered_trips / total_trips * 100

month_label = month if month != "All" else "All Months"
day_label = day + "s" if day != "All" else "All Days"

st.write(f"Showing **{filtered_trips:,}** trips for **{city}** — {month_label}, {day_label} — representing **{pct:.1f}%** of the {total_trips:,} total trips in the {city} dataset.")

# Build all three dataframes:
month_order = ['January', 'February', 'March', 'April', 'May', 'June']
month_counts = df['Month'].value_counts().reindex(month_order).reset_index()
month_counts.columns = ['Month', 'Rides']
popular_month = month_counts.loc[month_counts['Rides'].idxmax(), 'Month']
month_counts['Color'] = month_counts['Month'].apply(
    lambda x: '#C4622D' if x == popular_month else '#DBA088')

day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
day_counts = df['Day of Week'].value_counts().reindex(day_order).reset_index()
day_counts.columns = ['Day', 'Rides']
popular_day = day_counts.loc[day_counts['Rides'].idxmax(), 'Day']
day_counts['Color'] = day_counts['Day'].apply(
    lambda x: '#C4622D' if x == popular_day else '#DBA088')

hour_counts = df['Hour'].value_counts().sort_index().reset_index()
hour_counts.columns = ['Hour', 'Rides']
popular_hour = hour_counts.loc[hour_counts['Rides'].idxmax(), 'Hour']
hour_counts['Hour Label'] = hour_counts['Hour'].apply(
    lambda h: f"{h % 12 or 12}{'am' if h < 12 else 'pm'}"
)
hour_counts['Color'] = hour_counts['Hour'].apply(
    lambda x: '#C4622D' if x == popular_hour else '#DBA088'
)

# Shared y-axis Max
max_rides = max(
    month_counts['Rides'].max(),
    day_counts['Rides'].max(),
    hour_counts['Rides'].max()
) * 1.1  # 10% headroom above the tallest bar

# Draw 3 charts

# # Month distribution
st.markdown('<p style="font-size:11px;font-weight:600;color:#2D7D7B;text-transform:uppercase;letter-spacing:0.08em;border-bottom:1.5px solid #2D7D7B;padding-bottom:4px;margin-top:1.5rem;">Most Popular Month (by Trips)</p>', unsafe_allow_html=True)

fig_month = px.bar(month_counts, x='Month', y='Rides',
                   color='Color', color_discrete_map='identity')
fig_month.update_xaxes(tickangle=-60, title_text="")
fig_month.update_yaxes(title_text="", range=[0, max_rides])
fig_month.update_layout(width=600,
                        showlegend=False, 
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        margin=dict(l=10, r=10, t=10, b=10),
                        font=dict(family='DM Sans')
                        )
fig_month.update_traces(hovertemplate='%{x}<br>%{y:,} trips<extra></extra>')
st.plotly_chart(fig_month)
st.caption("Note: Dataset covers January–June 2017 only.")

# Day Distribution
st.markdown('<p style="font-size:11px;font-weight:600;color:#2D7D7B;text-transform:uppercase;letter-spacing:0.08em;border-bottom:1.5px solid #2D7D7B;padding-bottom:4px;margin-top:1.5rem;">Most Popular Day of Week (by Trips)</p>', unsafe_allow_html=True)

fig_day = px.bar(day_counts, x='Day', y='Rides',
                 color='Color', color_discrete_map='identity', category_orders={'Day': day_order})
fig_day.update_xaxes(tickangle=-60, title_text="")
fig_day.update_yaxes(title_text="", range=[0, max_rides])
fig_day.update_layout(showlegend=False,
                      plot_bgcolor='rgba(0,0,0,0)',
                      paper_bgcolor='rgba(0,0,0,0)',
                      margin=dict(l=10, r=10, t=10, b=10),
                      font=dict(family='DM Sans')
                      )
fig_day.update_traces(hovertemplate='%{x}<br>%{y:,} trips<extra></extra>')
st.plotly_chart(fig_day)

# Hour Distribution
st.markdown('<p style="font-size:11px;font-weight:600;color:#2D7D7B;text-transform:uppercase;letter-spacing:0.08em;border-bottom:1.5px solid #2D7D7B;padding-bottom:4px;margin-top:1.5rem;">Most popular hour (by Trips)</p>', unsafe_allow_html=True)

fig_hour = px.bar(hour_counts, x='Hour Label', y='Rides',
             color='Color',
             color_discrete_map='identity',
             category_orders={'Hour Label': hour_counts['Hour Label'].tolist()})
fig_hour.update_xaxes(tickangle=-60, title_text="")
fig_hour.update_yaxes(title_text="", range=[0, max_rides])
fig_hour.update_layout(showlegend=False,
                  plot_bgcolor='rgba(0,0,0,0)',
                  paper_bgcolor='rgba(0,0,0,0)',
                  margin=dict(l=10, r=10, t=10, b=10),
                  font=dict(family='DM Sans')
                  )
fig_hour.update_traces(hovertemplate='%{x}<br>%{y:,} trips<extra></extra>')
st.plotly_chart(fig_hour)

# Most popular stations
st.markdown('<p style="font-size:11px;font-weight:600;color:#2D7D7B;text-transform:uppercase;letter-spacing:0.08em;border-bottom:1.5px solid #2D7D7B;padding-bottom:4px;margin-top:1.5rem;">Most popular stations</p>', unsafe_allow_html=True)

start_station = df['Start Station'].value_counts().index[0]
end_station = df['End Station'].value_counts().index[0]
most_common_trip = (df['Start Station'] + " → " + df['End Station']).value_counts().index[0]

st.markdown("**Most Popular Start Station:**")
st.markdown(f"<p style='margin-top:-20px;color:#555;'>{start_station}</p>", unsafe_allow_html=True)

st.markdown("**Most Popular End Station:**")
st.markdown(f"<p style='margin-top:-20px;color:#555;'>{end_station}</p>", unsafe_allow_html=True)

trip_start = df.groupby(['Start Station', 'End Station']).size().idxmax()[0]
trip_end = df.groupby(['Start Station', 'End Station']).size().idxmax()[1]
st.markdown("**Most Popular Trip:**")
st.markdown(f"<p style='margin-top:-20px;color:#555;'>{trip_start}</p>", unsafe_allow_html=True)
st.markdown(f"<p style='margin-top:-20px;color:#555;font-style:italic;'>to:</p>", unsafe_allow_html=True)
st.markdown(f"<p style='margin-top:-20px;color:#555;'>{trip_end}</p>", unsafe_allow_html=True)

# Trip Duration
st.markdown('<p style="font-size:11px;font-weight:600;color:#2D7D7B;text-transform:uppercase;letter-spacing:0.08em;border-bottom:1.5px solid #2D7D7B;padding-bottom:4px;margin-top:1.5rem;">Trip Duration</p>', unsafe_allow_html=True)

total_seconds = df['Trip Duration'].sum()
mean_seconds = df['Trip Duration'].mean()

def format_duration(seconds):
    if seconds < 3600:
        return f"{seconds / 60:.1f} minutes"
    else:
        return f"{seconds / 3600:,.1f} hours"

st.markdown("**Total Travel Time:**")
st.markdown(f"<p style='margin-top:-20px;color:#555;'>{format_duration(total_seconds)}</p>", unsafe_allow_html=True)

st.markdown("**Average Trip Duration:**")
st.markdown(f"<p style='margin-top:-20px;color:#555;'>{format_duration(mean_seconds)}</p>", unsafe_allow_html=True)

# User statistics
st.markdown('<p style="font-size:11px;font-weight:600;color:#2D7D7B;text-transform:uppercase;letter-spacing:0.08em;border-bottom:1.5px solid #2D7D7B;padding-bottom:4px;margin-top:1.5rem;">User statistics</p>', unsafe_allow_html=True)

# User Types pie chart
st.markdown("**User Types**")
user_type_data = df['User Type'].fillna('Not Specified').value_counts().reset_index()
user_type_data.columns = ['User Type', 'Trips']
user_type_data['Label'] = user_type_data.apply(
    lambda row: f"{row['User Type']} - {row['Trips']:,} trips", axis=1)

fig_user = px.pie(user_type_data, values='Trips', names='Label',
                  color_discrete_sequence=['#C4622D', '#DBA088', '#E8C4B0'])
fig_user.update_layout(
    showlegend=True,
    legend=dict(
        orientation='h',
        yanchor='bottom',
        y=1.02,
        xanchor='center',
        x=0.5,
        entrywidth=300
    ),
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    margin=dict(l=10, r=10, t=10, b=10),
    font=dict(family='DM Sans')
)
fig_user.update_traces(
    textposition='inside',
    texttemplate='%{percent:.1%}',
    hovertemplate='%{label}<br>%{percent:.1%}<extra></extra>'
)
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.plotly_chart(fig_user)

# Gender pie chart
if 'Gender' in df.columns:
    st.markdown("**Gender**")
    gender_order = ['Male', 'Female', 'Not Specified']
    gender_data = df['Gender'].fillna('Not Specified').value_counts()
    gender_data = gender_data.reindex(gender_order).reset_index()
    gender_data.columns = ['Gender', 'Trips']
    gender_data['Label'] = gender_data.apply(
        lambda row: f"{row['Gender']} - {row['Trips']:,} trips", axis=1)

    fig_gender = px.pie(gender_data, values='Trips', names='Label',
                        color_discrete_sequence=['#C4622D', '#DBA088', '#E8C4B0'])
    fig_gender.update_layout(
        showlegend=True,
        legend=dict(
                orientation='h',
                yanchor='bottom',
                y=1.02,
                xanchor='center',
                x=0.5,
                entrywidth=300
            ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=10, r=10, t=10, b=10),
        font=dict(family='DM Sans')
    )
    fig_gender.update_traces(
        textposition='inside',
        texttemplate='%{percent:.1%}',
        hovertemplate='%{label}<br>%{percent:.1%}<extra></extra>'
    )
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.plotly_chart(fig_gender)

    # Birth year histogram
    st.markdown("**Birth Year**")
    earliest = int(df['Birth Year'].min())
    most_recent = int(df['Birth Year'].max())
    most_common = int(df['Birth Year'].mode()[0])
    no_birth_year = df['Birth Year'].isnull().sum()

    birth_counts = df['Birth Year'].dropna().astype(int).value_counts().sort_index().reset_index()
    birth_counts.columns = ['Year', 'Rides']
    birth_counts['Color'] = birth_counts['Year'].apply(
        lambda x: '#C4622D' if x == most_common else '#DBA088')

    fig_birth = px.bar(birth_counts, x='Year', y='Rides',
                       color='Color', color_discrete_map='identity')
    fig_birth.update_xaxes(tickangle=-60, title_text="")
    fig_birth.update_yaxes(title_text="", range=[0, birth_counts['Rides'].max() * 1.2])
    fig_birth.update_layout(
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=10, r=10, t=10, b=10),
        font=dict(family='DM Sans')
    )
    fig_birth.update_traces(hovertemplate='%{x}<br>%{y:,} trips<extra></extra>')
    most_common_count = birth_counts.loc[birth_counts['Year'] == most_common, 'Rides'].values[0]
    fig_birth.add_annotation(
        x=most_common,
        y=most_common_count,
        text=str(most_common),
        showarrow=False,
        yanchor='bottom',
        yshift=8,
        font=dict(size=10, color='#C4622D', family='DM Sans')
    )
    st.plotly_chart(fig_birth)

    st.markdown(f"<p style='margin-top:-20px;color:#555;'>Earliest: {earliest}</p>", unsafe_allow_html=True)
    st.markdown(f"<p style='margin-top:-20px;color:#555;'>Most Recent: {most_recent}</p>", unsafe_allow_html=True)
    st.markdown(f"<p style='margin-top:-20px;color:#555;'>Most Common: {most_common}</p>", unsafe_allow_html=True)
    st.markdown(f"<p style='margin-top:-20px;color:#555;'>Not specified: {no_birth_year:,}</p>", unsafe_allow_html=True)

else:
    st.markdown("<p style='color:#888;font-style:italic;'>Gender and birth year data not available for Washington.</p>", unsafe_allow_html=True)

st.divider()
with st.expander("View raw data"):
    st.dataframe(df)