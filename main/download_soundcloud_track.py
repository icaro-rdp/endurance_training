import os

from main.utils.soundcloud import SoundCloud

soundcloud = SoundCloud(
    client_id=os.environ["SOUNDCLOUD_CLIENT_ID"],
    client_secret=os.environ["SOUNDCLOUD_CLIENT_SECRET"],
)

soundcloud.authenticate_app()

saved_file = soundcloud.download(
    "https://soundcloud.com/artist/track-name",
    "~/Downloads/track-name.mp3",
)

print(f"Saved to: {saved_file}")
