from googleapiclient.discovery import build
import pandas as pd
import time
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer

USERNAME = "NeuralNine"  # YouTube handle (@NeuralNine)

# Initialize YouTube API client
youtube = build("youtube", "v3", developerKey="AIzaSyABWmJr0pv7Uscn3JeixRudl_b1WPTdBIY")

# Function to get the channel ID from username
def get_channel_id(username):
    request = youtube.search().list(
        part="id",
        q=username,
        type="channel",
        maxResults=1
    )
    response = request.execute()

    if "items" in response and response["items"]:
        return response["items"][0]["id"]["channelId"]
    return None

# Function to get the uploads playlist ID
def get_uploads_playlist_id(channel_id):
    request = youtube.channels().list(
        part="contentDetails",
        id=channel_id
    )
    response = request.execute()

    if "items" in response and response["items"]:
        return response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    return None

# Function to get all video IDs from the uploads playlist
def get_all_video_ids(playlist_id):
    video_ids = []
    next_page_token = None

    while True:
        request = youtube.playlistItems().list(
            part="contentDetails",
            playlistId=playlist_id,
            maxResults=50,  # Max results per API request
            pageToken=next_page_token
        )
        response = request.execute()

        for item in response.get("items", []):
            video_ids.append(item["contentDetails"]["videoId"])

        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break  # No more pages

        time.sleep(1)  # Avoid hitting API limits

    return video_ids

# Function to get video details (title, views, likes, published date, thumbnail)
def get_video_details(video_ids):
    videos_data = []
    for i in range(0, len(video_ids), 50):  # API allows max 50 videos per request
        request = youtube.videos().list(
            part="snippet,statistics",
            id=",".join(video_ids[i:i+50])
        )
        response = request.execute()

        for item in response.get("items", []):
            videos_data.append({
                "Video ID": item["id"],
                "Title": item["snippet"]["title"],
                "Views": item["statistics"].get("viewCount", "N/A"),
                "Likes": item["statistics"].get("likeCount", "N/A"),
                "Comments": item["statistics"].get("commentCount", "N/A"),
                "Published At": item["snippet"]["publishedAt"],
                "Thumbnail URL": item["snippet"]["thumbnails"]["high"]["url"]  # Get high-resolution thumbnail
            })

        time.sleep(1)  # Avoid hitting API limits

    return videos_data

def fetch_comments(video_id):
    comments = []
    next_page_token = None

    while True:
        request = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=100,
            pageToken=next_page_token
        )
        response = request.execute()

        for item in response['items']:
            comment = item['snippet']['topLevelComment']['snippet']
            comments.append([
                comment['authorDisplayName'],
                pd.to_datetime(comment['publishedAt']).strftime("%Y-%m-%d %H:%M:%S"),  # Convert format
                pd.to_datetime(comment['updatedAt']).strftime("%Y-%m-%d %H:%M:%S"),
                comment['likeCount'],
                comment['textDisplay']
            ])

        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break  # No more pages

    # Create DataFrame
    return pd.DataFrame(comments, columns=['author', 'published_at', 'updated_at', 'like_count', 'text'])



# Load the comments CSV

# Function to analyze sentiment
def analyze_sentiment(comment):
    nltk.download('vader_lexicon')
    sia = SentimentIntensityAnalyzer()
    score = sia.polarity_scores(comment)["compound"]
    if score >= 0.05:
        return "Positive", score
    elif score <= -0.05:
        return "Negative", score
    else:
        return "Neutral", score

# Apply sentiment analysis


