'''
SiriusXM to USB drive
Grab an XM playlist, find the songs on youtube, pull them local
Uses:
    - https://xmplaylist.com/api/documentation
    - https://music.youtube.com/search?q=

Requirements:
    - yt-dlp
    - ytmusicapi
    - colorlog
    - colorama

Channels
siriusxmhits1
'''

from datetime import datetime
from pathlib import Path
from utils.arg_parser import parse_args
from utils.logging_config import setup_logging, get_logger
from ytmusicapi import YTMusic
import yt_dlp
import json
import os
import sys
import requests
from multiprocessing import Pool, cpu_count



# Get the module logger
logger = get_logger(__name__)

def get_xm_stations() -> dict:
    """
    Fetches the list of available stations from XM Playlist API.
    
    Returns:
        dict: JSON response containing station information
    
    Raises:
        requests.RequestException: If the API request fails
    """
    url = 'https://xmplaylist.com/api/station'
    headers = {
        'accept': 'application/json'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx, 5xx)
        data = response.json()
        
        # Ensure we have the expected data structure
        if not isinstance(data, dict) or 'results' not in data:
            logger.error("Unexpected API response format")
            return None
            
        return data
    except requests.RequestException as e:
        logger.error(f"Failed to fetch XM stations: {e}")
        return None

