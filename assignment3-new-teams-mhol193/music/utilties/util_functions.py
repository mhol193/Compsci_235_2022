def fix_broken_album_url(orig_url: str):
    start_index = orig_url.rfind("/") + 1
    _param = orig_url[start_index:]
    new_url = f'https://freemusicarchive.org/image/?file=images%2Falbums%2F{_param}&width=290&height=290&type=image'
    return new_url

def format_duration_as_time(duration: int) -> str:
    _sec = duration % 60
    _min = (duration // 60) % 60
    _hr = duration // (60*60)
    if _hr > 0:
        return f'{_hr}:{_min:02}:{_sec:02}'
    else:
        return f'{_min}:{_sec:02}'