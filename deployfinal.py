"""
Name:       Logan Costa
CS230:      Section 3
Data:       alt_fuel_stations.csv
URL:       https://cs230final-z2xohczwsckqycsqcjqwgz.streamlit.app/

Description:

This program will go through the given CSV file to find important information. Then it will be visualized.
1. will be an interactive map of all the fuel stations
2. a bar chart showing which towns have the most stations
3. A line chart showing how mnay have opened it total as time has continued forward
.
References:
1. https://medium.com/@ayeshakhan00/what-does-nrows-do-in-python-a7580a8dd7ae (this taught me nrows)
2. https://pandas.pydata.org/docs/reference/api/pandas.to_datetime.html (used to understand datetime in pandas)
3. https://www.datacamp.com/tutorial/python-lambda-functions (this helped me better understand lambda functions)
4. https://docs.streamlit.io/develop/api-reference (provided streamlit help)
5. CS213
6. Google's AI gemini helped me deploy my website through streamlit
7. https://matplotlib.org/ (used to help with the graphs)

"""
import streamlit as sl
import pandas as pd
import matplotlib.pyplot as mp
import pydeck as dk

# [FUNC2P] Function with two parameters, one with a default value
# this function has the parameters of finding the file path which can change. the default is nrows which says how many
# rows to load none guarantees all are read.
def load_data(file_path, nrows=None):
    """
    This function loads data from a CSV file, makes some new columns for use later, and makes the type acronyms full words
    """
    # Read the CSV file
    df = pd.read_csv(file_path, nrows=nrows)

    # Convert 'Open Date' to datetime objects this will be used in making a line graph later
    df['Open Date'] = pd.to_datetime(df['Open Date'])

    # [COLUMNS] Add a new column for the Year then using the .dt(a modifier unlocked when using datetime) we use . year to get the year
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
        counts[fuel] = counts.get(fuel, 0) + 1 #each time we get one it adds it to the total for the type

    # Find the most common fuel type
    if counts:#if the fuel type from before got counted
        # [LAMBDA] Lambda function to find the key with the highest value
        # this makes pairs of all the fuel types and there count then finding the highest value in the count with [1] using max
        most_common = max(counts.items(), key=lambda x: x[1])
        return most_common[0], most_common[1]
    return "None", 0

def main():
    """
    Run the previous functions and make the displays using them
    Having a main function was also part of the requirements
    """

    # Load data none local for deployment
    # Ensure this path is correct for your specific machine when doing mine I had problems getting the file to open on streamlit.
    # This code works for my github cloud
    try:
        df = load_data("alt_fuel_stations.csv")
    except FileNotFoundError:#this is to handle if the csv doesn't load right which happened to me a lot
        sl.error("File not found. Please check the file path in the code.")
        return

    # Page Title
    sl.title("MA Alternative Fuel Stations Explorer")

    # SIDEBAR FILTERS
    sl.sidebar.header("Filter Options")#gives the sidebar a header describing what it does

    # [LISTCOMP] List comprehension to get sorted fuel types
    fuel_types = sorted([fuel for fuel in df['Fuel Type Code'].unique()])#returns an alphabetical list for each type of fuel with no repeats

    # [ST1] Streamlit widget: Multiselect
    selected_fuels = sl.sidebar.multiselect(
        "Select Fuel Types to Map:",
        options=fuel_types,
        default=fuel_types
    )#this will allow the map to be interactive with fuel types

    # [ST3] Streamlit widget: Text Input (Search Box)
    town_search = sl.sidebar.text_input("Search by Town (e.g. Boston):")#also makes the map interactive by allowing a town search

    # [ST3] Streamlit widget: Radio Button
    top_n = sl.sidebar.radio("Select Top N Cities for Bar Chart:", [5, 10, 15, 20])#makes the bar chart interactive by choosing number of things shown

    # Year Range Filter this helps build our slider using the year column we previously made we can set a range for the line graph
    min_year = int(df['Year'].min())
    max_year = int(df['Year'].max())

    # [ST2] Streamlit widget: Slider
    #this takes the variables created above and uses them in the slider. It also sets a default min of 2010 as not much happened until after that,
    # and it's a good even year
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

    #Apply Fuel Filter from the multiselect onto the map
    if selected_fuels:
        map_data = map_data[map_data['Fuel Type Code'].isin(selected_fuels)]

    #Apply Town Search Filter
    if town_search:
        # Use str.contains for partial, case-insensitive matching
        map_data = map_data[map_data['City'].str.contains(town_search, case=False, na=False)]

    sl.write(f"Showing {len(map_data)} stations based on filters.")

    # Calculate stats for the filtered data using our custom function
    common_fuel, count = get_fuel_stats(map_data)
    sl.info(f"**Fun Fact:** The most common fuel type in this selection is **{common_fuel}** with **{count}** stations.") # the stars * make the text bold on the website

    # [MAP] Detailed PyDeck Map
    # Prevent crash if data is empty
    if not map_data.empty:# assuming the data we have works it finds the average latitude and longitude and
        # loads there. This updates when we filter by town
        mid_lat = map_data['lat'].mean()
        mid_lon = map_data['lon'].mean()
    else:#if the data does not work we load this exact location which is around Boston
        mid_lat = 42
        mid_lon = -71

    view_state = dk.ViewState(
        latitude=mid_lat,
        longitude=mid_lon,
        #takes the cordinates calculated in the previous if statement and applies it to the map
        zoom=9,#sets a zoom of 9 when loading
        pitch=0#default for 2d map like mine
    )
