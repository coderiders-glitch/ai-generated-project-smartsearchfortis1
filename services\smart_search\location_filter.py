import logging
import math
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class LocationFilter:
    """Filter search results by geographic location."""

    def __init__(self):
        self.earth_radius_km = 6371
        logger.info("LocationFilter initialized")

    def filter_by_location(
        self,
        results: List[Dict[str, Any]],
        latitude: float,
        longitude: float,
        radius_km: float
    ) -> List[Dict[str, Any]]:
        """Filter results to only include items within specified radius."""
        try:
            filtered_results = []
            
            for item in results:
                item_latitude = item.get("latitude")
                item_longitude = item.get("longitude")
                
                if item_latitude is None or item_longitude is None:
                    logger.debug(f"Item {item.get('id')} missing location data")
                    continue
                
                distance = self._calculate_distance(
                    latitude, longitude, item_latitude, item_longitude
                )
                
                if distance <= radius_km:
                    item["distance_km"] = round(distance, 2)
                    filtered_results.append(item)
            
            logger.info(f"Location filter: {len(filtered_results)} results within {radius_km}km")
            return filtered_results
        except Exception as error:
            logger.error(f"Location filter error: {str(error)}")
            return results

    def _calculate_distance(
        self,
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float
    ) -> float:
        """Calculate distance between two coordinates using Haversine formula."""
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        delta_lat = lat2_rad - lat1_rad
        delta_lon = lon2_rad - lon1_rad
        
        a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
        c = 2 * math.asin(math.sqrt(a))
        
        distance = self.earth_radius_km * c
        return distance