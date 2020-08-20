## Setup

You need a Twilio account. Use virtualenv and then install these two third-party packages:

```
pip install requests twilio
```

Next, copy `twilio.json.example` to `twilio.json` and replace dummy values with
your authentication credentials and phone numbers.

## Usage

I run this as a cron on my Mac every five minutes.

```
*/5 * * * * /path/to/virtualenv/bin/python /path/to/repo/main.py 2>&1 >> /tmp/app.log
```

By default the program will send two SMS messages per day: ~2pm and ~10pm.
If one or more slots are available, the program will dial your phone and send sms.
