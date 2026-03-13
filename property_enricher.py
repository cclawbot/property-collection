#!/usr/bin/env python3
"""
Property Enricher - Uses Geoapify API, Heritage Council, and BetterEducation
"""

import csv
import json
import os
import time
import math
import re
import requests
from datetime import datetime
from bs4 import BeautifulSoup

# Configuration
GEOAPIFY_API_KEY = "07c63cf239774696acf794e8b3c0c140"
TARGET_ADDRESS = "4 Freshwater Pl, Southbank VIC 3006"
BOXHILL_CENTRAL = "Box Hill Central, Victoria"

# CSV file path
CSV_PATH = os.path.join(os.path.dirname(__file__), "properties_all.csv")

# New columns to add
NEW_COLUMNS = [
    "Has Swimming Pool",
    "On Main Road", 
    "T-Shape Intersection",
    "Heritage Overlay",
    "PT Time to Target",
    "Drive Time to Target",
    "Primary School Zone",
    "Primary School Ranking",
    "Secondary School Zone",
    "Secondary School Ranking",
    "Nearest Transport Station",
    "Walk Time to Station",
    "Nearest Supermarket",
    "Walk Time to Supermarket",
    "Drive Time to Supermarket",
    "PT Time to Boxhill Central",
    "Drive Time to Boxhill Central"
]

def geocode_address(address):
    """Convert address to coordinates using Geoapify"""
    url = "https://api.geoapify.com/v1/geocode/search"
    params = {
        "text": address + ", Victoria, Australia",
        "apiKey": GEOAPIFY_API_KEY
    }
    try:
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
        if data.get("features") and len(data["features"]) > 0:
            result = data["features"][0]["properties"]
            return {
                "lat": result.get("lat"),
                "lon": result.get("lon"),
                "formatted": result.get("formatted", address)
            }
    except Exception as e:
        print(f"Geocoding error: {e}")
    return None

def get_travel_time(from_coords, to_coords, mode="drive"):
    """Get travel time using Geoapify Routing API"""
    if not from_coords or not to_coords:
        return {"time": None, "distance": None}
    
    url = "https://api.geoapify.com/v1/routing"
    # Format: lat,lon|lat,lon
    waypoints = f"{from_coords['lat']},{from_coords['lon']}|{to_coords['lat']},{to_coords['lon']}"
    params = {
        "waypoints": waypoints,
        "mode": mode,
        "apiKey": GEOAPIFY_API_KEY
    }
    try:
        resp = requests.get(url, params=params, timeout=15)
        data = resp.json()
        if data.get("features"):
            props = data["features"][0]["properties"]
            return {
                "time": props.get("time", 0) / 60,  # minutes
                "distance": props.get("distance", 0) / 1000  # km
            }
    except Exception as e:
        print(f"Routing error: {e}")
    return {"time": None, "distance": None}

def find_nearby_stations(lat, lon):
    """Find nearest train/bus/tram station using Geoapify Places API"""
    url = "https://api.geoapify.com/v2/places"
    params = {
        "lat": lat,
        "lon": lon,
        "categories": "public_transport.train,public_transport.tram,public_transport.bus",
        "limit": 3,
        "apiKey": GEOAPIFY_API_KEY
    }
    try:
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
        # GeoJSON format - results are in 'features', each feature has 'properties'
        if data.get("features") and len(data["features"]) > 0:
            props = data["features"][0]["properties"]
            return {
                "name": props.get("name", "Unknown"),
                "lat": props.get("lat"),
                "lon": props.get("lon"),
                "distance": props.get("distance", 0)
            }
    except Exception as e:
        print(f"Station search error: {e}")
    return {"name": "Not found", "lat": None, "lon": None, "distance": None}

def find_nearby_supermarket(lat, lon):
    """Find nearest supermarket using Geoapify Places API"""
    url = "https://api.geoapify.com/v2/places"
    params = {
        "lat": lat,
        "lon": lon,
        "categories": "commercial.supermarket",
        "limit": 3,
        "apiKey": GEOAPIFY_API_KEY
    }
    try:
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
        # GeoJSON format
        if data.get("features") and len(data["features"]) > 0:
            props = data["features"][0]["properties"]
            return {
                "name": props.get("name", "Unknown"),
                "lat": props.get("lat"),
                "lon": props.get("lon"),
                "distance": props.get("distance", 0)
            }
    except Exception as e:
        print(f"Supermarket search error: {e}")
    return {"name": "Not found", "lat": None, "lon": None, "distance": None}

def get_school_rankings():
    """Scrape school rankings from BetterEducation"""
    rankings = {
        "primary_gov": [],
        "primary_private": [],
        "secondary_gov": [],
        "secondary_private": []
    }
    
    headers = {"User-Agent": "Mozilla/5.0"}
    
    urls = {
        "primary_gov": "https://bettereducation.com.au/school/Primary/vic/melbourne_top_primary_schools.aspx",
        "primary_private": "https://bettereducation.com.au/school/Primary/vic/melbourne_top_non_government_primary_schools.aspx",
        "secondary_gov": "https://bettereducation.com.au/school/Secondary/vic/melbourne_top_secondary_schools.aspx",
        "secondary_private": "https://bettereducation.com.au/school/Secondary/vic/melbourne_top_non_government_secondary_schools.aspx"
    }
    
    for key, url in urls.items():
        try:
            resp = requests.get(url, headers=headers, timeout=15)
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # Find table with rankings
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                for row in rows[1:]:  # Skip header
                    cols = row.find_all(['td', 'th'])
                    if len(cols) >= 2:
                        # Extract school name and ranking
                        text = cols[0].get_text(strip=True)
                        if text and not text.startswith('#'):
                            rankings[key].append(text)
        except Exception as e:
            print(f"Error fetching {key}: {e}")
    
    return rankings

