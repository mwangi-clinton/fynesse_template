"""
Access module for the fynesse framework.

This module handles data access functionality including:
- Data loading from various sources (web, local files, databases)
- Legal compliance (intellectual property, privacy rights)
- Ethical considerations for data usage
- Error handling for access issues

Legal and ethical considerations are paramount in data access.
Ensure compliance with e.g. .GDPR, intellectual property laws, and ethical guidelines.

Best Practice on Implementation
===============================

1. BASIC ERROR HANDLING:
   - Use try/except blocks to catch common errors
   - Provide helpful error messages for debugging
   - Log important events for troubleshooting

2. WHERE TO ADD ERROR HANDLING:
   - File not found errors when loading data
   - Network errors when downloading from web
   - Permission errors when accessing files
   - Data format errors when parsing files

3. SIMPLE LOGGING:
   - Use print() statements for basic logging
   - Log when operations start and complete
   - Log errors with context information
   - Log data summary information

4. EXAMPLE PATTERNS:
   
   Basic error handling:
   try:
       df = pd.read_csv('data.csv')
   except FileNotFoundError:
       print("Error: Could not find data.csv file")
       return None
   
   With logging:
   print("Loading data from data.csv...")
   try:
       df = pd.read_csv('data.csv')
       print(f"Successfully loaded {len(df)} rows of data")
       return df
   except FileNotFoundError:
       print("Error: Could not find data.csv file")
       return None
"""
from typing import Any, Union, Optional, List, Dict
import pandas as pd
import logging
import osmnx as ox
import matplotlib.pyplot as plt
import geopandas as gpd  # type: ignore

# Set up basic logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def data() -> Union[pd.DataFrame, None]:
    """
    Read the data from the web or local file, returning structured format such as a data frame.

    IMPLEMENTATION GUIDE
    ====================

    1. REPLACE THIS FUNCTION WITH YOUR ACTUAL DATA LOADING CODE:
       - Load data from your specific sources
       - Handle common errors (file not found, network issues)
       - Validate that data loaded correctly
       - Return the data in a useful format

    2. ADD ERROR HANDLING:
       - Use try/except blocks for file operations
       - Check if data is empty or corrupted
       - Provide helpful error messages

    3. ADD BASIC LOGGING:
       - Log when you start loading data
       - Log success with data summary
       - Log errors with context

    4. EXAMPLE IMPLEMENTATION:
       try:
           print("Loading data from data.csv...")
           df = pd.read_csv('data.csv')
           print(f"Successfully loaded {len(df)} rows, {len(df.columns)} columns")
           return df
       except FileNotFoundError:
           print("Error: data.csv file not found")
           return None
       except Exception as e:
           print(f"Error loading data: {e}")
           return None

    Returns:
        DataFrame or other structured data format
    """
    logger.info("Starting data access operation")

    try:
        # IMPLEMENTATION: Replace this with your actual data loading code
        # Example: Load data from a CSV file
        logger.info("Loading data from data.csv")
        df = pd.read_csv("data.csv")

        # Basic validation
        if df.empty:
            logger.warning("Loaded data is empty")
            return None

        logger.info(
            f"Successfully loaded data: {len(df)} rows, {len(df.columns)} columns"
        )
        return df

    except FileNotFoundError:
        logger.error("Data file not found: data.csv")
        print("Error: Could not find data.csv file. Please check the file path.")
        return None
    except Exception as e:
        logger.error(f"Unexpected error loading data: {e}")
        print(f"Error loading data: {e}")
        return None


