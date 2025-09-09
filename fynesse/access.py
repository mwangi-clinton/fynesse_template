"""
Access module for the fynesse framework.

This module handles data access functionality including:
- Data loading from various sources (web, local files, databases)
- Legal compliance (intellectual property, privacy rights)
- Ethical considerations for data usage
- Error handling for access issues

Legal and ethical considerations are paramount in data access.
Ensure compliance with e.g. .GDPR, intellectual property laws, and ethical guidelines.
"""

from typing import Any, Dict, Optional, Union
import pandas as pd
import logging
import osmnx as ox
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import geopandas as gpd  # type: ignore[import]


# Type alias for OSM tag dictionaries expected by osmnx
TagsType = Dict[str, Union[bool, str, list[str]]]

# Set up basic logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def data() -> Optional[pd.DataFrame]:
    """
    Read the data from the web or local file, returning a pandas DataFrame.

    Replace with your actual data-loading logic.
    """
    logger.info("Starting data access operation")

    try:
        logger.info("Loading data from data.csv")
        df = pd.read_csv("data.csv")

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
    place_name: str,
    latitude: float,
    longitude: float,
    boxing_size: float,
    return_fig: bool = False,
) -> Optional[Figure]:
    """
    Plot a city map using OpenStreetMap (OSM) data around a given location.

    Args:
        place_name (str): Name of the place (e.g., "Nyeri, Kenya")
        latitude (float): Center latitude
        longitude (float): Center longitude
        boxing_size (float): Size of the bounding box (approx. in km)
        return_fig (bool): If True, do NOT call plt.show() and instead return the Figure object.
                           If False (default), show the plot and return None.

    Returns:
        Optional[matplotlib.figure.Figure]: The matplotlib figure object if return_fig is True,
                                           otherwise None on success or None on failure.
    """
    logger.info(f"Starting map plot for {place_name} at ({latitude}, {longitude})")

    try:
        # Define bounding box (degrees)
        box_width = boxing_size / 111  # ~111 km per degree
        box_height = boxing_size / 111
        north = latitude + box_height / 2
        south = latitude - box_height / 2
        west = longitude - box_width / 2
        east = longitude + box_width / 2

        logger.info(f"Bounding box (N,S,E,W): {north}, {south}, {east}, {west}")

        # Define tags with explicit value union type to satisfy mypy/osmnx typing
        tags: TagsType = {
            "amenity": True,
            "building": True,
            "historic": True,
            "leisure": True,
            "shop": True,
            "tourism": True,
            "religion": True,
            "memorial": True,
        }
        building_tags: TagsType = {"building": True}

        # Load OSM data
        logger.info("Fetching OSM graph data...")
        graph = ox.graph_from_bbox(north, south, east, west)

        logger.info("Fetching OSM geocode data...")
        area = ox.geocode_to_gdf(place_name)

        logger.info("Fetching street network data...")
        nodes, edges = ox.graph_to_gdfs(graph)

        logger.info("Fetching buildings data...")
        buildings = ox.features_from_bbox(north, south, east, west, tags=building_tags)

        logger.info("Fetching POIs...")
        pois = ox.features_from_bbox(north, south, east, west, tags=tags)

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
        fig.tight_layout()

        logger.info(f"Successfully plotted map for {place_name}")

        if return_fig:
            # Caller wants the figure object to manipulate or display themselves.
            return fig

        # Default behaviour: display the figure and return None (keeps previous logic)
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
    return_fig: bool = False,
) -> Optional[Figure]:
    """
    Plot a city map using OpenStreetMap (OSM) data around a given location,
    and overlay dataset points (lat/lon) as red markers.

    Args:
        place_name (str): Name of the place (e.g., "Nyeri, Kenya")
        latitude (float): Center latitude
        longitude (float): Center longitude
        boxing_size (float): Size of the bounding box (approx. in km)
        porini_df (pd.DataFrame): Dataset containing 'Latitude' and 'Longitude' columns
        return_fig (bool): If True, do NOT call plt.show() and instead return the Figure object.

    Returns:
        Optional[matplotlib.figure.Figure]: The matplotlib figure object if return_fig is True,
                                           otherwise None on success or None on failure.
    """
    logger.info(f"Starting map plot for {place_name} with dataset points")

    try:
        # Validate the porini_df has the expected columns
        if not {"Latitude", "Longitude"}.issubset(porini_df.columns):
            raise ValueError("porini_df must contain 'Latitude' and 'Longitude' columns")

        # Define bounding box (degrees)
        box_width = boxing_size / 111  # ~111 km per degree
        box_height = boxing_size / 111
        north = latitude + box_height / 2
        south = latitude - box_height / 2
        west = longitude - box_width / 2
        east = longitude + box_width / 2

        logger.info(f"Bounding box (N,S,E,W): {north}, {south}, {east}, {west}")

        # Tags
        tags: TagsType = {
            "amenity": True,
            "building": True,
            "historic": True,
            "leisure": True,
            "shop": True,
            "tourism": True,
            "religion": True,
            "memorial": True,
        }
        building_tags: TagsType = {"building": True}

        # Load OSM data
        logger.info("Fetching OSM graph data...")
        graph = ox.graph_from_bbox(north, south, east, west)

        logger.info("Fetching OSM geocode data...")
        area = ox.geocode_to_gdf(place_name)

        logger.info("Fetching street network data...")
        nodes, edges = ox.graph_to_gdfs(graph)

        logger.info("Fetching buildings data...")
        buildings = ox.features_from_bbox(north, south, east, west, tags=building_tags)

        logger.info("Fetching POIs...")
        pois = ox.features_from_bbox(north, south, east, west, tags=tags)

        # Convert dataset to GeoDataFrame
        gdf_points = gpd.GeoDataFrame(
            porini_df.copy(),
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
        fig.tight_layout()

        logger.info(f"Successfully plotted map for {place_name}")

        if return_fig:
            return fig

        plt.show()
        return None

    except Exception as e:
        logger.error(f"Error while plotting map for {place_name}: {e}")
        print(f"Error: Could not plot map for {place_name}. {e}")
        return None