def save_stations_to_file(stations: dict, filename: str = "json/stations.json") -> bool:
    """
    Saves the station information to a JSON file.
    
    Args:
        stations: Dictionary containing station information
        filename: Name of the file to save to (default: json/stations.json)
    
    Returns:
        bool: True if successful, False otherwise
    """
    if not stations:
        logger.error("No station data to save")
        return False
    
    try:
        # Ensure the json directory exists
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        # Write the data with nice formatting
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(stations, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Successfully saved station data to {filename}")
        return True
    
    except Exception as e:
        logger.error(f"Failed to save stations to file: {e}")
        return False

def update_stations():
    """Updates the local stations file with fresh data from the API."""
    stations = get_xm_stations()
    if stations:
        save_stations_to_file(stations)

def get_sorted_channels(json_file_path='json/stations.json'):
    """
    Reads a JSON file, extracts the 'deeplink' values from the 'results' list,
    and returns them in a formatted multi-column string.

    Args:
        json_file_path (str): The path to the JSON file.

    Returns:
        str: A formatted multi-column string of channel names, or empty string if error occurs.
    """
    try:
        with open(json_file_path, 'r') as file:
            data = json.load(file)

        channels = sorted(item['deeplink'] for item in data.get('results', []))
        
        # Format channels in columns
        col_width = max(len(channel) for channel in channels) + 2  # Add 2 for spacing
        term_width = os.get_terminal_size().columns
        num_cols = max(1, term_width // col_width)
        
        # Create the formatted output
        output = []
        for i in range(0, len(channels), num_cols):
            row = channels[i:i + num_cols]
            output.append(''.join(channel.ljust(col_width) for channel in row))
        
        return '\n'.join(output)

    except FileNotFoundError:
        return "Error: File not found at {json_file_path}"
    except json.JSONDecodeError:
        return "Error: Invalid JSON format in {json_file_path}"
    except KeyError:
        return "Error: JSON structure is incorrect in {json_file_path}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"


def process_track_records(json_data):
    """
    Processes track records from a JSON object and returns "artist - title" strings.

    Args:
        json_data: A JSON object (dict or list) containing track information.

    Returns:
        A list of strings, where each string is in the format "artist - title".
        Returns an empty list if no track records are found or the input is invalid.
    """

    track_records = []

    def extract_tracks(data) -> list[str]:
        if isinstance(data, dict):
            # Check for both "track" and "tracks" keys to handle different JSON structures
            tracks_to_process = []
            if "track" in data and isinstance(data["track"], dict):
                tracks_to_process = [data["track"]] # Handle single track object
            elif "tracks" in data and isinstance(data["tracks"], list):
                tracks_to_process = data["tracks"] # Handle list of tracks

            for track in tracks_to_process:
                if isinstance(track, dict) and "artists" in track and "title" in track:
                    artists = track["artists"]
                    if isinstance(artists, list):
                        artist_names = [artist if isinstance(artist, str) else artist.get("name") for artist in artists if isinstance(artist, (str, dict)) and (isinstance(artist, str) or artist.get("name"))]
                        if artist_names:  # Check if artist names were extracted
                            artist_string = ", ".join(artist_names)
                            title = track.get("title")
                            if title:  # Check if the title exists
                                track_records.append(f"{artist_string} - {title}")

            # Recursively search nested dictionaries and lists
            for value in data.values():
                extract_tracks(value)

        elif isinstance(data, list):
            for item in data:
                extract_tracks(item)  # Recursively search nested dictionaries and lists


    try:
        # Attempt to load the JSON if it's a string, otherwise assume it's already a dict/list
        if isinstance(json_data, str):
            data = json.loads(json_data)
        else:
            data = json_data

        extract_tracks(data)  # Start the recursive extraction

    except (json.JSONDecodeError, TypeError):  # Handle JSON decoding or type errors
        return []

    return track_records

def process_track_records_from_file(filepath) -> list[str]:
    """
    Processes track records from a JSON file.

    Args:
        filepath: The path to the JSON file.

    Returns:
        A list of strings, where each string is in the format "artist - title".
        Returns an empty list if the file cannot be opened, read, or if the JSON is invalid.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:  # Handle potential encoding issues
            json_data = json.load(f)
            return process_track_records(json_data)
    except (FileNotFoundError, json.JSONDecodeError, OSError) as e:  # Catch file errors
        logger.error(f"Error processing file {filepath}: {e}") 
        return []

def find_song_on_youtube(artist: str, title:str ) -> str:
    """
    Takes in a track string with artist - track

    Args:
        track: The track name in the format artsts - track

    Returns:
        Top result on ytmusic

    search_url = 'https://music.youtube.com/search?q='

    """
    ytmusic = YTMusic()
    search_param = f'{artist} - {title}'
    search_results = ytmusic.search(search_param, limit=1, filter="songs")
    # data = json.loads(search_results)
    for item in search_results:
        # if isinstance(item, dict) and item.get("category") == "Top result" and item.get("resultType") == "video":
        if isinstance(item, dict) and item.get("category") == "Songs" and item.get("videoId") != None:
            # logger.info(f'Item: {item}')
            vid = item.get("videoId")
            url = f'https://music.youtube.com/watch?v={vid}'
            return url
        else:
            logger.error(f'Error finding song on youtube:')
            logger.info(search_results)

def download_worker(task):
    """Worker function that creates a new YoutubeDL instance per process"""
    # Set up logging for the worker process
    from utils.logging_config import setup_logging
    setup_logging()
    logger = get_logger(__name__)
    
    url, filename, quality, output_folder, download = task
    ydl_opts = {
        'quiet': True,
        'writethumbnail': True,
        'progress': True,
        'outtmpl': f'{output_folder}/{filename}',
        'format': 'bestaudio/best',
        'postprocessors': [
            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': quality,
            },
            {'key': 'EmbedThumbnail'},
            {'key': 'FFmpegMetadata'},
        ],
    }
    if download:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            logger.info(f'Downloading: {url} to {filename}')
            ydl.download([url])
    else:
        logger.info(f'DRY RUN: Would download: {url} to {filename}')

def getChannelJson(channel: str) -> str:
    """
    Gets the JSON data for a channel, either from local file or API if local doesn't exist.
    
    Args:
        channel: The channel name/id to get JSON for
        
    Returns:
        str: Path to the JSON file
    """
    jsonfilepath = f'json/{channel}.json'
    
    # If file doesn't exist, fetch from API and save
    if not os.path.exists(jsonfilepath):
        # Create json directory if it doesn't exist
        os.makedirs('json', exist_ok=True)
        
        # Fetch from API
        url = f'https://xmplaylist.com/api/station/{channel}/most-heard?days=30'
        headers = {'accept': 'application/json'}
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            # Save the JSON response to file
            with open(jsonfilepath, 'w', encoding='utf-8') as f:
                json.dump(response.json(), f, indent=2)
            logger.info(f"Successfully fetched and saved JSON for channel {channel}")
        except requests.RequestException as e:
            logger.error(f"Failed to fetch JSON for channel {channel}: {e}")
            return None
    
    return jsonfilepath

def download_a_channel(channel):
    track_list = process_track_records_from_file(getChannelJson(channel))
    dst_folder=f'sirius-{channel}'
    logger.info(f'Downloading {len(track_list)} tracks to {dst_folder}')
    
    with Pool(processes=cpu_count()) as pool:
        # Process tracks and submit downloads immediately
        for track in track_list:
            logger.info(f'working on track: {track}')
            track_sanitize = track.replace('/', '-').replace('\\', '-')
            if not os.path.exists(f'{dst_folder}/{track_sanitize}.mp3'):
                a, t = track.split(' - ', 1)
                u = find_song_on_youtube(a,t)
                if u:
                    # Submit download task immediately
                    pool.apply_async(download_worker, [(u, track_sanitize, '192', dst_folder, args.download)])
                else:
                    logger.error(f'ERROR: SONG NOT FOUND')
            else:
                logger.warning(f'File already exist: {track}.mp3')
        
        # Wait for all downloads to complete
        pool.close()
        pool.join()

def main() -> int:
    """Setup Logging, Process the args, and run the program"""

    # Setup logging
    log_file = args.log_file or Path(f"logs/app_{datetime.now():%Y%m%d_%H%M%S}.log")
    setup_logging(log_file, args.debug)

    try:
        logger.info("Starting siriusxm2usb...")
        if args.debug:
            logger.debug("Debug mode enabled")
        logger.info("Updating station data")
        update_stations()
        for channel in args.channel:
            try:
                download_a_channel(channel=channel)
            except Exception as e:
                logger.critical(f"Check your channel name: {channel}\nAvailable channels:\n{get_sorted_channels()}")
                # logger.exception(f"An error occurred: {e}")
        return 0
    except Exception as e:
        logger.exception(f"An error occurred: {e}")
        return 1

if __name__ == "__main__":
    args = parse_args()
    sys.exit(main())
