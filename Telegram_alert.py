import requests
from keepass import key_pass

def telega_alert(Report: str):
    api_token = key_pass('AF Report Bot').password
    requests.get('https://api.telegram.org/bot{}/sendMessage'.format(api_token), params=dict(
        chat_id = key_pass('AlfaForex Reports').password,
        parse_mode= 'Markdown',
        text=Report
    ))
