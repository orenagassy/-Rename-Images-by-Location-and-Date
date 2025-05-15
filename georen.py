import os
import sys
import time
import piexif
import googlemaps
from PIL import Image

# Replace with your actual Google Maps API key
GOOGLE_MAPS_API_KEY = "YOUR_GOOGLE_MAPS_API_KEY"
gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)

def extract_gps_data(image_path):
    """
    Extracts GPS coordinates from the image EXIF metadata.
    """
    try:
        exif_data = piexif.load(image_path)
        gps = exif_data.get("GPS", {})
        if not gps:
            return None

        def convert_to_degrees(values):
            d, m, s = values
            return d[0]/d[1] + m[0]/m[1]/60 + s[0]/s[1]/3600

        lat = convert_to_degrees(gps[piexif.GPSIFD.GPSLatitude])
        lon = convert_to_degrees(gps[piexif.GPSIFD.GPSLongitude])
        if gps[piexif.GPSIFD.GPSLatitudeRef] != b'N':
            lat = -lat
        if gps[piexif.GPSIFD.GPSLongitudeRef] != b'E':
            lon = -lon
        return lat, lon
    except Exception as e:
        print(f"[!] Failed to extract GPS from {image_path}: {e}")
        return None

def extract_date_taken(image_path):
    """
    Extracts the original date the picture was taken from EXIF metadata.
    Returns a string in YYYY-MM-DD format or None.
    """
    try:
        exif_data = piexif.load(image_path)
        date_str = exif_data["Exif"].get(piexif.ExifIFD.DateTimeOriginal)
        if date_str:
            return date_str.decode("utf-8").split(" ")[0].replace(":", "-")
    except Exception as e:
        print(f"[!] Failed to extract date from {image_path}: {e}")
    return None

def reverse_geocode(lat, lon):
    """
    Uses Google Maps API to convert lat/lon to a human-readable address.
    """
    try:
        results = gmaps.reverse_geocode((lat, lon))
        if results:
            return results[0]['formatted_address']
    except Exception as e:
        print(f"[!] Reverse geocoding error: {e}")
    return None

def safe_filename(name):
    """
    Makes a string safe for use as a filename.
    """
    return "".join(c for c in name if c.isalnum() or c in (' ', '_', '-')).strip().replace(' ', '_')

def rename_file_with_location(image_path):
    """
    Renames a file based on GPS coordinates and date taken.
    """
    gps = extract_gps_data(image_path)
    date = extract_date_taken(image_path)
    
    if not gps:
        print(f"[!] No GPS data in: {image_path}")
        return

    location = reverse_geocode(*gps)
    if not location:
        print(f"[!] Could not get address for: {image_path}")
        return

    directory, old_name = os.path.split(image_path)
    extension = os.path.splitext(old_name)[1]

    base_name_parts = []
    if date:
        base_name_parts.append(date)
    base_name_parts.append(safe_filename(location))
    base_name = "_".join(base_name_parts)

    new_path = os.path.join(directory, f"{base_name}{extension}")
    counter = 1
    while os.path.exists(new_path):
        new_path = os.path.join(directory, f"{base_name}_{counter}{extension}")
        counter += 1

    os.rename(image_path, new_path)
    print(f"[✔] Renamed: {old_name} → {os.path.basename(new_path)}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python rename_by_location.py <image_or_directory>")
        return

    path = sys.argv[1]
    if os.path.isdir(path):
        for filename in os.listdir(path):
            if filename.lower().endswith(".jpg"):
                full_path = os.path.join(path, filename)
                rename_file_with_location(full_path)
                time.sleep(1)  # avoid hitting API too fast
    elif os.path.isfile(path) and path.lower().endswith(".jpg"):
        rename_file_with_location(path)
    else:
        print("[!] Invalid file or directory")

if __name__ == "__main__":
    main()
