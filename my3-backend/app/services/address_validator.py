"""
Address validation service using Google Maps Geocoding API or SmartyStreets API.
Handles validation gracefully - always returns a result, never blocks recipient creation.
"""
import logging
import json
from typing import Optional, Dict, Any
import httpx
from app.config import settings

logger = logging.getLogger(__name__)


async def validate_address(
    street: Optional[str] = None,
    city: Optional[str] = None,
    state: Optional[str] = None,
    postal_code: Optional[str] = None,
    country: Optional[str] = None
) -> Dict[str, Any]:
    """
    Validate an address using available validation service.
    
    Returns:
        {
            "validated": bool,
            "normalized_address": dict or None,
            "status": str,  # "validated", "unvalidated", "failed"
            "error": str or None
        }
    
    Always returns a result - never raises exceptions.
    If validation fails, returns status "unvalidated" with original address.
    """
    # Check if validation is enabled
    if not settings.enable_address_validation:
        logger.info("Address validation is disabled")
        return {
            "validated": False,
            "normalized_address": None,
            "status": "unvalidated",
            "error": "Validation disabled"
        }
    
    # Check if we have required fields
    if not street or not city:
        logger.info("Address validation skipped - missing required fields (street or city)")
        return {
            "validated": False,
            "normalized_address": None,
            "status": "unvalidated",
            "error": "Missing required fields"
        }
    
    # Try Google Maps API first if available
    if settings.google_maps_api_key:
        try:
            return await _validate_with_google_maps(street, city, state, postal_code, country)
        except Exception as e:
            logger.warning(f"Google Maps validation failed: {e}")
            # Fall through to return unvalidated
    
    # Try SmartyStreets API if available
    if settings.smartystreets_api_key:
        try:
            return await _validate_with_smartystreets(street, city, state, postal_code, country)
        except Exception as e:
            logger.warning(f"SmartyStreets validation failed: {e}")
            # Fall through to return unvalidated
    
    # No validation service available or all failed
    logger.info("No address validation service available or all services failed")
    return {
        "validated": False,
        "normalized_address": None,
        "status": "unvalidated",
        "error": "No validation service available"
    }


async def _validate_with_google_maps(
    street: str,
    city: str,
    state: Optional[str] = None,
    postal_code: Optional[str] = None,
    country: Optional[str] = None
) -> Dict[str, Any]:
    """Validate address using Google Maps Geocoding API."""
    # Build address string
    address_parts = [street, city]
    if state:
        address_parts.append(state)
    if postal_code:
        address_parts.append(postal_code)
    if country:
        address_parts.append(country)
    
    address_string = ", ".join(address_parts)
    
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": address_string,
        "key": settings.google_maps_api_key
    }
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") == "OK" and data.get("results"):
                # Get the first result (most likely match)
                result = data["results"][0]
                address_components = result.get("address_components", [])
                
                # Extract normalized address components
                normalized = {
                    "formatted_address": result.get("formatted_address", ""),
                    "street_number": "",
                    "route": "",
                    "locality": "",
                    "administrative_area_level_1": "",
                    "postal_code": "",
                    "country": ""
                }
                
                for component in address_components:
                    types = component.get("types", [])
                    if "street_number" in types:
                        normalized["street_number"] = component.get("long_name", "")
                    elif "route" in types:
                        normalized["route"] = component.get("long_name", "")
                    elif "locality" in types or "sublocality" in types:
                        normalized["locality"] = component.get("long_name", "")
                    elif "administrative_area_level_1" in types:
                        normalized["administrative_area_level_1"] = component.get("short_name", "")
                    elif "postal_code" in types:
                        normalized["postal_code"] = component.get("long_name", "")
                    elif "country" in types:
                        normalized["country"] = component.get("short_name", "")
                
                logger.info(f"Address validated successfully: {normalized['formatted_address']}")
                return {
                    "validated": True,
                    "normalized_address": normalized,
                    "status": "validated",
                    "error": None
                }
            else:
                # API returned but address not found
                logger.info(f"Google Maps API returned status: {data.get('status')}")
                return {
                    "validated": False,
                    "normalized_address": None,
                    "status": "unvalidated",
                    "error": f"Address not found: {data.get('status')}"
                }
    
    except httpx.TimeoutException:
        logger.warning("Google Maps API timeout")
        return {
            "validated": False,
            "normalized_address": None,
            "status": "unvalidated",
            "error": "Validation timeout"
        }
    except httpx.HTTPStatusError as e:
        logger.warning(f"Google Maps API HTTP error: {e}")
        return {
            "validated": False,
            "normalized_address": None,
            "status": "unvalidated",
            "error": f"HTTP error: {e.response.status_code}"
        }
    except Exception as e:
        logger.error(f"Google Maps validation error: {e}", exc_info=True)
        return {
            "validated": False,
            "normalized_address": None,
            "status": "unvalidated",
            "error": str(e)
        }


async def _validate_with_smartystreets(
    street: str,
    city: str,
    state: Optional[str] = None,
    postal_code: Optional[str] = None,
    country: Optional[str] = None
) -> Dict[str, Any]:
    """Validate address using SmartyStreets API."""
    # SmartyStreets primarily works with US addresses
    if country and country.upper() not in ["US", "USA", "UNITED STATES"]:
        logger.info("SmartyStreets only supports US addresses")
        return {
            "validated": False,
            "normalized_address": None,
            "status": "unvalidated",
            "error": "SmartyStreets only supports US addresses"
        }
    
    url = "https://us-street.api.smartystreets.com/street-address"
    params = {
        "auth-id": settings.smartystreets_api_key.split(":")[0] if ":" in settings.smartystreets_api_key else settings.smartystreets_api_key,
        "auth-token": settings.smartystreets_api_key.split(":")[1] if ":" in settings.smartystreets_api_key else "",
        "street": street,
        "city": city,
        "state": state or "",
        "zipcode": postal_code or ""
    }
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data and isinstance(data, list) and len(data) > 0:
                # Get the first result
                result = data[0]
                components = result.get("components", {})
                metadata = result.get("metadata", {})
                
                normalized = {
                    "formatted_address": result.get("delivery_line_1", ""),
                    "street_number": components.get("primary_number", ""),
                    "route": components.get("street_name", ""),
                    "locality": components.get("city_name", ""),
                    "administrative_area_level_1": components.get("state_abbreviation", ""),
                    "postal_code": components.get("zipcode", ""),
                    "country": "US"
                }
                
                logger.info(f"Address validated successfully with SmartyStreets")
                return {
                    "validated": True,
                    "normalized_address": normalized,
                    "status": "validated",
                    "error": None
                }
            else:
                logger.info("SmartyStreets API returned no results")
                return {
                    "validated": False,
                    "normalized_address": None,
                    "status": "unvalidated",
                    "error": "Address not found"
                }
    
    except httpx.TimeoutException:
        logger.warning("SmartyStreets API timeout")
        return {
            "validated": False,
            "normalized_address": None,
            "status": "unvalidated",
            "error": "Validation timeout"
        }
    except httpx.HTTPStatusError as e:
        logger.warning(f"SmartyStreets API HTTP error: {e}")
        return {
            "validated": False,
            "normalized_address": None,
            "status": "unvalidated",
            "error": f"HTTP error: {e.response.status_code}"
        }
    except Exception as e:
        logger.error(f"SmartyStreets validation error: {e}", exc_info=True)
        return {
            "validated": False,
            "normalized_address": None,
            "status": "unvalidated",
            "error": str(e)
        }

