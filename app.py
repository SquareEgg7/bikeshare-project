import streamlit as st
import pandas as pd
import plotly.express as px

CITY_DATA = {
    'Chicago': 'chicago.csv',
    'New York City': 'new_york_city.csv',
    'Washington': 'washington.csv'
}

st.title("US Bikeshare Data Explorer")
st.write("Explore bikeshare usage patterns across Chicago, New York City, and Washington DC.")

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
# Popular times of travel
st.subheader("Popular Times of Travel")

if month == "All":
    popular_month = df['Month'].value_counts().index[0]
    st.write(f"**Most Popular Month:** {popular_month}")
else:
    st.write(f"**Month filter active:** {month}")

if day == "All":
    popular_day = df['Day of Week'].value_counts().index[0]
    st.write(f"**Most Popular Day:** {popular_day}")
else:
    st.write(f"**Day filter active:** {day}")

popular_hour = df['Hour'].value_counts().index[0]
hour_label = f"{popular_hour % 12 or 12}{'am' if popular_hour < 12 else 'pm'}"
st.write(f"**Most Popular Hour:** {hour_label}")

# Most popular hour
st.subheader("Most Popular Start Hour")

hour_counts = df['Hour'].value_counts().sort_index().reset_index()
hour_counts.columns = ['Hour', 'Count']
hour_counts['Hour Label'] = hour_counts['Hour'].apply(
    lambda h: f"{h % 12 or 12}{'am' if h < 12 else 'pm'}"
)

fig = px.bar(hour_counts, x='Hour Label', y='Count',
             category_orders={'Hour Label': hour_counts['Hour Label'].tolist()})
fig.update_xaxes(tickangle=-60, title_text="")
fig.update_yaxes(title_text="Rides")
st.plotly_chart(fig)

# Most popular stations
st.subheader("Most Popular Stations")

start_station = df['Start Station'].value_counts().index[0]
end_station = df['End Station'].value_counts().index[0]
most_common_trip = (df['Start Station'] + " → " + df['End Station']).value_counts().index[0]

st.write(f"**Most Popular Start Station:** {start_station}")
st.write(f"**Most Popular End Station:** {end_station}")
st.write(f"**Most Popular Trip:** {most_common_trip}")

# Trip duration
st.subheader("Trip Duration")

total_seconds = df['Trip Duration'].sum()
mean_seconds = df['Trip Duration'].mean()

def format_duration(seconds):
    if seconds < 3600:
        return f"{seconds / 60:.1f} minutes"
    else:
        return f"{seconds / 3600:,.1f} hours"

st.write(f"**Total Travel Time:** {format_duration(total_seconds)}")
st.write(f"**Average Trip Duration:** {format_duration(mean_seconds)}")

# User statistics
st.subheader("User Statistics")

# User types
user_types = df['User Type'].value_counts()
no_user_type = df['User Type'].isnull().sum()
st.markdown("#### User Types")
for user_type, count in user_types.items():
    st.write(f"**{user_type}:** {count:,}")
st.write(f"**Not specified:** {no_user_type:,}")

if 'Gender' in df.columns:
    st.divider()
    st.markdown("#### Gender")
    gender_counts = df['Gender'].value_counts()
    for gender, count in gender_counts.items():
        st.write(f"**{gender}:** {count:,}")
    no_gender = df['Gender'].isnull().sum()
    st.write(f"**Not specified:** {no_gender:,}")
    
    st.divider()
    st.markdown("#### Birth Year")
    st.write(f"**Earliest:** {int(df['Birth Year'].min())}")
    st.write(f"**Most Recent:** {int(df['Birth Year'].max())}")
    st.write(f"**Most Common:** {int(df['Birth Year'].mode()[0])}")
    no_birth_year = df['Birth Year'].isnull().sum()
    st.write(f"**Not specified:** {no_birth_year:,}")
else:
    st.write("*Gender and birth year data not available for Washington.*")

st.divider()
# Raw data at the bottom - optional viewing
with st.expander("View raw data"):
    st.dataframe(df)
