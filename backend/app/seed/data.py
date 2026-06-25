"""Static reference pools used to generate realistic synthetic data."""
from __future__ import annotations

# (region name, center latitude, center longitude, base population density)
REGIONS: list[tuple[str, float, float, int]] = [
    ("Gulf Coast", 29.76, -95.37, 1400),
    ("Bay Area", 37.77, -122.42, 2700),
    ("South Florida", 25.76, -80.19, 2000),
    ("Pacific Northwest", 47.61, -122.33, 1300),
    ("Front Range", 39.74, -104.99, 1600),
    ("Great Lakes", 41.88, -87.63, 1900),
    ("Mid-Atlantic", 38.91, -77.04, 1800),
    ("Southern California", 34.05, -118.24, 2500),
    ("Gulf Plains", 30.27, -97.74, 1200),
    ("Northeast Corridor", 40.71, -74.01, 3200),
]

INCIDENT_NAME_PREFIX = {
    "wildfire": ["Ridge", "Canyon", "Summit", "Pine", "Mesa", "Foothill", "Timber"],
    "flood": ["River", "Delta", "Bayou", "Lowland", "Basin", "Creek"],
    "hurricane": ["Atlantic", "Coastal", "Tropical", "Tidewater"],
    "earthquake": ["Fault", "Seismic", "Rift", "Tremor"],
    "industrial_accident": ["Refinery", "Plant", "Terminal", "Depot"],
    "disease_outbreak": ["Metro", "County", "Regional", "Urban"],
    "infrastructure_failure": ["Grid", "Bridge", "Tunnel", "Dam"],
    "severe_storm": ["Supercell", "Squall", "Thunder", "Hail"],
}

INCIDENT_NAME_SUFFIX = {
    "wildfire": ["Fire", "Blaze", "Burn Complex"],
    "flood": ["Flood", "Flooding Event", "Inundation"],
    "hurricane": ["Hurricane", "Storm System"],
    "earthquake": ["Earthquake", "Seismic Event"],
    "industrial_accident": ["Incident", "Release", "Explosion"],
    "disease_outbreak": ["Outbreak", "Cluster", "Surge"],
    "infrastructure_failure": ["Failure", "Collapse", "Outage"],
    "severe_storm": ["Storm", "Weather Event"],
}

HOSPITAL_NAMES = [
    "General", "Memorial", "Regional Medical Center", "Mercy", "St. Vincent",
    "University Medical", "Sacred Heart", "Providence", "Mount Sinai", "Baptist",
    "Methodist", "Children's", "Veterans", "Community", "Presbyterian",
]

SHELTER_VENUES = [
    "Community Center", "High School Gymnasium", "Convention Hall", "Recreation Center",
    "Civic Auditorium", "Fairgrounds Pavilion", "Sports Arena", "Church Hall",
    "Armory", "Field House", "Public Library Annex", "Stadium Concourse",
]

RESOURCE_LABELS = {
    "ambulance": ("Medic Unit", "units", 2),
    "fire_truck": ("Engine Company", "units", 1),
    "medical_team": ("Medical Strike Team", "personnel", 8),
    "rescue_team": ("Search & Rescue Team", "personnel", 10),
    "helicopter": ("Air Asset", "units", 1),
    "food_supply": ("Food Cache", "meals", 5000),
    "water_supply": ("Water Cache", "liters", 20000),
    "fuel_supply": ("Fuel Depot", "liters", 30000),
    "generator": ("Mobile Generator", "kW", 250),
}

DATA_SOURCES = [
    ("National Weather Service Feed", "weather_api", "https://api.weather.gov"),
    ("NOAA Storm Prediction", "weather_api", "https://api.noaa.gov/storms"),
    ("State GIS Hazard Layer", "gis_feed", "https://gis.state.gov/hazards/wfs"),
    ("Regional Hospital Bed Registry", "hospital_system", "https://hhs.example.gov/beds"),
    ("County 911 CAD Bridge", "emergency_call_system", "https://cad.county.gov/api"),
    ("Statewide Resource Tracker", "resource_system", "https://resources.state.gov/api"),
    ("Utility Outage Aggregator", "gis_feed", "https://outage.utility.com/feed"),
]