def check_heritage_overlay(lat, lon):
    """Check heritage overlay"""
    # Victorian Heritage Database would need proper API
    return "TBC - Check vhd.heritagecouncil.vic.gov.au"

def process_property(prop, target_coords, boxhill_coords, school_rankings):
    """Process a single property"""
    address = f"{prop['Address']}, {prop['Suburb']}, Victoria, Australia"
    
    print(f"\nProcessing: {prop['Address']}, {prop['Suburb']}")
    
    coords = geocode_address(address)
    if not coords:
        print(f"  Could not geocode address")
        return None
    
    result = {
        "Has Swimming Pool": "TBC",
        "On Main Road": "TBC",
        "T-Shape Intersection": "TBC", 
        "Heritage Overlay": check_heritage_overlay(coords["lat"], coords["lon"]),
    }
    
    # Travel times
    if target_coords:
        pt = get_travel_time(coords, target_coords, "transit")
        drive = get_travel_time(coords, target_coords, "drive")
        result["PT Time to Target"] = f"{pt['time']:.0f} min" if pt['time'] else "N/A"
        result["Drive Time to Target"] = f"{drive['time']:.0f} min" if drive['time'] else "N/A"
    
    if boxhill_coords:
        pt = get_travel_time(coords, boxhill_coords, "transit")
        drive = get_travel_time(coords, boxhill_coords, "drive")
        result["PT Time to Boxhill Central"] = f"{pt['time']:.0f} min" if pt['time'] else "N/A"
        result["Drive Time to Boxhill Central"] = f"{drive['time']:.0f} min" if drive['time'] else "N/A"
    
    # Transport & Supermarkets
    station = find_nearby_stations(coords["lat"], coords["lon"])
    result["Nearest Transport Station"] = station.get("name", "Not found")
    if station.get("lat"):
        walk_time = get_travel_time(coords, station, "walk")
        result["Walk Time to Station"] = f"{walk_time['time']:.0f} min" if walk_time['time'] else "N/A"
    else:
        result["Walk Time to Station"] = "N/A"
    
    supermarket = find_nearby_supermarket(coords["lat"], coords["lon"])
    result["Nearest Supermarket"] = supermarket.get("name", "Not found")
    if supermarket.get("lat"):
        walk_time = get_travel_time(coords, supermarket, "walk")
        result["Walk Time to Supermarket"] = f"{walk_time['time']:.0f} min" if walk_time['time'] else "N/A"
        drive_time = get_travel_time(coords, supermarket, "drive")
        result["Drive Time to Supermarket"] = f"{drive_time['time']:.0f} min" if drive_time['time'] else "N/A"
    else:
        result["Walk Time to Supermarket"] = "N/A"
        result["Drive Time to Supermarket"] = "N/A"
    
    # Schools
    result["Primary School Zone"] = "TBC - Use findmyschool.vic.gov.au"
    result["Primary School Ranking"] = "TBC"
    result["Secondary School Zone"] = "TBC - Use findmyschool.vic.gov.au"
    result["Secondary School Ranking"] = "TBC"
    
    return result

def main():
    print(f"Property Enricher - {datetime.now()}")
    print("=" * 60)
    
    # Load properties
    properties = []
    with open(CSV_PATH, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            properties.append(row)
    
    print(f"Loaded {len(properties)} properties")
    
    # Get coordinates
    print(f"\nGetting coordinates...")
    target_coords = geocode_address(TARGET_ADDRESS)
    boxhill_coords = geocode_address(BOXHILL_CENTRAL)
    
    if target_coords:
        print(f"  Target: {target_coords['lat']:.4f}, {target_coords['lon']:.4f}")
    if boxhill_coords:
        print(f"  Box Hill: {boxhill_coords['lat']:.4f}, {boxhill_coords['lon']:.4f}")
    
    # Get school rankings
    print("\nFetching school rankings from BetterEducation...")
    school_rankings = get_school_rankings()
    for key, schools in school_rankings.items():
        print(f"  {key}: {len(schools)} schools")
    
    # Process all properties
    print("\n" + "=" * 60)
    print(f"Processing {len(properties)} properties...")
    
    all_results = []
    for i, prop in enumerate(properties):
        print(f"\n[{i+1}/{len(properties)}] {prop['Address']}, {prop['Suburb']}")
        result = process_property(prop, target_coords, boxhill_coords, school_rankings)
        
        if result:
            # Combine original property data with enrichment data
            combined = {
                "Address": prop.get("Address", ""),
                "Suburb": prop.get("Suburb", ""),
                "Price": prop.get("Price", ""),
                "Bedrooms": prop.get("Bedrooms", ""),
                "Bathrooms": prop.get("Bathrooms", ""),
                "Cars": prop.get("Cars", ""),
                "Land Size": prop.get("Land Size", ""),
                "Property Type": prop.get("Property Type", ""),
                "URL": prop.get("URL", ""),
            }
            # Add enrichment data
            combined.update(result)
            all_results.append(combined)
        
        time.sleep(0.5)  # Rate limiting
    
    # Save to CSV
    if all_results:
        output_path = os.path.join(os.path.dirname(__file__), "properties_enriched.csv")
        fieldnames = list(all_results[0].keys())
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_results)
        
        print(f"\n\n✅ Saved {len(all_results)} properties to: {output_path}")
    
    print("\n\nNote: Full implementation needs:")
    print("  - findmyschool.vic.gov.au for school zones")
    print("  - Manual pool/road/heritage research")
    print("  - findmyschool.vic.gov.au API for school zones")
    print("  - Manual pool/road/heritage research")

if __name__ == "__main__":
    main()
