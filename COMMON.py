def clean_string(ip_str):
    ip_str.strip().replace('\n', ' ')
    ip_str.replace('\r', '')
    return ip_str
