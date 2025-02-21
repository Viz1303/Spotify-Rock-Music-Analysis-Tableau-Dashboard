import requests
import pandas as pd
import base64
import time

# API Credentials
CLIENT_ID = "4325ca8d218b49be85c62cb04e7896bc"
CLIENT_SECRET = "33792a37d4c14175ba9f2889fa026de0"

# Step 1: Fetch Access Token
def get_access_token():
    print("Fetching Access Token...")
    auth_string = f"{CLIENT_ID}:{CLIENT_SECRET}"
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = base64.b64encode(auth_bytes).decode("utf-8")
    
    token_url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": f"Basic {auth_base64}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    
    response = requests.post(token_url, headers=headers, data=data)
    if response.status_code == 200:
        print("✅ Access Token received!")
        return response.json()["access_token"]
    else:
        print("❌ Error fetching token:", response.json())
        exit()

access_token = get_access_token()
headers = {"Authorization": f"Bearer {access_token}"}

# Step 2: Get Popular Rock Tracks (Post-2000)
def get_rock_tracks(limit=1000):
    print("Fetching popular rock tracks (2000-present)...")
    tracks = []
    offset = 0
    batch_size = 50  # Maximum per request
    
    while len(tracks) < limit:
        query = "genre:rock year:2000-2025"
        search_url = f"https://api.spotify.com/v1/search?q={query}&type=track&limit={batch_size}&offset={offset}"
        response = requests.get(search_url, headers=headers)
        
        if response.status_code != 200:
            print("❌ Error fetching rock tracks:", response.json())
            break
        
        new_tracks = response.json().get("tracks", {}).get("items", [])
        if not new_tracks:
            break  # Stop if no more results
        
        tracks.extend(new_tracks)
        offset += batch_size
        print(f"✅ Retrieved {len(tracks)} tracks so far...")
        time.sleep(1)  # Avoid rate limiting
    
    print(f"✅ Final track count: {len(tracks)}")
    return tracks

rock_tracks = get_rock_tracks()

tracks = []
for idx, track in enumerate(rock_tracks, start=1):
    track_id = track["id"]
    album = track["album"]
    
    print(f"Fetching details for track {idx}/{len(rock_tracks)}: {track['name']}...")
    track_details_url = f"https://api.spotify.com/v1/tracks/{track_id}"
    track_details = requests.get(track_details_url, headers=headers).json()
    
    tracks.append({
        "Track Name": track["name"],
        "Artist(s)": ", ".join([artist["name"] for artist in track["artists"]]),
        "Album Name": album["name"],
        "Release Date": album["release_date"],
        "Track ID": track_id,
        "Duration (ms)": track["duration_ms"],
        "Popularity": track_details.get("popularity", "N/A"),
        "Spotify URL": track["external_urls"]["spotify"]
    })
    
    time.sleep(0.5)  # Avoid rate limiting
    print(f"✅ Track {idx} processed successfully!")

# Convert to DataFrame
df_tracks = pd.DataFrame(tracks)
df_tracks["Release Date"] = pd.to_datetime(df_tracks["Release Date"], errors='coerce')

# Step 3: Save Data to Excel
print("Saving data to Excel...")
with pd.ExcelWriter("spotify_rock_tracks.xlsx") as writer:
    df_tracks.to_excel(writer, sheet_name="Tracks", index=False)

print("✅ Data saved as 'spotify_rock_tracks.xlsx'")
