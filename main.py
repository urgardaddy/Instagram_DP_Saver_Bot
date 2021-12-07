import json
import yt_dlp


class MyLogger:
    def debug(self, msg):
        # For compatability with youtube-dl, both debug and info are passed into debug
        # You can distinguish them by the prefix '[debug] '
        if msg.startswith('[debug] '):
            pass
        else:
            self.info(msg)

    def info(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)


# ℹ️ See the docstring of yt_dlp.postprocessor.common.PostProcessor
class MyCustomPP(yt_dlp.postprocessor.PostProcessor):
    # ℹ️ See docstring of yt_dlp.postprocessor.common.PostProcessor.run
    def run(self, info):
        self.to_screen('Doing stuff')
        return [], info


# ℹ️ See "progress_hooks" in the docstring of yt_dlp.YoutubeDL
def my_hook(d):
    if d['status'] == 'finished':
        print('Done downloading, now converting ...')


def format_selector(ctx):
    """ Select the best video and the best audio that won't result in an mkv.
    This is just an example and does not handle all cases """

    # formats are already sorted worst to best
    formats = ctx.get('formats')[::-1]

    # acodec='none' means there is no audio
    best_video = next(f for f in formats
                      if f['vcodec'] != 'none' and f['acodec'] == 'none')

    # find compatible audio extension
    audio_ext = {'mp4': 'm4a', 'webm': 'webm'}[best_video['ext']]
    # vcodec='none' means there is no video
    best_audio = next(f for f in formats if (
        f['acodec'] != 'none' and f['vcodec'] == 'none' and f['ext'] == audio_ext))

    yield {
        # These are the minimum required fields for a merged format
        'format_id': f'{best_video["format_id"]}+{best_audio["format_id"]}',
        'ext': best_video['ext'],
        'requested_formats': [best_video, best_audio],
        # Must be + seperated list of protocols
        'protocol': f'{best_video["protocol"]}+{best_audio["protocol"]}'
    }


# ℹ️ See docstring of yt_dlp.YoutubeDL for a description of the options
ydl_opts = {
    'format': format_selector,
    'postprocessors': [{
        # Embed metadata in video using ffmpeg.
        # ℹ️ See yt_dlp.postprocessor.FFmpegMetadataPP for the arguments it accepts
        'key': 'FFmpegMetadata',
        'add_chapters': True,
        'add_metadata': True,
    }],
    'logger': MyLogger(),
    'progress_hooks': [my_hook],
}


# Add custom headers
yt_dlp.utils.std_headers.update({'Referer': 'https://www.google.com'})

# ℹ️ See the public functions in yt_dlp.YoutubeDL for for other available functions.
# Eg: "ydl.download", "ydl.download_with_info_file"
with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    ydl.add_post_processor(MyCustomPP())
    info = ydl.extract_info('https://www.youtube.com/watch?v=BaW_jenozKc')

    # ℹ️ ydl.sanitize_info makes the info json-serializable
    print(json.dumps(ydl.sanitize_info(info)))
