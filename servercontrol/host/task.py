# Create your tasks here
from celery import shared_task
import json

from labcontrol.browser import Browser
from labcontrol.lab_aws import LabAWS
from labcontrol.constants import BrowserStatus, PCStatus
import redis
from django.core.cache import cache


@shared_task
def start_browser():
    browser = Browser()
    if browser.status == BrowserStatus.Stopped:
        cache.set("browser_status", BrowserStatus.Running.value)
    browser.load_aws()
    return True


@shared_task
def stop_browser():
    browser = Browser()
    Browser.stop(browser)
    return True


@shared_task
def go_to_url(url):
    browser = Browser()
    browser.go_url(url)
    return True


@shared_task
def get_status():
    lab = LabAWS()
    status = lab.status
    return {"lab_status": status.value}
