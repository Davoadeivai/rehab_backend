import os
import requests
from pathlib import Path

# Create backgrounds directory if it doesn't exist
backgrounds_dir = Path("static/img/backgrounds")
backgrounds_dir.mkdir(parents=True, exist_ok=True)

# List of background images to download (using free-to-use medical images from Pexels)
backgrounds = {
    # Default backgrounds
    "default-bg.jpg": "https://images.pexels.com/photos/4577653/pexels-photo-4577653.jpeg?auto=compress&cs=tinysrgb&w=1920",
    "light-bg.jpg": "https://images.pexels.com/photos/45842/clasping-hands-comfort-hands-people-45842.jpeg?auto=compress&cs=tinysrgb&w=1920",
    
    # Authentication
    "login-bg.jpg": "https://images.pexels.com/photos/5215024/pexels-photo-5215024.jpeg?auto=compress&cs=tinysrgb&w=1920",
    "register-bg.jpg": "https://images.pexels.com/photos/5215025/pexels-photo-5215025.jpeg?auto=compress&cs=tinysrgb&w=1920",
    
    # Patient related
    "patient-bg.jpg": "https://images.pexels.com/photos/3985163/pexels-photo-3985163.jpeg?auto=compress&cs=tinysrgb&w=1920",
    "patient-detail-bg.jpg": "https://images.pexels.com/photos/4033148/pexels-photo-4033148.jpeg?auto=compress&cs=tinysrgb&w=1920",
    "patient-form-bg.jpg": "https://images.pexels.com/photos/4033148/pexels-photo-4033148.jpeg?auto=compress&cs=tinysrgb&w=1920",
    
    # Prescription related
    "prescription-bg.jpg": "https://images.pexels.com/photos/3985163/pexels-photo-3985163.jpeg?auto=compress&cs=tinysrgb&w=1920",
    "prescription-detail-bg.jpg": "https://images.pexels.com/photos/4033148/pexels-photo-4033148.jpeg?auto=compress&cs=tinysrgb&w=1920",
    "prescription-form-bg.jpg": "https://images.pexels.com/photos/4033148/pexels-photo-4033148.jpeg?auto=compress&cs=tinysrgb&w=1920",
    
    # Appointment related
    "appointment-bg.jpg": "https://images.pexels.com/photos/4033148/pexels-photo-4033148.jpeg?auto=compress&cs=tinysrgb&w=1920",
    "calendar-bg.jpg": "https://images.pexels.com/photos/4033148/pexels-photo-4033148.jpeg?auto=compress&cs=tinysrgb&w=1920",
    
    # Reports
    "report-bg.jpg": "https://images.pexels.com/photos/5905445/pexels-photo-5905445.jpeg?auto=compress&cs=tinysrgb&w=1920",
    "financial-bg.jpg": "https://images.pexels.com/photos/5905445/pexels-photo-5905445.jpeg?auto=compress&cs=tinysrgb&w=1920",
    
    # Inventory
    "inventory-bg.jpg": "https://images.pexels.com/photos/3985163/pexels-photo-3985163.jpeg?auto=compress&cs=tinysrgb&w=1920",
    "medication-bg.jpg": "https://images.pexels.com/photos/4033148/pexels-photo-4033148.jpeg?auto=compress&cs=tinysrgb&w=1920",
    
    # User related
    "profile-bg.jpg": "https://images.pexels.com/photos/4033148/pexels-photo-4033148.jpeg?auto=compress&cs=tinysrgb&w=1920",
    "settings-bg.jpg": "https://images.pexels.com/photos/4033148/pexels-photo-4033148.jpeg?auto=compress&cs=tinysrgb&w=1920",
    
    # Support
    "contact-bg.jpg": "https://images.pexels.com/photos/4033148/pexels-photo-4033148.jpeg?auto=compress&cs=tinysrgb&w=1920",
    "support-bg.jpg": "https://images.pexels.com/photos/4033148/pexels-photo-4033148.jpeg?auto=compress&cs=tinysrgb&w=1920",
    "faq-bg.jpg": "https://images.pexels.com/photos/4033148/pexels-photo-4033148.jpeg?auto=compress&cs=tinysrgb&w=1920"
}

def download_image(url, filename):
    """Download an image from a URL and save it to the backgrounds directory."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded {filename}")
        return True
    except Exception as e:
        print(f"Error downloading {filename}: {e}")
        # If there's an error, use a default image
        default_image = backgrounds_dir / "default-bg.jpg"
        if default_image.exists():
            import shutil
            shutil.copy2(default_image, filename)
            print(f"Copied default image to {filename}")
            return True
        return False

def main():
    print("Starting background image download...")
    
    # Download each background image
    for filename, url in backgrounds.items():
        filepath = backgrounds_dir / filename
        if not filepath.exists():
            print(f"Downloading {filename}...")
            download_image(url, filepath)
        else:
            print(f"{filename} already exists, skipping...")
    
    print("\nBackground images download complete!")
    print(f"Images saved to: {backgrounds_dir.absolute()}")

if __name__ == "__main__":
    main()
