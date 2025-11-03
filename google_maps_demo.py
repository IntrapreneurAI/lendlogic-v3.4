#!/usr/bin/env python3.11
"""
Google Maps Geocoding API Demo for LendLogic v3.4
Validates borrower and vendor addresses
"""

import requests
import json
import os
from datetime import datetime

# Sample addresses from our test deal
BORROWER_ADDRESS = "1234 Industrial Parkway, Chicago, IL 60601"
BORROWER_NAME = "Midwest Freight Solutions LLC"
VENDOR_ADDRESS = "5678 Highway 41, Hammond, IN 46320"
VENDOR_NAME = "Midwest Truck Sales"

def geocode_address(address, business_name=None):
    """
    Use Google Maps Geocoding API to validate an address.
    Returns structured data including coordinates, place type, and confidence.
    """
    
    # Check if API key is available
    api_key = os.environ.get('GOOGLE_MAPS_API_KEY')
    
    if not api_key:
        print("⚠️  No GOOGLE_MAPS_API_KEY found in environment variables")
        print("    Using simulated data for demonstration purposes\n")
        return simulate_geocoding(address, business_name)
    
    # Make API call
    base_url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        'address': address,
        'key': api_key
    }
    
    try:
        response = requests.get(base_url, params=params)
        data = response.json()
        
        if data['status'] == 'OK' and len(data['results']) > 0:
            result = data['results'][0]
            
            # Extract key information
            formatted_address = result['formatted_address']
            location = result['geometry']['location']
            lat = location['lat']
            lng = location['lng']
            location_type = result['geometry']['location_type']
            
            # Determine place type
            place_types = result.get('types', [])
            place_type = determine_place_type(place_types)
            
            # Calculate confidence score
            confidence = calculate_confidence(location_type, place_types)
            
            # Generate Google Maps link
            maps_link = f"https://maps.google.com/?q={lat},{lng}"
            
            return {
                'found': True,
                'formatted_address': formatted_address,
                'latitude': lat,
                'longitude': lng,
                'place_type': place_type,
                'confidence': confidence,
                'maps_link': maps_link,
                'raw_types': place_types
            }
        else:
            return {
                'found': False,
                'error': data.get('status', 'Unknown error')
            }
            
    except Exception as e:
        return {
            'found': False,
            'error': str(e)
        }

def simulate_geocoding(address, business_name):
    """Simulate geocoding results for demonstration when no API key is available."""
    
    if "Chicago" in address:
        return {
            'found': True,
            'formatted_address': '1234 Industrial Pkwy, Chicago, IL 60601, USA',
            'latitude': 41.8781,
            'longitude': -87.6298,
            'place_type': 'Commercial',
            'confidence': 95,
            'maps_link': 'https://maps.google.com/?q=41.8781,-87.6298',
            'raw_types': ['street_address', 'premise'],
            'simulated': True
        }
    elif "Hammond" in address:
        return {
            'found': True,
            'formatted_address': '5678 US-41, Hammond, IN 46320, USA',
            'latitude': 41.5834,
            'longitude': -87.4967,
            'place_type': 'Industrial',
            'confidence': 100,
            'maps_link': 'https://maps.google.com/?q=41.5834,-87.4967',
            'raw_types': ['premise', 'point_of_interest'],
            'simulated': True
        }
    else:
        return {
            'found': False,
            'error': 'Address not found in simulation',
            'simulated': True
        }

def determine_place_type(types):
    """Determine if location is commercial, industrial, residential, etc."""
    
    if any(t in types for t in ['point_of_interest', 'establishment', 'store']):
        return 'Commercial'
    elif any(t in types for t in ['industrial', 'warehouse']):
        return 'Industrial'
    elif 'street_address' in types:
        return 'Commercial'
    elif 'premise' in types:
        return 'Commercial'
    else:
        return 'Unknown'

def calculate_confidence(location_type, types):
    """Calculate match confidence score based on geocoding result quality."""
    
    if location_type == 'ROOFTOP':
        return 100
    elif location_type == 'RANGE_INTERPOLATED':
        return 90
    elif location_type == 'GEOMETRIC_CENTER':
        return 75
    elif 'premise' in types or 'street_address' in types:
        return 85
    else:
        return 60

def format_output(entity_name, entity_type, result):
    """Format the geocoding result in a user-friendly way."""
    
    if not result['found']:
        return f"""
**{entity_type}:** {entity_name}
⚠️ Couldn't confidently match this address. Might need manual confirmation.
Error: {result.get('error', 'Unknown')}
"""
    
    lat = result['latitude']
    lng = result['longitude']
    lat_dir = 'N' if lat >= 0 else 'S'
    lng_dir = 'E' if lng >= 0 else 'W'
    
    confidence_emoji = '✅' if result['confidence'] >= 85 else '⚠️'
    
    output = f"""
**{entity_type}:** [{entity_name}]({result['maps_link']})
{confidence_emoji} Found it. Location is {result['place_type']}. Verified at {result['confidence']}% confidence.
📍 {abs(lat):.4f}° {lat_dir}, {abs(lng):.4f}° {lng_dir}
🔗 [View on Google Maps]({result['maps_link']})
"""
    
    if result.get('simulated'):
        output += "ℹ️  (Simulated data - no API key provided)\n"
    
    return output

def create_supabase_payload(borrower_result, vendor_result, deal_id):
    """Create JSON payload for Supabase logging."""
    
    return {
        'deal_id': deal_id,
        'borrower_validation': {
            'found': borrower_result['found'],
            'formatted_address': borrower_result.get('formatted_address'),
            'latitude': borrower_result.get('latitude'),
            'longitude': borrower_result.get('longitude'),
            'place_type': borrower_result.get('place_type'),
            'confidence': borrower_result.get('confidence'),
            'maps_link': borrower_result.get('maps_link')
        },
        'vendor_validation': {
            'found': vendor_result['found'],
            'formatted_address': vendor_result.get('formatted_address'),
            'latitude': vendor_result.get('latitude'),
            'longitude': vendor_result.get('longitude'),
            'place_type': vendor_result.get('place_type'),
            'confidence': vendor_result.get('confidence'),
            'maps_link': vendor_result.get('maps_link')
        },
        'validation_timestamp': datetime.utcnow().isoformat() + 'Z'
    }

def main():
    print("=" * 70)
    print("GOOGLE MAPS ADDRESS VALIDATION - LendLogic v3.4")
    print("=" * 70)
    print()
    
    # Validate borrower address
    print("🔍 Validating borrower address...")
    borrower_result = geocode_address(BORROWER_ADDRESS, BORROWER_NAME)
    
    # Validate vendor address
    print("🔍 Validating vendor address...")
    vendor_result = geocode_address(VENDOR_ADDRESS, VENDOR_NAME)
    
    print()
    print("=" * 70)
    print("VALIDATION RESULTS")
    print("=" * 70)
    
    print(format_output(BORROWER_NAME, "Borrower", borrower_result))
    print(format_output(VENDOR_NAME, "Vendor", vendor_result))
    
    # Create Supabase payload
    print()
    print("=" * 70)
    print("SUPABASE LOGGING PAYLOAD")
    print("=" * 70)
    print()
    
    payload = create_supabase_payload(borrower_result, vendor_result, "DEAL-2025-001")
    print(json.dumps(payload, indent=2))
    
    # Save to file
    output_file = "/home/ubuntu/lendlogic-v3.4/google_maps_validation_result.json"
    with open(output_file, 'w') as f:
        json.dump(payload, f, indent=2)
    
    print()
    print(f"✅ Results saved to: {output_file}")

if __name__ == "__main__":
    main()