def plot_city_map(
    place_name: str, latitude: float, longitude: float, boxing_size: float
) -> Optional[plt.Figure]:
    """
    Plot a city map using OpenStreetMap (OSM) data around a given location.

    Args:
        place_name (str): Name of the place (e.g., "Nyeri, Kenya")
        latitude (float): Center latitude
        longitude (float): Center longitude
        boxing_size (float): Size of the bounding box (approx. in km)

    Returns:
        Optional[plt.Figure]: The matplotlib figure object if successful, None otherwise
    """
    logger.info(f"Starting map plot for {place_name} at ({latitude}, {longitude})")

    try:
        # Define bounding box
        box_width = boxing_size / 111  # ~111 km per degree
        box_height = boxing_size / 111
        north = latitude + box_height / 2
        south = latitude - box_height / 2
        west = longitude - box_width / 2
        east = longitude + box_width / 2
        bbox = (west, south, east, north)

        logger.info(f"Bounding box: {bbox}")

        # Define tags with proper type
        tags: Dict[str, Union[bool, str, List[str]]] = {
            "amenity": True,
            "building": True,
            "historic": True,
            "leisure": True,
            "shop": True,
            "tourism": True,
            "religion": True,
            "memorial": True,
        }

        # Load OSM data
        logger.info("Fetching OSM graph data...")
        graph = ox.graph_from_bbox(bbox)
        logger.info("Fetching OSM geocode data...")
        area = ox.geocode_to_gdf(place_name)

        logger.info("Fetching street network data...")
        nodes, edges = ox.graph_to_gdfs(graph)

        logger.info("Fetching buildings data...")
        buildings = ox.features_from_bbox(bbox, tags={"building": True})

        logger.info("Fetching POIs...")
        pois = ox.features_from_bbox(bbox, tags=tags)

        # Plot
        fig, ax = plt.subplots(figsize=(6, 6))
        area.plot(ax=ax, color="tan", alpha=0.5)
        buildings.plot(ax=ax, facecolor="gray", edgecolor="gray")
        edges.plot(ax=ax, linewidth=1, edgecolor="black", alpha=0.3)
        nodes.plot(ax=ax, color="black", markersize=1, alpha=0.3)
        pois.plot(ax=ax, color="green", markersize=5, alpha=1)

        ax.set_xlim(west, east)
        ax.set_ylim(south, north)
        ax.set_title(place_name, fontsize=14)

        logger.info(f"Successfully plotted map for {place_name}")

        plt.show()

        return None

    except Exception as e:
        logger.error(f"Error while plotting map for {place_name}: {e}")
        print(f"Error: Could not plot map for {place_name}. {e}")
        return None


def plot_city_map_with_points(
    place_name: str,
    latitude: float,
    longitude: float,
    boxing_size: float,
    porini_df: pd.DataFrame,
) -> Optional[plt.Figure]:
    """
    Plot a city map using OpenStreetMap (OSM) data around a given location,
    and overlay dataset points (lat/lon) as red markers.

    Args:
        place_name (str): Name of the place (e.g., "Nyeri, Kenya")
        latitude (float): Center latitude
        longitude (float): Center longitude
        boxing_size (float): Size of the bounding box (approx. in km)
        porini_df (pd.DataFrame): Dataset containing 'Latitude' and 'Longitude' columns

    Returns:
        Optional[plt.Figure]: The matplotlib figure object if successful, None otherwise
    """
    logger.info(f"Starting map plot for {place_name} with dataset points")

    try:
        # Define bounding box
        box_width = boxing_size / 111  # ~111 km per degree
        box_height = boxing_size / 111
        north = latitude + box_height / 2
        south = latitude - box_height / 2
        west = longitude - box_width / 2
        east = longitude + box_width / 2
        bbox = (west, south, east, north)

        logger.info(f"Bounding box: {bbox}")

        # Define tags with proper type
        tags: Dict[str, Union[bool, str, List[str]]] = {
            "amenity": True,
            "building": True,
            "historic": True,
            "leisure": True,
            "shop": True,
            "tourism": True,
            "religion": True,
            "memorial": True,
        }

        # Load OSM data
        logger.info("Fetching OSM graph data...")
        graph = ox.graph_from_bbox(bbox)

        logger.info("Fetching OSM geocode data...")
        area = ox.geocode_to_gdf(place_name)

        logger.info("Fetching street network data...")
        nodes, edges = ox.graph_to_gdfs(graph)

        logger.info("Fetching buildings data...")
        buildings = ox.features_from_bbox(bbox, tags={"building": True})

        logger.info("Fetching POIs...")
        pois = ox.features_from_bbox(bbox, tags=tags)

        # Convert dataset to GeoDataFrame
        gdf_points = gpd.GeoDataFrame(
            porini_df,
            geometry=gpd.points_from_xy(porini_df["Longitude"], porini_df["Latitude"]),
            crs="EPSG:4326",
        )

        logger.info(f"Overlaying {len(gdf_points)} dataset points on map")

        # Plot
        fig, ax = plt.subplots(figsize=(6, 6))
        area.plot(ax=ax, color="tan", alpha=0.5)
        buildings.plot(ax=ax, facecolor="gray", edgecolor="gray")
        edges.plot(ax=ax, linewidth=1, edgecolor="black", alpha=0.3)
        nodes.plot(ax=ax, color="black", markersize=1, alpha=0.3)
        pois.plot(ax=ax, color="green", markersize=5, alpha=1)

        # Plot dataset points
        gdf_points.plot(
            ax=ax, color="red", markersize=40, alpha=0.7, label="Dataset Points"
        )

        ax.set_xlim(west, east)
        ax.set_ylim(south, north)
        ax.set_title(place_name, fontsize=14)
        ax.legend()

        logger.info(f"Successfully plotted map for {place_name}")
        plt.show()
        return None

    except Exception as e:
        logger.error(f"Error while plotting map for {place_name}: {e}")
        print(f"Error: Could not plot map for {place_name}. {e}")
        return None
