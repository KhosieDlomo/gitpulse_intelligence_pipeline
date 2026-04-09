import pytest
from src.notifier import NotificationProvider

def test_discord_message_logic():
    notifier = NotificationProvider(webhook_url="http://fake-url")
    
    test_repo = [{
        'name': 'ViralProject',
        'lang': 'Python',
        'growth': 150, # Should trigger the [EXPLOSIVE] tag
        'label': 'AI',
        'stars': 1000,
        'link': 'http://link',
        'summary': 'Cool project'
    }]