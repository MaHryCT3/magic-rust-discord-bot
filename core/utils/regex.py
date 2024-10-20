import re


def remove_url_from_text(text: str):
    return re.sub(r'^https?:\/\/.*[\r\n]*', '', text, flags=re.MULTILINE)


def get_user_id_from_mention(mention: str):
    regex = r'<@(\d+)>'
    match_user_id = re.search(regex, mention)
    return match_user_id.group(1)
