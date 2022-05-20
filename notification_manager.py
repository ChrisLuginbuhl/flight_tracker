import credentials
import logging
from twilio.rest import Client

logger = logging.getLogger()
logging.basicConfig(level=logging.DEBUG)


class NotificationManager:
    #This class is responsible for sending notifications with the deal flight details.

    # Find your Account SID and Auth Token at twilio.com/console
    # and set the environment variables. See http://twil.io/secure
    def notify(self, flights: list) -> str:
        """Accepts a list of FlightData objects (which are (Tequila query response.json()['data']). Formats
        and sends SMS notification with cheap fight details via Twilio. Returns message status. """
        message = "Cheap flight alert! "
        for flight in flights:
            price = flight['price']
            from_city = flight['cityFrom']
            from_iata_code = flight['flyFrom']
            to_city = flight['cityTo']
            to_iata_code = flight['flyTo']
            outbound_date = flight['route'][0]['local_departure'].split('T')[0]
            inbound_date = flight['route'][1]['local_departure'].split('T')[0]
            airline = flight['airlines'][0]
            message += f"${price} from {from_city} {from_iata_code} to {to_city} {to_iata_code}, " \
                       f"{outbound_date} to {inbound_date} on {airline}.\n"
        print(message)


        # account_sid = os.environ['TWILIO_ACCOUNT_SID']
        # auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
        # logger.debug(f"Twilio auth token: {auth_token}")
        account_sid = credentials.TWILIO_SID
        auth_token = credentials.TWILIO_TOKEN
        client = Client(account_sid, auth_token)
        client.http_client.logger.setLevel(logging.INFO)
        message = client.messages \
            .create(
            body=message,
            from_=credentials.TWILIO_PHONE,
            to='+14168196639'
        )

        print(message.sid)
        logger.debug(message.status)

