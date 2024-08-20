import streamlit as st
import yt_dlp as youtube_dl
import os
import ssl
import certifi

# Set up the default SSL context with certifi certificates
ssl._create_default_https_context = ssl._create_unverified_context

# Function to download YouTube video
def download_video(url, resolution):
    ydl_opts = {
        'format': f'best[height<={resolution[:-1]}][ext=mp4]/best[ext=mp4]',
        'outtmpl': '%(title)s.%(ext)s',
    }
    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            download_path = ydl.prepare_filename(info_dict)
            return download_path
    except Exception as e:
        st.error(f"❌ An error occurred: {str(e)}")
        return None

# Function to download YouTube audio
def download_audio(url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': '%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
        }],
    }
    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            download_path = ydl.prepare_filename(info_dict).replace('.webm', '.mp3')
            return download_path
    except Exception as e:
        st.error(f"❌ An error occurred: {str(e)}")
        return None

# Initialize session state for user history
if 'download_history' not in st.session_state:
    st.session_state.download_history = []

# Function to add download to history
def add_to_history(url, resolution, path, media_type="video"):
    st.session_state.download_history.append({
        "url": url,
        "resolution": resolution,
        "path": path,
        "media_type": media_type
    })

# Function to display download history
def display_history():
    st.subheader("📜 Download History")
    if st.session_state.download_history:
        for entry in st.session_state.download_history:
            st.write(f"🔗 **URL:** {entry['url']}")
            st.write(f"📹 **Type:** {entry['media_type'].capitalize()}")
            if entry['media_type'] == "video":
                st.write(f"📹 **Resolution:** {entry['resolution']}")
                st.video(entry['path'])
            else:
                st.audio(entry['path'])
            st.download_button(
                label="⬇️ Download Again",
                data=open(entry['path'], "rb"),
                file_name=os.path.basename(entry['path']),
                mime="audio/mp3" if entry['media_type'] == "audio" else "video/mp4"
            )
            st.write("---")
    else:
        st.write("🚫 No downloads yet.")

# Function to clear download history
def clear_history():
    st.session_state.download_history = []
    st.success("✅ Download history cleared!")

# Streamlit app
st.sidebar.title("🚀 Navigation")
page = st.sidebar.radio("Go to", ["🎬 Downloader", "📜 History"])

if page == "🎬 Downloader":
    st.image("COVER-yt.png")
    st.title("YouTube Video Downloader")
    url = st.text_input("🔗 Enter the URL of the YouTube video:")
    media_type = st.selectbox("📹 Select the type:", ["Video", "Audio"])
    resolution = None
    if media_type == "Video":
        resolution = st.selectbox("📹 Select the resolution:", ["360p", "720p", "1080p"])
    if st.button("⬇️ Download"):
        if url:
            with st.spinner('⬇️ Downloading...'):
                if media_type == "Video":
                    download_path = download_video(url, resolution)
                else:
                    download_path = download_audio(url)
                if download_path:
                    st.success("✅ Download completed!")
                    if media_type == "Video":
                        st.video(download_path)
                    else:
                        st.audio(download_path)
                    with open(download_path, "rb") as file:
                        btn = st.download_button(
                            label="⬇️ Download File",
                            data=file,
                            file_name=os.path.basename(download_path),
                            mime="audio/mp3" if media_type == "Audio" else "video/mp4"
                        )
                    # Add download to history
                    add_to_history(url, resolution, download_path, media_type.lower())
        else:
            st.error("❌ Please enter a valid URL.")

elif page == "📜 History":
    display_history()
    if st.button("🗑️ Clear History"):
        clear_history()
