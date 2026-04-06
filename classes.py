from dataclasses import dataclass

@dataclass
class SongInfo:
    """
    A class containing info on a song / argument passed to play:
    :var srch_trm - Search term to be passed to yt-dL
    :var srch_type - Tracks if search is a url search or a ytsearch
    :var title - Song title
    :var uploader - Uploder's Channel
    :var url - url to video
    :var duration - Length of song in seconds
    :var plying_url - URL used to launch a PCM audio stream
    :var seek_to - Time in seconds to seek to
    """
    seek_to: int = 0
    start_time: datetime = None
    srch_trm: str = field(default_factory=str)
    srch_type: str = field(default_factory=str)
    title: str = field(default_factory=str)
    uploader: str = field(default_factory=str)
    url: str = field(default_factory=str)
    duration: float = field(default_factory=float)
    plying_url: str = field(default_factory=str)
    seeked: bool = False
    options: dict[str: str] = field(
        default_factory=lambda: {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                                 'options': '-vn'})

    def __str__(self):
        return f"Title: {self.title}\tUploaded by: {self.uploader}"