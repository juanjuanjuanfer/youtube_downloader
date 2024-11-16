# YouTube Video Downloader
## This is a YouTube video downloader web app with Streamlit and yt-dlp.
### instalation:
  * on linux:
    
    - install ffmpeg for quality selection on videos. 
      ```bash
      sudo apt install ffmpeg
      ```
    - create your virtual environment
      ```bash
      python3 -m virtualenv .venv
      ```
    - install streamlit and yt-dlp. Do not forger to activate your environment.
        ```bash
        source .venv/bin/activate
        python3 -m pip install streamlit yt-dlp
        ```
     - or just install requirements.txt with
        ```bash
        source .venv/bin/activate
        python3 -m pip install -r requirements.txt
        ```

### usage
  To run the app use streamlit, activate your environment.
  
  ```bash
  source .venv/bin/activate
  streamlit run main.py
  ```

    
