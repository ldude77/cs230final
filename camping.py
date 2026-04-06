import streamlit as st

# 1. Setup the page to be wide so the websites have room
st.set_page_config(page_title="Trip Command Center", layout="wide")

st.sidebar.title("Navigation")
st.sidebar.info("Select a tool below to view it inside this app.")

# 2. Define your two website links here
site_one_name = "Trip Availability"
site_one_url = "https://forms.gle/wbV27pZhhQbU1NNZA"  # Replace with your actual link

site_two_name = "Suggestion Box"
site_two_url = "https://forms.gle/Fc9vH3kgC1hy7GVj6"  # Replace with your actual link

# 3. Sidebar Selection
choice = st.sidebar.radio("Go to:", [site_one_name, site_two_name])

# 4. Display Logic
if choice == site_one_name:
    st.subheader(f"Showing: {site_one_name}")
    st.caption(f"If the window below is blank, [click here to open in a new tab]({site_one_url})")

    # This embeds the site
    st.components.v1.iframe(site_one_url, height=900, scrolling=True)

elif choice == site_two_name:
    st.subheader(f"Showing: {site_two_name}")
    st.caption(f"If the window below is blank, [click here to open in a new tab]({site_two_url})")

    # This embeds the site
    st.components.v1.iframe(site_two_url, height=900, scrolling=True)
