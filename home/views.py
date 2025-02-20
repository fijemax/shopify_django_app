from django.shortcuts import render
import shopify
from shopify_app.decorators import shop_login_required
from django.http import JsonResponse
from django.conf import settings
import hashlib
import hmac
from django.views.decorators import clickjacking
SHOPIFY_API_KEY="e9639cbd4c600d4a18c7ca629b4e842b"
SHOPIFY_API_SECRET="1ad27a9c2ac0947ad9d46c94a7181107"
# DJANGO_SECRET="!e%o$-jg+ad6&9@e-09k!7mdazuh+3urwolnb$asw7u!owt$$v"

@shop_login_required
@clickjacking.xframe_options_exempt
def index(request):
    products = shopify.Product.find(limit=3)
    orders = shopify.Order.find(limit=3, order="created_at DESC")
    return render(request, 'home/index.html', {'products': products, 'orders': orders})

def get_auth_url(shop):
    shop_url = "localhost"
    return shopify.Session.setup(api_key=SHOPIFY_API_KEY, secret=SHOPIFY_API_SECRET)
    # return f"https://{shop_url}/admin/oauth/authorize?client_id=5e86f42aac4231029515c8d7d6280612&scope=read_products,read_orders,write_products&redirect_uri=http://localhost:8000/shopify_app/finalize/"

def create_product(request):
    print("cicicicicic\n"*10)
    print(request)
    print(request.session['shopify']["access_token"])

    # chatgpt code to try:
    # shopify.ShopifyResource.set_site(f"https://{ACCESS_TOKEN}@{SHOP_URL}/admin/api/2025-01")

    product = shopify.Product()
    product.title = "Sample Product"
    product.body_html = "<strong>This is a great product!</strong>"
    product.vendor = "Your Brand"
    product.product_type = "T-Shirt"

    # Save the product to Shopify
    success = product.save()

    print(success)

    return JsonResponse({"message": f"Action completed successfully! {success}"})


def create_webhook(request):
    # Not received when order finished
    # webhook_data = {
    #     "topic": "orders/fulfilled",
    #     "address": "pubsub://dresskare-1638635070154:shopify-dev",
    #     # "address": "pubsub://dresskare-1638635070154:shopify-dev-sub",
    #     # "address": "pubsub://projects/dresskare-1638635070154/topics/shopify-dev",
    #     "format": "json"
    # }
    # webhook = shopify.Webhook.create(webhook_data)

    # received
    webhook_data = {
        "topic": "orders/paid",
        "address": "pubsub://dresskare-1638635070154:shopify-dev",
        # "address": "pubsub://dresskare-1638635070154:shopify-dev-sub",
        # "address": "pubsub://projects/dresskare-1638635070154/topics/shopify-dev",
        "format": "json"
    }
    webhook = shopify.Webhook.create(webhook_data)


    # example with https
    # webhook_data = {
    #     "topic": "orders/paid",
    #     "address": "https://fd5f-2a01-cb14-588-5100-9477-ba1-2f53-60bf.ngrok-free.app/shopify/webhook3",
    #     "format": "json"
    # }
    # webhook = shopify.Webhook.create(webhook_data)

    if webhook.errors:
        print("Erreur :", webhook.errors.full_messages())
    else:
        print("Webhook créé avec succès :", webhook)

    webhooks = shopify.Webhook.find()
    for webhook in webhooks:
        print(f"ID: {webhook.id}, Topic: {webhook.topic}, Adresse: {webhook.address}")
    return JsonResponse({"message": "Action completed successfully!"})

def destroy_webhook(request):
    webhooks = shopify.Webhook.find()
    for webhook in webhooks:
        webhook = shopify.Webhook.find(webhook.id)
        webhook.destroy()
        print(f"Webhook {webhook.id} supprimé.")
    return JsonResponse({"message": "Action completed successfully!"})


def logs_webhook(request):
    # 📌 Récupérer tous les webhooks
    webhooks = shopify.Webhook.find()

    for webhook in webhooks:
        print(f"Webhook ID: {webhook.id}, Topic: {webhook.topic}, Address: {webhook.address}")

        # 🔍 Récupérer les deliveries pour chaque webhook
        deliveries_url = f"/admin/api/2025-01/webhooks/{webhook.id}/deliveries.json"
        deliveries = shopify.ShopifyResource.connection.get(deliveries_url)

        for delivery in deliveries["deliveries"]:
            print(f" - 📅 Date: {delivery['created_at']}")
            print(f"   ✅ Status: {delivery['status_code']}")
            print(f"   🔄 Tentatives: {delivery['attempts_count']}")
            print(f"   📝 Body: {delivery['response_body']}\n")

def verify_shopify_webhook(data, hmac_header):
    """ Vérifie l'authenticité du webhook Shopify """
    digest = hmac.new(apps.get_app_config('shopify_app').SHOPIFY_API_SECRET.encode(), data, hashlib.sha256).digest()
    computed_hmac = hmac_header.encode()
    return hmac.compare_digest(computed_hmac, digest)