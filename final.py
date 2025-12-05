"""
Name:       Logan Costa
CS230:      Section 3
Data:       alt_fuel_stations.csv
URL:       (get back to this)

Description:    

This program will go through the given CSV file to find important information. Then it will be visualized.
1. will be an interactive map of all the fuel stations
2. a bar chart showing which towns have the most stations
3. A line chart showing how mnay have opened it total as time has continued forward
.
References:
(get back to this)

"""
#base imports to support all the code
import streamlit as sl
import pandas as pd
import matplotlib.pyplot as mp
import pydeck as dk



# [FUNC2P] Function with two parameters, one with a default value
# This function loads the data and performs initial cleaning
def load_data(file_path, nrows=None):
    # Read the CSV file
    df = pd.read_csv(file_path, nrows=nrows)

    # Convert 'Open Date' to datetime objects for time-series analysis
    df['Open Date'] = pd.to_datetime(df['Open Date'])

    # [COLUMNS] Add a new column for just the Year
    df['Year'] = df['Open Date'].dt.year

    # Rename columns for easier mapping
    df = df.rename(columns={'Latitude': 'lat', 'Longitude': 'lon'})

    return df


# Load data
df = load_data(r"C:\Users\logan\OneDrive - Bentley University\python cs230\alt_fuel_stations.csv")

# Page Title
sl.title("MA Alternative Fuel Stations Explorer")

# ---------------------------------------------------------
# SIDEBAR FILTERS
# ---------------------------------------------------------
sl.sidebar.header("Filter Options")

# Query 1: Fuel Type Filter
# [LISTCOMP] List comprehension to get a sorted list of fuel types
fuel_types = sorted([fuel for fuel in df['Fuel Type Code'].unique()])

# [ST1] Streamlit widget: Multiselect
selected_fuels = sl.sidebar.multiselect(
    "Select Fuel Types to Map:",
    options=fuel_types,
    default=fuel_types
)

# Query 2: City Count Filter
# [ST3] Streamlit widget: Radio Button
top_n = sl.sidebar.radio("Select Top N Cities for Bar Chart:", [5, 10, 15, 20])

# Query 3: Year Range Filter
min_year = int(df['Year'].min())
max_year = int(df['Year'].max())

# [ST2] Streamlit widget: Slider (Double-ended)
year_range = sl.sidebar.slider(
    "Select Year Range for Timeline:",
    min_value=min_year,
    max_value=max_year,
    value=(2010, max_year)
)

# ---------------------------------------------------------
# VISUALIZATION 1: MAP (Fuel Type)
# ---------------------------------------------------------
sl.header(f"1. Station Locations")

# [FILTER1] Filter data by Fuel Type
if selected_fuels:
    map_data = df[df['Fuel Type Code'].isin(selected_fuels)]
else:
    map_data = df

sl.write(f"Showing {len(map_data)} stations based on selected fuel types.")

# [MAP] Display Map
sl.map(map_data)

# ---------------------------------------------------------
# VISUALIZATION 2: BAR CHART (Top Cities)
# ---------------------------------------------------------
sl.header(f"2. Top {top_n} Cities with Most Stations")

# Count stations per city
city_counts = df['City'].value_counts().reset_index()
city_counts.columns = ['City', 'Count']

# [SORT] Sort data in descending order
city_counts = city_counts.sort_values(by='Count', ascending=False)

# Slice the dataframe to get only the top N
top_cities = city_counts.head(top_n)

# [CHART1] Bar Chart using Matplotlib
fig, ax = mp.subplots()
ax.bar(top_cities['City'], top_cities['Count'], color='skyblue')
mp.xticks(rotation=45, ha='right')
ax.set_ylabel("Number of Stations")
ax.set_title(f"Top {top_n} Cities")
sl.pyplot(fig)

# ---------------------------------------------------------
# VISUALIZATION 3: LINE CHART (Openings Over Time)
# ---------------------------------------------------------
sl.header("3. Station Openings Over Time")

# [FILTER2] Filter data by two conditions (Year range)
timeline_data = df[(df['Year'] >= year_range[0]) & (df['Year'] <= year_range[1])]

# Group by Year and count
stations_by_year = timeline_data.groupby('Year').size()

# [CHART2] Line Chart
sl.line_chart(stations_by_year)

# Show the filtered data table at the bottom
if sl.checkbox("Show Filtered Data for Timeline"):
    sl.write(timeline_data)

