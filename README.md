# 📸 Rename Images by Location and Date

A Python script that renames `.jpg` image files based on their **GPS coordinates** and **date taken**, using the **Google Maps Geocoding API** to determine the location.

---

## ✨ Features

- Extracts **GPS coordinates** from EXIF data.
- Reverse geocodes using **Google Maps API**.
- Adds **date the picture was taken** to the filename.
- Automatically renames the file to:  
  `YYYY-MM-DD_Location_Name.jpg`
- Handles **single images** or **entire folders**.
- Skips files without GPS data gracefully.

---

## 🧰 Requirements

Install dependencies with:

```bash
pip install pillow piexif googlemaps
