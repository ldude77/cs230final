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
import streamlit as sl
import pandas as pd
import matplotlib.pyplot as mp
import pydeck as dk

# [FUNC2P] Function with two parameters, one with a default value
def load_data(file_path, nrows=None):
    """
    Loads data from a CSV file, cleans it, and maps acronyms to full names.
    """
    # Read the CSV file
    df = pd.read_csv(file_path, nrows=nrows)

    # Convert 'Open Date' to datetime objects
    df['Open Date'] = pd.to_datetime(df['Open Date'])

    # [COLUMNS] Add a new column for the Year
    df['Year'] = df['Open Date'].dt.year

    # Rename columns for PyDeck (it needs 'lat' and 'lon' specifically)
    df = df.rename(columns={'Latitude': 'lat', 'Longitude': 'lon'})

    # [DICTMETHOD] Create a dictionary to map acronyms to full names
    fuel_map = {
        "ELEC": "Electric",
        "LPG": "Propane",
        "BD": "Biodiesel",
        "CNG": "Compressed Natural Gas",
        "E85": "Ethanol (E85)",
        "HY": "Hydrogen",
        "LNG": "Liquefied Natural Gas"
    }

    # Replace the acronyms in the dataframe with full names
    df['Fuel Type Code'] = df['Fuel Type Code'].replace(fuel_map)

    return df

# [FUNCRETURN2] Function that returns two values (most common fuel & count)
def get_fuel_stats(data):
    """
    Calculates the most common fuel type and its count from the provided dataframe.
    """
    counts = {}

    # [ITERLOOP] Iterate through the fuel types in the dataframe
    for fuel in data['Fuel Type Code']:
        # [DICTMETHOD] Use .get() to count occurrences
        counts[fuel] = counts.get(fuel, 0) + 1

    # Find the most common fuel type
    if counts:
        # [DICTMETHOD] Use .items() to find max
        # [LAMBDA] Lambda function to find the key with the highest value
        most_common = max(counts.items(), key=lambda x: x[1])
        return most_common[0], most_common[1]
    return "None", 0

def main():
    # Load data none local for deployment
    # Note: Ensure this path is correct for your specific machine
    try:
        df = load_data("alt_fuel_stations.csv")
    except FileNotFoundError:
        sl.error("File not found. Please check the file path in the code.")
        return

    # Page Title
    sl.title("MA Alternative Fuel Stations Explorer")

    # ---------------------------------------------------------
    # SIDEBAR FILTERS
    # ---------------------------------------------------------
    sl.sidebar.header("Filter Options")

    # [LISTCOMP] List comprehension to get sorted fuel types
    fuel_types = sorted([fuel for fuel in df['Fuel Type Code'].unique()])

    # [ST1] Streamlit widget: Multiselect
    selected_fuels = sl.sidebar.multiselect(
        "Select Fuel Types to Map:",
        options=fuel_types,
        default=fuel_types
    )

    # [ST4] Streamlit widget: Text Input (Search Box)
    town_search = sl.sidebar.text_input("Search by Town (e.g. Boston):")

    # [ST3] Streamlit widget: Radio Button
    top_n = sl.sidebar.radio("Select Top N Cities for Bar Chart:", [5, 10, 15, 20])

    # Year Range Filter
    min_year = int(df['Year'].min())
    max_year = int(df['Year'].max())

    # [ST2] Streamlit widget: Slider
    year_range = sl.sidebar.slider(
        "Select Year Range for Timeline:",
        min_value=min_year,
        max_value=max_year,
        value=(2010, max_year)
    )

    # ---------------------------------------------------------
    # VISUALIZATION 1: PYDECK MAP (Green Dots & Tooltip)
    # ---------------------------------------------------------
    sl.header(f"1. Station Locations")

    # [FILTER1] & [FILTER2] Filter data by Fuel Type AND Town Search
    # Start with all data
    map_data = df

    # 1. Apply Fuel Filter
    if selected_fuels:
        map_data = map_data[map_data['Fuel Type Code'].isin(selected_fuels)]

    # 2. Apply Town Search Filter
    if town_search:
        # Use str.contains for partial, case-insensitive matching
        map_data = map_data[map_data['City'].str.contains(town_search, case=False, na=False)]

    sl.write(f"Showing {len(map_data)} stations based on filters.")

    # Calculate stats for the filtered data using our custom function
    common_fuel, count = get_fuel_stats(map_data)
    sl.info(f"**Quick Stat:** The most common fuel type in this selection is **{common_fuel}** with **{count}** stations.")

    # [MAP] Detailed PyDeck Map
    # Prevent crash if data is empty
    if not map_data.empty:
        mid_lat = map_data['lat'].mean()
        mid_lon = map_data['lon'].mean()
    else:
        mid_lat = 42.4072
        mid_lon = -71.3824

    view_state = dk.ViewState(
        latitude=mid_lat,
        longitude=mid_lon,
        zoom=9,
        pitch=0
    )

    layer = dk.Layer(
        "ScatterplotLayer",
        data=map_data,
        get_position='[lon, lat]',
        get_color='[0, 255, 0, 200]',
        get_radius=500,
        pickable=True
    )

    tool_tip = {
        "html": "<b>Town:</b> {City}<br/><b>Type:</b> {Fuel Type Code}",
        "style": {"backgroundColor": "steelblue", "color": "white"}
    }

    sl.pydeck_chart(dk.Deck(
        map_style=None,
        initial_view_state=view_state,
        layers=[layer],
        tooltip=tool_tip
    ))

    # ---------------------------------------------------------
    # VISUALIZATION 2: BAR CHART (Top Cities)
    # ---------------------------------------------------------
    sl.header(f"2. Top {top_n} Cities with Most Stations")

    city_counts = df['City'].value_counts().reset_index()
    city_counts.columns = ['City', 'Count']

    # [SORT] Sort data
    city_counts = city_counts.sort_values(by='Count', ascending=False)
    top_cities = city_counts.head(top_n)

    # [CHART1] Bar Chart using Matplotlib (mp)
    fig, ax = mp.subplots()
    ax.bar(top_cities['City'], top_cities['Count'], color='green')
    mp.xticks(rotation=45, ha='right')
    ax.set_ylabel("Number of Stations")
    ax.set_title(f"Top {top_n} Cities")
    sl.pyplot(fig)

    # ---------------------------------------------------------
    # VISUALIZATION 3: LINE CHART (Openings Over Time)
    # ---------------------------------------------------------
    sl.header("3. Station Openings Over Time")

    # [FILTER2] Filter data by year range
    timeline_data = df[(df['Year'] >= year_range[0]) & (df['Year'] <= year_range[1])]
    stations_by_year = timeline_data.groupby('Year').size()

    # [CHART2] Line Chart using Matplotlib (Switched to allow Green Color)
    fig2, ax2 = mp.subplots()
    ax2.plot(stations_by_year.index, stations_by_year.values, color='green', marker='o')
    ax2.set_xlabel("Year")
    ax2.set_ylabel("Count")
    ax2.set_title("Stations Opened by Year")
    ax2.grid(True, linestyle='--', alpha=0.5)

    sl.pyplot(fig2)

    if sl.checkbox("Show Filtered Data for Timeline"):
        sl.write(timeline_data)

# Run the main function
if __name__ == "__main__":
    main()

