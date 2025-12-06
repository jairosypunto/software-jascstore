from django import template
register = template.Library()

@register.filter
def youtube_id(url):
    """
    Extrae el ID de un video de YouTube desde la URL.
    Ejemplo: https://www.youtube.com/watch?v=abc123 -> abc123
    """
    import re
    if not url:
        return ""
    match = re.search(r"v=([a-zA-Z0-9_-]+)", url)
    if match:
        return match.group(1)
    match = re.search(r"youtu\.be/([a-zA-Z0-9_-]+)", url)
    if match:
        return match.group(1)
    return url