#this next section makes the dots (scatterplot) on the map we learned most in class then I pickable = true
    # to make it so they could be selected and do something
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
    }# a friend told me you could use basic HTML in python with streamlit. I took CS213 last semester and
    # used my knowledge from that

    sl.pydeck_chart(dk.Deck(
        map_style=None,
        initial_view_state=view_state,
        layers=[layer],
        tooltip=tool_tip
    ))#this applies the tool tip which states the town and type of station when you hover over them on the map
    # while rendering the whole map

    # VISUALIZATION 2: BAR CHART (Top Cities)
    sl.header(f"2. Top {top_n} Cities with Most Stations")#top_n comes from the radio select in sidebar
#make a new df that has the cities and a count of stations in the city
    city_counts = df['City'].value_counts().reset_index()
    city_counts.columns = ['City', 'Count']

    # [SORT] Sort data this sorts the count from greatest to least
    city_counts = city_counts.sort_values(by='Count', ascending=False)
    top_cities = city_counts.head(top_n)#head loads the top amount of rows from the data in this case the radio buttons decide the amount

    # [CHART1] Bar Chart using Matplotlib
    fig, ax = mp.subplots() # figure is used for streamlit to and ax = subploats allows us to make it all in one line
    ax.bar(top_cities['City'], top_cities['Count'], color='green')#green to go with alternative fuel theme
    mp.xticks(rotation=45, ha='right')#rotate the words 45 degrees right to make them easy to read and not overlap
    ax.set_ylabel("Number of Stations")#rename the y-axis
    ax.set_title(f"Top {top_n} Cities") #reanme the x-axis with top_n from radio
    ax.grid(True, axis="y", linestyle='--', alpha=0.5)#True makes a grid, linestyle has dashes and alpha is the transparency
    sl.pyplot(fig)#let it appear in streamlit

    # VISUALIZATION 3: LINE CHART (Openings Over Time)
    sl.header("3. Station Openings Over Time")

    # [FILTER1] Filter data by year range
    timeline_data = df[(df['Year'] >= year_range[0]) & (df['Year'] <= year_range[1])]#modifies the df to only have years selected by the slider
    stations_by_year = timeline_data.groupby('Year').size()#groups by year to get a total for the year

    # [CHART2] Line Chart using Matplotlib (Switched to allow Green Color)
    fig2, ax2 = mp.subplots()#used in streamlit same as bar chart
    ax2.plot(stations_by_year.index, stations_by_year.values, color='green', marker='o')#make the line chart green and have dots each year
    ax2.set_xlabel("Year")# rename x-axis
    ax2.set_ylabel("Count")#name the y-axis
    ax2.set_title("Stations Opened by Year")#title
    ax2.grid(True, linestyle='--', alpha=0.5)#True makes a grid, linestyle has dashes and alpha is the transparency
    sl.pyplot(fig2)
#[ST3]
    if sl.checkbox("Show Filtered Data for Timeline"):#allows the user to check a box and see a print out of the data frame for the timeline
        sl.write(timeline_data)

# Run the main function
if __name__ == "__main__":
    main()

