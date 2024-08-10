import streamlit as st
import json
import os
import requests
import streamlit.components.v1 as components

# Define file path
json_file = 'khouribga_sites.json'

# Load existing sites from JSON file
def load_sites():
    if os.path.exists(json_file):
        with open(json_file, 'r') as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                return []  # Return empty list if JSON is malformed
    return []

# Save sites to JSON file
def save_sites(sites):
    with open(json_file, 'w') as file:
        json.dump(sites, file, indent=4)

# HTML and CSS for styling
tooltip_style = """
<style>
.tooltip-container {
    position: relative;
    display: inline-block;
    margin: 4px;
}

.green-button, .details-button, .delete-button {
    background-color: #4CAF50; 
    color: white; 
    border: none; 
    padding: 8px 14px;  /* Slightly larger padding */
    text-align: center; 
    display: inline-block; 
    font-size: 15px;    /* Slightly larger font size */
    cursor: pointer;
    border-radius: 5px;
    transition: background-color 0.3s;
    min-width: 110px;  /* Slightly larger minimum width */
}

.green-button:hover {
    background-color: #45a049;
}

.details-button {
    background-color: #f0f0f0;
    color: black;
}

.details-button:hover {
    background-color: #ddd;
}

.delete-button {
    background-color: #ff4d4d;
    color: white;
}

.delete-button:hover {
    background-color: #ff1a1a;
}

.tooltip-container .tooltiptext {
    visibility: hidden;
    width: 200px;
    background-color: #555;
    color: #fff;
    text-align: center;
    border-radius: 6px;
    padding: 5px;
    position: absolute;
    z-index: 1;
    bottom: 125%; /* Position above the button */
    left: 50%;
    margin-left: -100px;
    opacity: 0;
    transition: opacity 0.3s;
}

.tooltip-container:hover .tooltiptext {
    visibility: visible;
    opacity: 1;
}
</style>
"""

# Initialize the app
st.title("Site Khouribga")
st.markdown("## Manage and View Sites in Khouribga")

# Load existing sites
sites = load_sites()

# Initialize session state for tracking clicked site
if 'clicked_site' not in st.session_state:
    st.session_state.clicked_site = None

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.selectbox("Choose a page", ["Add New Site", "View All Sites"])

# Page: Add New Site
if page == "Add New Site":
    st.subheader("Add a New Site")
    with st.form("Create Site"):
        name = st.text_input("Site Name")
        info1 = st.text_input("Information 1")
        info2 = st.text_input("Information 2")
        info3 = st.text_input("Information 3")
        latitude = st.number_input("Latitude", format="%.6f")
        longitude = st.number_input("Longitude", format="%.6f")

        submitted = st.form_submit_button("Submit")
        if submitted and name and info1 and info2 and info3:
            new_site = {
                'name': name,
                'info1': info1,
                'info2': info2,
                'info3': info3,
                'latitude': latitude,
                'longitude': longitude
            }
            sites.append(new_site)
            save_sites(sites)
            st.success(f"Site '{name}' created successfully!")

# Page: View All Sites
else:
    st.subheader("All Sites")
    if sites:
        st.markdown(tooltip_style, unsafe_allow_html=True)

        # Display site name buttons with tooltip and click handling
        for site in sites:
            # Display buttons
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                button_html = f"""
                <div class="tooltip-container">
                    <button class="green-button">{site['name']}</button>
                    <span class="tooltiptext">{site['info1']}</span>
                </div>
                """
                st.markdown(button_html, unsafe_allow_html=True)
            with col2:
                if st.button("Details", key=f"details_{site['name']}"):
                    st.session_state.clicked_site = site['name']
                    st.experimental_rerun()
            with col3:
                if st.button("Delete", key=f"delete_{site['name']}"):
                    sites = [s for s in sites if s['name'] != site['name']]
                    save_sites(sites)
                    st.experimental_rerun()

        # Show detailed information if a site was clicked
        clicked_site = st.session_state.clicked_site
        if clicked_site:
            site = next((s for s in sites if s['name'] == clicked_site), None)
            if site:
                st.markdown(f"**Name**: {site['name']}")
                st.markdown(f"**Information 1**: {site['info1']}")
                st.markdown(f"**Information 2**: {site['info2']}")
                st.markdown(f"**Information 3**: {site['info3']}")
                st.markdown(f"**Location**: [View on Google Maps](https://www.google.com/maps/?q={site['latitude']},{site['longitude']})")
                
                # Embed interactive HERE map with marker
                map_html = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Interactive Map</title>
                    <meta charset="utf-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <script src="https://js.api.here.com/v3/3.1/mapsjs-core.js"></script>
                    <script src="https://js.api.here.com/v3/3.1/mapsjs-service.js"></script>
                    <script src="https://js.api.here.com/v3/3.1/mapsjs-mapevents.js"></script>
                    <script src="https://js.api.here.com/v3/3.1/mapsjs-ui.js"></script>
                    <script src="https://js.api.here.com/v3/3.1/mapsjs-places.js"></script>
                    <style>
                        #map {{
                            height: 400px;  /* Increased height */
                            width: 600px;  /* Increased width */
                        }}
                        .leaflet-control-zoom {{
                            font-size: 16px;  /* Adjust zoom control size */
                        }}
                    </style>
                </head>
                <body>
                    <div id="map"></div>
                    <script>
                        var platform = new H.service.Platform({{ 'apikey': 'YOUR_HERE_API_KEY' }});
                        var defaultLayers = platform.createDefaultLayers();
                        var map = new H.Map(
                            document.getElementById('map'),
                            defaultLayers.vector.normal.map,
                            {{
                                zoom: 14,
                                center: {{ lat: {site['latitude']}, lng: {site['longitude']} }}
                            }}
                        );

                        var behavior = new H.mapevents.Behavior(new H.mapevents.MapEvents(map));
                        var ui = H.ui.UI.createDefault(map, defaultLayers);

                        // Add a marker to the map
                        var marker = new H.map.Marker({{ lat: {site['latitude']}, lng: {site['longitude']} }});
                        map.addObject(marker);

                        // Add zoom control
                        var zoomControl = new H.ui.ZoomControl();
                        ui.addControl('zoom', zoomControl);
                    </script>
                </body>
                </html>
                """
                components.html(map_html, height=400, width=600)  # Adjust height and width
                if st.button("Back"):
                    st.session_state.clicked_site = None
                    st.experimental_rerun()

    else:
        st.info("No sites available. Create a new site using the 'Add New Site' page.")
