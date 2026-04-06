import streamlit as st

# 1. Setup the page to be wide
st.set_page_config(page_title="Trip Command Center", layout="wide", page_icon="✈️")

st.sidebar.title("Navigation")
st.sidebar.info("Select a tool below to view it inside this app.")

# Define page names and URLs
welcome_name = "🏠 Welcome"
site_one_name = "📅 Trip Availability"
site_one_url = "https://forms.gle/wbV27pZhhQbU1NNZA" 

site_two_name = "💡 Suggestion Box"
site_two_url = "https://forms.gle/Fc9vH3kgC1hy7GVj6" 

# 2. Sidebar Selection (Added Welcome to the list)
choice = st.sidebar.radio("Go to:", [welcome_name, site_one_name, site_two_name])

# 3. Display Logic
if choice == welcome_name:
    # --- THIS IS YOUR NEW WELCOME PAGE ---
    st.title("Welcome to the Trip Hub! 🗺️")
    
    st.markdown("""
    ### Thanks for being interested in going camping this summer. This site should make planning easier!
    
    Use the navigation menu on the left to coordinate our schedules and brainstorm ideas. 
    
    **How to use this app:**
    1.  **Check Availability:** Head over to the **Trip Availability** tab and fill out the form so we can find our overlapping dates.
    2.  **Suggest Ideas:** Got a specificlocationin mind? Drop it in the **Suggestion Box**.
    
    *Note: If the embedded forms appear blank or won't load, use the "click here" links at the top of each page to open them in a new window.*
    """)
    
    st.info("Log your dates by the end of the week so we can start booking!")

elif choice == site_one_name:
    st.subheader(f"Showing: {site_one_name}")
    st.caption(f"If the window below is blank, [click here to open in a new tab]({site_one_url})")

    # This embeds the site
    st.components.v1.iframe(site_one_url, height=900, scrolling=True)

elif choice == site_two_name:
    st.subheader(f"Showing: {site_two_name}")
    st.caption(f"If the window below is blank, [click here to open in a new tab]({site_two_url})")

    # This embeds the site
    st.components.v1.iframe(site_two_url, height=900, scrolling=True)
