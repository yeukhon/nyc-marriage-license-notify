import datetime
import logging
import json
import os
import time

import requests
from twilio.rest import Client

CALENDAR_LINK = (
    "https://calendly.com/api/booking/event_types/BFEN3HYGXBSSUYOC/calendar"
    "/range?timezone=America%2FNew_York&diagnostics=false"
    "&range_start=2020-08-19&range_end=2020-12-18"
    "&single_use_link_uuid=&embed_domain=projectcupid.cityofnewyork.us"
)
CALL_MESSAGE = "Found appointment for NYC marriage license. Check SMS!"
LUCKY_MESSAGE = "GOOD NEWS! NYC CUPID marriage license appointment available on these dates: {}"
SAD_MESSAGE = "Time is {}. No free spot yet! I will keep checking!"

logger = logging.getLogger(__name__)
#logging.basicConfig(filename="app.log", 
#                    level=logging.DEBUG, 
#                    format="%(asctime)s - %(levelname)s - %(message)s")

class BadRequest(Exception):
    pass


def load_configs():
    configs = {}
    curr_dir = os.path.dirname(os.path.realpath(__file__))
    config_file = os.path.join(curr_dir, "twilio.json")
    with open(config_file, "r") as f:
        configs = json.load(f)
    if not configs:
        raise Exception("No Twilio credentials and configurations read!")
    return configs

def get_avaialble_appointments():
    availables = []
    response = requests.get(CALENDAR_LINK)
    if response.status_code in (200, 304):
        data = response.json()
        for date in data["days"]:
            if date["status"] != "unavailable":
                availables.append(date["date"])
    else:
        logger.error(f"Unable to get valid response from the calendar app (status={response.status_code})")
        raise BadRequest("Something went wrong with the calendar app")
    print("Found {} dates availables from the calendar app".format(len(availables)))
    return availables


def send_sms(client, to_number, from_number, message):
    # either case we send sms
    twilio_msg = client.messages.create(
        to=to_number,
        from_=from_number,
        body=message
    )
    return twilio_msg


def make_call(client, to_number, from_number, message):
    twilio_call = client.calls.create(
        twiml=f"<Response><Say>{message}</Say></Response>",
        to=to_number,
        from_=from_number
    )
    return twilio_call


def main():
    configs = load_configs()
    to_number = configs["to_number"]
    from_number = configs["from_number"]
    twilio_creds = configs["auth"]

    client = Client(twilio_creds["account_sid"], twilio_creds["auth_token"])

    dates = get_avaialble_appointments()
    if dates:
        sms_message = LUCKY_MESSAGE.format(", ".join(date for date in dates))
    else:
        sms_message = SAD_MESSAGE.format(time.ctime())
    print(f"SMS message: {sms_message}")

    # by default we only send sms twice a day
    do_send_sms = False
    # if there are dates, call immediately and send sms
    if dates:
        do_send_sms = True
        call = make_call(client, to_number, from_number, CALL_MESSAGE)
        print(f"Call made. SID = {call.sid}")
    else:
        now = datetime.datetime.now()
        if now.hour in (14, 22) and now.minute in range(5, 10):
           do_send_sms = True

    if do_send_sms:
        sms = send_sms(client, to_number, from_number, sms_message)
        print(f"SMS made. SID = {sms.sid}")


if __name__ == "__main__":
    main()
