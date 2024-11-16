import streamlit as st
from yt_dlp import YoutubeDL
import os
import base64
import tempfile

def get_video_info(url):
    """Get video title and available formats."""
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
    }
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = []
            
            # Get all available formats
            for f in info['formats']:
                # Only include formats with video stream
                if f.get('vcodec') != 'none':
                    height = f.get('height', 0)
                    # Only include formats up to 1080p
                    if height and height <= 1080:
                        format_id = f['format_id']
                        resolution = f"{height}p"
                        formats.append({
                            'format_id': format_id,
                            'height': height,
                            'resolution': resolution,
                            'display': f"{resolution}"
                        })
            
            # Remove duplicates and sort by height
            unique_formats = []
            seen_resolutions = set()
            for f in sorted(formats, key=lambda x: x['height'], reverse=True):
                if f['resolution'] not in seen_resolutions:
                    unique_formats.append(f)
                    seen_resolutions.add(f['resolution'])
            
            return {
                'title': info.get('title', 'Video'),
                'formats': unique_formats
            }
    except Exception as e:
        st.error(f"Error fetching video info: {str(e)}")
        return None

def download_video(url, temp_dir, height, format_option='mp4'):
    """
    Download a video from YouTube using yt-dlp
    
    Args:
        url (str): YouTube video URL
        temp_dir (str): Temporary directory to save the video
        height (int): Desired video height (quality)
        format_option (str): Desired video format
    """
    ydl_opts = {
        # Select format based on height and include audio
        'format': f'bestvideo[height<={height}]+bestaudio/best[height<={height}]',
        'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
        'merge_output_format': format_option,
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': format_option,
        }],
        'ffmpeg_location': None,  # Let it find FFmpeg in system PATH
    }
    
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            base_filename = os.path.splitext(filename)[0]
            actual_filename = f"{base_filename}.{format_option}"
            return actual_filename if os.path.exists(actual_filename) else filename
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return None

def get_binary_file_downloader_html(file_path, file_label):
    """Generate download link for file."""
    with open(file_path, 'rb') as f:
        data = f.read()
    b64 = base64.b64encode(data).decode()
    return f'<a href="data:application/octet-stream;base64,{b64}" download="{os.path.basename(file_path)}" target="_blank">{file_label}</a>'

def main():
    st.set_page_config(page_title='YouTube Downloader', layout='centered', initial_sidebar_state='collapsed')
    st.title('YouTube Downloader')
    
    # Initialize session state
    if 'downloaded_file' not in st.session_state:
        st.session_state.downloaded_file = None
    if 'temp_dir' not in st.session_state:
        st.session_state.temp_dir = tempfile.mkdtemp()
    if 'video_info' not in st.session_state:
        st.session_state.video_info = None
    if 'done' not in st.session_state:
        st.session_state.done = False

    # Input section
    st.write('Enter a YouTube video URL to download.')
    video_url = st.text_input('YouTube Video URL')
    
    # Format selection
    format_option = st.selectbox(
        'Select output format',
        ['mp4', 'webm', 'mkv'],
        index=0
    )

    if video_url:
        # Only fetch video info if URL changes or info not already fetched
        if not st.session_state.video_info or 'current_url' not in st.session_state or st.session_state.current_url != video_url:
            with st.spinner('Fetching video information...'):
                st.session_state.video_info = get_video_info(video_url)
                st.session_state.current_url = video_url
        
        if st.session_state.video_info:
            st.write(f"Video Title: {st.session_state.video_info['title']}")
            
            # Quality selection
            if st.session_state.video_info['formats']:
                format_displays = [f['display'] for f in st.session_state.video_info['formats']]
                selected_quality = st.selectbox(
                    'Select video quality',
                    format_displays,
                    index=0  # Default to highest quality
                )
                
                # Find the selected format details
                selected_format = next(
                    f for f in st.session_state.video_info['formats'] 
                    if f['display'] == selected_quality
                )
                
                if st.button('Download Video'):
                    with st.spinner('Downloading video... Please wait...'):
                        downloaded_file = download_video(
                            video_url,
                            st.session_state.temp_dir,
                            selected_format['height'],
                            format_option
                        )
                        
                        if downloaded_file and os.path.exists(downloaded_file):
                            st.session_state.downloaded_file = downloaded_file
                            st.success('Download completed!')
                        else:
                            st.error('Download failed. Please try again.')

    # Show download link if file is ready
    if st.session_state.downloaded_file and os.path.exists(st.session_state.downloaded_file):
        st.write("---")
        st.write("Your video is ready!")
        
        file_size = os.path.getsize(st.session_state.downloaded_file) / (1024 * 1024)  # Convert to MB
        st.write(f"File size: {file_size:.1f} MB")
        
        with open(st.session_state.downloaded_file, 'rb') as file:
            st.download_button(
                label="Download Video",
                data=file,
                file_name=os.path.basename(st.session_state.downloaded_file),
                mime='video/mp4'
            )
            st.session_state.done = True
    if st.session_state.done:
        if st.button("Download another video"):
            os.remove(st.session_state.downloaded_file)
            st.session_state.done = False
            st.session_state.downloaded_file = None
            st.rerun()
if __name__ == '__main__':
    main()