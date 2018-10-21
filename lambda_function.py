'''

The following JSON template shows what is sent as the payload:
{
    "serialNumber": "GXXXXXXXXXXXXXXXXX",
    "batteryVoltage": "xxmV",
    "clickType": "SINGLE" | "DOUBLE" | "LONG"
}

A "LONG" clickType is sent if the first press lasts longer than 1.5 seconds.
"SINGLE" and "DOUBLE" clickType payloads are sent for short clicks.

For more documentation, follow the link below.
http://docs.aws.amazon.com/iot/latest/developerguide/iot-lambda-rule.html
'''

from __future__ import print_function

import boto3
import json
import logging
import os
import urllib2

logger = logging.getLogger()
logger.setLevel(logging.INFO)

sns = boto3.client('sns')
ses = boto3.client('ses')

phone_number = os.environ['phone_number']
email_address = os.environ['email_address']

# Check whether email is verified. Only verified emails are allowed to send emails to or from.
def check_email(email):
    result = ses.get_identity_verification_attributes(Identities=[email])
    attr = result['VerificationAttributes']
    if (email not in attr or attr[email]['VerificationStatus'] != 'Success'):
        logging.info('Verification email sent. Please verify it.')
        ses.verify_email_identity(EmailAddress=email)
        return False
    return True

## Main treatment
def lambda_handler(event, context):
    import subprocess
    logger.info('Received event: ' + json.dumps(event))


    subject = 'Appui sur le bouton de la maison xxxxxxxxx. Mode %s.'% (event['clickType'])
    body_text = 'Here is the full event: %s' % json.dumps(event)
    

    ## In every cases, send a mail
    if not check_email(email_address):
        logging.error('Email is not verified')
    else:
        ses.send_email(Source=email_address,
                       Destination={'ToAddresses': [email_address]},
                       Message={'Subject': {'Data': subject}, 'Body': {'Text': {'Data': body_text}}})
        logger.info('Email has been sent')
    
    ## If clickType= DOUBLE => Escalate as SMS
    ## clickType = event['clickType']
    ## logger.info('clickType: ' + clickType)

    #sns.publish(PhoneNumber=phone_number, Message=subject)
    #logger.info('SMS has been sent to ' + phone_number)
    
    #Send to user1
    urllib2.urlopen('https://smsapi.free-mobile.fr/sendmsg?user=xxxxxxxxx&pass=xxxxxxxxx&msg=' + subject).read()
    # Send to user2
    urllib2.urlopen('https://smsapi.free-mobile.fr/sendmsg?user=xxxxxxxxx&pass=xxxxxxxxx&msg=' + subject).read()
    logger.info('SMS has been sent')
