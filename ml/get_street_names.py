#!/usr/bin/env python3
"""
Get real street names for defects using reverse geocoding
Uses Nominatim (OpenStreetMap) - FREE but rate limited to 1 request/second
"""

import pandas as pd
import requests
import time
from pathlib import Path

def get_street_name(lat, lon):
    """Get street name from coordinates using Nominatim"""
    try:
        url = f"https://nominatim.openstreetmap.org/reverse"
        params = {
            'lat': lat,
            'lon': lon,
            'format': 'json',
            'addressdetails': 1,
            'accept-language': 'ru'  # Russian language for Bishkek
        }
        headers = {
            'User-Agent': 'RoadDoctor/1.0 (Hackathon)'
        }

        response = requests.get(url, params=params, headers=headers, timeout=10)

        if response.status_code == 200:
            data = response.json()
            address = data.get('address', {})

            # Try to get street name in priority order
            street = (
                address.get('road') or
                address.get('street') or
                address.get('pedestrian') or
                address.get('suburb') or
                address.get('neighbourhood') or
                'Unknown Street'
            )

            district = (
                address.get('suburb') or
                address.get('city_district') or
                address.get('neighbourhood') or
                'Unknown District'
            )

            print(f"✓ ({lat:.4f}, {lon:.4f}) → {street}, {district}")
            return street, district
        else:
            print(f"✗ Error {response.status_code} for ({lat}, {lon})")
            return 'Unknown Street', 'Unknown District'

    except Exception as e:
        print(f"✗ Exception for ({lat}, {lon}): {e}")
        return 'Unknown Street', 'Unknown District'

def main():
    print("🗺️  Getting street names for all defects...\n")

    # Load defects
    csv_path = Path(__file__).parent / 'output' / 'defects.csv'
    df = pd.read_csv(csv_path)

    print(f"Found {len(df)} defects\n")

    # Get unique coordinates to avoid duplicate requests
    unique_coords = df[['lat', 'lon']].drop_duplicates()
    print(f"Unique locations: {len(unique_coords)}\n")

    # Create mapping of coordinates to street names
    coord_to_street = {}

    for idx, (_, row) in enumerate(unique_coords.iterrows(), 1):
        lat, lon = row['lat'], row['lon']

        print(f"[{idx}/{len(unique_coords)}] ", end='')
        street, district = get_street_name(lat, lon)

        coord_to_street[(lat, lon)] = {
            'street': street,
            'district': district
        }

        # Respect rate limit: 1 request per second
        if idx < len(unique_coords):
            time.sleep(1.1)

    # Update dataframe with street names
    print("\n📝 Updating CSV with street names...")

    df['street_name'] = df.apply(
        lambda row: coord_to_street.get((row['lat'], row['lon']), {}).get('street', 'Unknown Street'),
        axis=1
    )

    df['district'] = df.apply(
        lambda row: coord_to_street.get((row['lat'], row['lon']), {}).get('district', 'Unknown District'),
        axis=1
    )

    # Save updated CSV
    df.to_csv(csv_path, index=False)

    print(f"✓ Updated {csv_path}")

    # Show statistics
    print("\n📊 Statistics:")
    print(f"Total defects: {len(df)}")
    print(f"Unique streets: {df['street_name'].nunique()}")
    print(f"Unique districts: {df['district'].nunique()}")

    print("\n🏆 Top streets by defect count:")
    top_streets = df['street_name'].value_counts().head(10)
    for street, count in top_streets.items():
        print(f"  {count:3d} × {street}")

    print("\n✅ Done! Refresh your browser to see street names.")

if __name__ == '__main__':
    main()
