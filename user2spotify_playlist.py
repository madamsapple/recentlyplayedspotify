# -*- coding: utf-8 -*-
"""user2spotify_playlist.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/12Jc6V33eZbdjR_Zt25iNFe66D1sWHaEy
"""



! pip install virtualenv

! virtualenv spotipy_virtlenv

! source spotipy_virtlenv/bin/activate

! pip install spotipy --upgrade

! pip install --upgrade pip

! pip install python-dotenv

# "r" - Read - Default value. Opens a file for reading, error if the file does not exist

# "a" - Append - Opens a file for appending, creates the file if it does not exist

# "w" - Write - Opens a file for writing, creates the file if it does not exist

# "x" - Create - Creates the specified file, returns an error if the file exist
with open("/content/.env", "w") as f:
    f.write("SPOTIFY_CLIENT_ID=943aade6234e4b098918872c419eee59\n")
    f.write("SPOTIFY_CLIENT_SECRET=6f1ee44eb51d45ccbc9439f7dbe50ec4\n")

!ls /content

import os
import requests
import base64
import json
from dotenv import load_dotenv
from urllib.parse import urlencode

# Load credentials from .env file
load_dotenv()

# Access credentials
client_id = os.getenv("SPOTIFY_CLIENT_ID")
client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")

redirect_uri = "https://www.example.com"  # Redirect URI you set in the Spotify Developer Dashboard

# Define the scopes you need
scopes = "user-read-recently-played"  # Example scopes for user data

# Function to get authorization URL
def get_authorization_url():
    auth_url = "https://accounts.spotify.com/authorize?" + urlencode({
        "client_id": client_id,
        "response_type": "code",
        "redirect_uri": redirect_uri,
        "scope": scopes
    })
    return auth_url

# Print authorization URL to get the code (user will log in and authorize)
print("Go to this URL to authorize the app:")
print(get_authorization_url())

# After user logs in, Spotify will redirect to redirect_uri with a code in the URL
# This code is obtained from the URL and passed to the next function

# Function to exchange the authorization code for an access token
def get_token(auth_code):
    url = "https://accounts.spotify.com/api/token"

    # Encode client credentials for Basic Authorization
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {
        "grant_type": "authorization_code",
        "code": auth_code,
        "redirect_uri": redirect_uri
    }

    result = requests.post(url, headers=headers, data=data)

    # Convert the resulting JSON string data containing the access token
    json_result = json.loads(result.content)

    # Extract the token
    token = json_result.get("access_token")
    return token

# Get the token after the user provides the authorization code
auth_code = input("Enter the authorization code from the URL: ")
token = get_token(auth_code)
print("Access Token:", token)

print()

#getting all recently played 50 tracks
recplayed_url = "https://api.spotify.com/v1/me/player/recently-played?limit=50"

# Define headers with the Authorization token
headers = {
    "Authorization": f"Bearer {token}"
}

print(headers)

result = requests.get(recplayed_url, headers=headers)
json_result = json.loads(result.content)

print(result)
print(json_result)

import csv

# Your JSON data (shortened for clarity)
data = json_result

# Specify CSV file name
csv_file = "spotify_tracks_nh.csv"

# Open CSV file for writing
with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=["Track Name", "Artist", "Album Name", "Release Date", "Track URL", "Album URL", "Played At"])
    writer.writeheader()

    # Loop through the JSON data and write each entry
    for item in data["items"]:
        track_info = item["track"]
        artist_name = track_info["artists"][0]["name"]
        album_name = track_info["album"]["name"]
        release_date = track_info["album"]["release_date"]
        track_url = track_info["external_urls"]["spotify"]
        album_url = track_info["album"]["external_urls"]["spotify"]
        played_at = item["played_at"]

        writer.writerow({
            "Track Name": track_info["name"],
            "Artist": artist_name,
            "Album Name": album_name,
            "Release Date": release_date,
            "Track URL": track_url,
            "Album URL": album_url,
            "Played At": played_at
        })

print("CSV file created successfully!")

#getting track name and id from the first result as an example/test

id = json_result["items"][0]['track']['id']
name = json_result["items"][0]['track']['name']

print("Track Title: " + name + ",  Track ID: " + id)

#Let's get the IDs of all 50 tracks. These IDs will help us fetch the audio
#features of them all.
#I first printed the IDs to test if it's working and see how it looks, and then I decided to create
#a dictionary which would store keys as int indices and values as IDs.

#I chose a dictionary to store the values so that I could conveniently add them to my url using
#string formatting. This smoothly automates the action of adding the IDs as queries to my url,
#while doing an audio feature request.

index = 0
IDs = {}

for x in json_result['items']:
    print(x['track']['id'])

    #starting from 0, add each increasing index and its corrresponding ID string to the dictionary
    IDs.update({index: x['track']['id']})
    index += 1


#print the ID dictionary
print(IDs)

features_url = "https://api.spotify.com/v1/audio-features?ids="

#adding all the IDs to the url for the request
for x in IDs:

    #if it is the last item
    #don't add the comma and just exit the loop
    if x == 49:
        features_url += IDs[x]
        break

    #realised we needed commas instead of %
    features_url += IDs[x] + ','



print(features_url)

#making request for audio features of all our top 50 tracks
ft_results = requests.get(features_url, headers = headers)
features = json.loads(ft_results.content)

#print(features)
# print(features['audio_features'])
# print(x)

for x in features['audio_features']:
    print(x)

# Parse the JSON response ft_results
if ft_results.status_code == 200:
    features_data = ft_results.json()  # Extract audio features data
else:
    print(f"Failed to fetch features: {ft_results.status_code}, {ft_results.text}")
    exit()

# Print each track's title with its corresponding features
for idx, item in enumerate(json_result['items']):
    title = item['track']['name']
    features = features_data['audio_features'][idx]

    # Print the title and its features
    print(f"Title: {title}")
    for feature, value in features.items():
        print(f"  {feature}: {value}")
    print()



# key
# integer
# The key the track is in. Integers map to pitches using standard Pitch Class notation. E.g. 0 = C, 1 = C♯/D♭, 2 = D, and so on. If no key was detected, the value is -1.

# Range: -1 - 11
# Example: 9

keys = []
for x in features_data['audio_features']:
    #print(x['key'])
    keys.append(x['key'])

for x in range(50):
    print("Track Title: " + json_result["items"][x]['track']['name'] + ", Key: " + str(keys[x]))

print(keys)

# Calculate the average of the keys
if keys:  # Ensure the list isn't empty to avoid division by zero
    average_key = sum(keys) / len(keys)
    print(f"\nAverage Key Value: {average_key:.2f}")
else:
    print("\nNo keys available to calculate an average.")