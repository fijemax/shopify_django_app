from django.apps import AppConfig
import os
from google.cloud import pubsub_v1
from pathlib import Path

class ShopifyAppConfig(AppConfig):
    name = 'shopify_app'
    # Replace the API Key and Shared Secret with the one given for your
    # App by Shopify.
    #
    # To create an application, or find the API Key and Secret, visit:
    # - for private Apps:
    #     https://${YOUR_SHOP_NAME}.myshopify.com/admin/api
    # - for partner Apps:
    #     https://www.shopify.com/services/partners/api_clients
    #
    # You can ignore this file in git using the following command:
    #   git update-index --assume-unchanged shopify_settings.py
    SHOPIFY_API_KEY = os.environ.get('SHOPIFY_API_KEY')
    SHOPIFY_API_SECRET = os.environ.get('SHOPIFY_API_SECRET')

    # API_VERSION specifies which api version that the app will communicate with
    SHOPIFY_API_VERSION = os.environ.get('SHOPIFY_API_VERSION', 'unstable')

    # See http://api.shopify.com/authentication.html for available scopes
    # to determine the permisssions your app will need.
    SHOPIFY_API_SCOPE = os.environ.get('SHOPIFY_API_SCOPE', 'read_products,read_orders,write_products').split(',')


    def __init__(self, app_name, app_module):
        print(os.getcwd())
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = Path(
            "./dresskare-gcp-credentials.json"
        ).as_posix()

        subscriber = pubsub_v1.SubscriberClient()

        # Define the subscription path
        subscription_path = subscriber.subscription_path("dresskare-1638635070154", "shopify-dev-sub")

        # Define a callback function to handle incoming messages
        def callback(message):
            print("Received message:\n"*5)
            print(f"Received message: {message.data.decode('utf-8')}")
            message.ack()  # Acknowledge the message

        # Subscribe to the topic
        subscriber.subscribe(subscription_path, callback=callback)

        super().__init__(app_name, app_module)