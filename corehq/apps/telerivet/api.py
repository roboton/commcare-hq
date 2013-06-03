import os
import pycurl
import StringIO
import json
from couchdbkit.ext.django.schema import *
from urllib import urlencode
from corehq.apps.sms.util import clean_phone_number
from corehq.apps.sms.mixin import SMSBackend
from corehq.apps.telerivet.forms import TelerivetBackendForm

MESSAGE_TYPE_SMS = "sms"

class TelerivetBackend(SMSBackend):
    api_key = StringProperty()      # The api key of the account to send from.
    project_id = StringProperty()   # The Telerivet project id.
    phone_id = StringProperty()     # The id of the phone to send from, as shown on Telerivet's API page.

    @classmethod
    def get_api_id(cls):
        return "TELERIVET"

    @classmethod
    def get_description(cls):
        return "Telerivet"

    @classmethod
    def get_template(cls):
        return "telerivet/backend.html"

    @classmethod
    def get_form_class(cls):
        return TelerivetBackendForm

    def send(msg, *args, **kwargs):
        try:
            text = msg.text.encode("iso-8859-1")
        except UnicodeEncodeError:
            text = msg.text.encode("utf-8")
        params = urlencode({
            "phone_id" : self.phone_id,
            "to_number" : clean_phone_number(msg.phone_number),
            "content" : text,
            "message_type" : MESSAGE_TYPE_SMS,
        })
        url = "https://api.telerivet.com/v1/projects/%s/messages/outgoing" % self.project_id
        
        curl = pycurl.Curl()
        buf = StringIO.StringIO()
        
        curl.setopt(curl.URL, url)
        curl.setopt(curl.USERPWD, "%s:" % self.api_key)
        curl.setopt(curl.WRITEFUNCTION, buf.write)
        curl.setopt(curl.POSTFIELDS, params)
        curl.setopt(curl.CAINFO, "%s/cacert.pem" % os.path.dirname(os.path.abspath(__file__)))
        curl.perform()
        curl.close()
        
        result = json.loads(buf.getvalue())
        buf.close()

