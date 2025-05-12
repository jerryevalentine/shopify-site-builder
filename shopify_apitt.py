# C:\Users\jerry\ecommerce\shopify_deploy
# shopify_api.py

import base64
import requests
import os
from dotenv import load_dotenv

# Load the .env file
load_dotenv()

# Read environment variables
SHOPIFY_STORE_URL = os.getenv('SHOPIFY_STORE_URL')
SHOPIFY_ACCESS_TOKEN = os.getenv('SHOPIFY_ACCESS_TOKEN')

# Set Headers for API Authentication
HEADERS = {
    "Content-Type": "application/json",
    "X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN
}

# --------- Product and Collection Management ---------

def create_product(product_data):
    """Create a new product in Shopify if SKU does not already exist."""
    existing_product_id = find_product_id_by_sku(product_data["SKU"])
    if existing_product_id:
        print(f"Product with SKU {product_data['SKU']} already exists. Skipping creation.")
        return {"status": "exists", "product_id": existing_product_id}
    
    url = f"{SHOPIFY_STORE_URL}/admin/api/2023-04/products.json"
    payload = {
        "product": {
            "title": product_data["Product Name"],
            "body_html": product_data.get("Description", ""),
            "vendor": product_data.get("Brand", ""),
            "product_type": product_data.get("Category", ""),
            "variants": [
                {
                    "sku": product_data["SKU"],
                    "price": str(product_data["Price"])
                }
            ]
        }
    }
    response = requests.post(url, headers=HEADERS, json=payload)
    return response.json()

def find_product_id_by_sku(sku):
    """Find a product's ID in Shopify using SKU."""
    url = f"{SHOPIFY_STORE_URL}/admin/api/2023-04/products.json?fields=id,variants"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        products = response.json().get('products', [])
        for product in products:
            for variant in product.get('variants', []):
                if variant['sku'] == sku:
                    return product['id']
    return None

def create_collection(collection_data):
    """Create a new custom collection in Shopify."""
    url = f"{SHOPIFY_STORE_URL}/admin/api/2023-04/custom_collections.json"
    payload = {
        "custom_collection": {
            "title": collection_data["Page Name"],
            "handle": collection_data["URL Slug"]
        }
    }
    response = requests.post(url, headers=HEADERS, json=payload)
    return response.json()

def find_collection_id_by_title(title):
    """Find a collection's ID in Shopify by title."""
    url = f"{SHOPIFY_STORE_URL}/admin/api/2023-04/custom_collections.json?fields=id,title"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        collections = response.json().get('custom_collections', [])
        for collection in collections:
            if collection['title'].lower() == title.lower():
                return collection['id']
    return None

def add_product_to_collection(product_id, collection_id):
    """Add a product to a collection."""
    url = f"{SHOPIFY_STORE_URL}/admin/api/2023-04/collects.json"
    payload = {
        "collect": {
            "product_id": product_id,
            "collection_id": collection_id
        }
    }
    response = requests.post(url, headers=HEADERS, json=payload)
    return response.json()

# --------- Image Uploading ---------

def upload_image_to_product(product_id, image_url):
    """Upload an external image URL to a product."""
    url = f"{SHOPIFY_STORE_URL}/admin/api/2023-04/products/{product_id}/images.json"
    payload = {
        "image": {
            "src": image_url
        }
    }
    response = requests.post(url, headers=HEADERS, json=payload)
    print(response.status_code)
    print(response.json())
    return response.json()

def upload_local_image_to_product(product_id, image_path, position):
    """Upload a local image file to a product and set its position and alt text."""
    url = f"{SHOPIFY_STORE_URL}/admin/api/2023-04/products/{product_id}/images.json"
    
    try:
        with open(image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
    except FileNotFoundError:
        print(f"Image file not found: {image_path}. Skipping...")
        return

    # Set ALT text based on position
    alt_text = "Front View" if position == 1 else \
               "Back View" if position == 2 else \
               "Side View" if position == 3 else \
               "Detail View" if position == 4 else \
               f"View {position}"

    payload = {
        "image": {
            "attachment": encoded_image,
            "position": position,
            "alt": alt_text
        }
    }
    response = requests.post(url, headers=HEADERS, json=payload)
    
    print(f"Uploaded image at position {position} with ALT text '{alt_text}'")
    print(response.status_code)
    print(response.json())
    
    return response.json()


# --------- Pages Management ---------

def create_page(page_data):
    """Create a new page in Shopify."""
    url = f"{SHOPIFY_STORE_URL}/admin/api/2023-04/pages.json"
    payload = {
        "page": {
            "title": page_data["Title"],
            "body_html": page_data["Body"]
        }
    }
    response = requests.post(url, headers=HEADERS, json=payload)
    print(response.status_code)
    print(response.json())
    return response.json()

# --------- Navigation Management (Deprecated REST, will show errors) ---------

def get_all_menus():
    """Fetch all navigation menus."""
    url = f"{SHOPIFY_STORE_URL}/admin/api/2023-04/menus.json"
    response = requests.get(url, headers=HEADERS)
    return response.json()

def find_menu_id_by_name(menu_name):
    """Find a menu ID by its name."""
    menus = get_all_menus()
    for menu in menus.get('menus', []):
        if menu['title'].lower() == menu_name.lower():
            return menu['id']
    return None

def add_link_to_navigation(menu_id, title, link_type, target_handle):
    """Add a link (Page, Collection, Product, URL) to a Menu."""
    url = f"{SHOPIFY_STORE_URL}/admin/api/2023-04/menus/{menu_id}/links.json"
    payload = {
        "link": {
            "title": title,
            "type": link_type,
            "subject_id": target_handle
        }
    }
    response = requests.post(url, headers=HEADERS, json=payload)
    return response.json()

# --------- Theme Asset Management ---------

def upload_theme_asset(theme_id, asset_key, asset_value):
    """Upload or update a file (asset or template) in the Shopify theme."""
    url = f"{SHOPIFY_STORE_URL}/admin/api/2023-04/themes/{theme_id}/assets.json"
    payload = {
        "asset": {
            "key": asset_key,
            "value": asset_value
        }
    }
    response = requests.put(url, headers=HEADERS, json=payload)
    print(response.status_code)
    print(response.json())
    return response.json()

def upload_local_image_to_product_with_alt(product_id, image_path, position, base_alt_text):
    """Upload a local image file to a product, setting structured alt text."""
    url = f"{SHOPIFY_STORE_URL}/admin/api/2023-04/products/{product_id}/images.json"

    try:
        with open(image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
    except FileNotFoundError:
        print(f"Image file not found: {image_path}. Skipping...")
        return

    # Determine the view name based on position
    view_name = "Front View" if position == 1 else \
                "Back View" if position == 2 else \
                "Side View" if position == 3 else \
                "Detail View" if position == 4 else \
                f"View {position}"

    # Build full structured ALT text
    structured_alt_text = f"{base_alt_text} - {view_name}"

    payload = {
        "image": {
            "attachment": encoded_image,
            "position": position,
            "alt": structured_alt_text
        }
    }
    response = requests.post(url, headers=HEADERS, json=payload)

    print(f"Uploaded image at position {position} with ALT text: '{structured_alt_text}'")
    print(response.status_code)
    print(response.json())

    return response.json()



def graphql_query(query, variables=None):
    """Send a GraphQL query to Shopify."""
    url = f"{SHOPIFY_STORE_URL}/admin/api/2023-04/graphql.json"
    payload = {
        "query": query,
        "variables": variables or {}
    }
    response = requests.post(url, headers=HEADERS, json=payload)
    response.raise_for_status()
    return response.json()



def add_link_to_navigation_menu(menu_id, link_title, link_type, destination_id=None):
    """Add a link to a specific navigation menu."""
    query = """
    mutation menuItemCreate($menuItem: MenuItemInput!) {
      menuItemCreate(menuItem: $menuItem) {
        menuItem {
          id
        }
        userErrors {
          field
          message
        }
      }
    }
    """
    menu_item = {
        "title": link_title,
        "menuId": menu_id,
    }

    if link_type == "URL":
        menu_item["url"] = destination_id  # destination_id would be like "/"
    else:
        menu_item["resourceId"] = destination_id  # Shopify Resource ID (gid)

    variables = {
        "menuItem": menu_item
    }
    response = graphql_query(query, variables)
    
    if 'errors' in response:
        print(f"❌ Error adding link {link_title}: {response['errors']}")
    else:
        print(f"✅ Added Link: {link_title}")
    
    return response


def find_page_id_by_title(title):
    """Find a Page ID in Shopify by its title."""
    query = """
    {
      pages(first: 50) {
        edges {
          node {
            id
            title
          }
        }
      }
    }
    """
    result = graphql_query(query)

    if 'errors' in result:
        print("GraphQL Errors:", result['errors'])
        return None

    pages = result['data']['pages']['edges']

    for page in pages:
        if page['node']['title'].lower() == title.lower():
            return page['node']['id']
    
    return None

def find_product_id_by_title(title):
    """Find a Product ID in Shopify by its title."""
    query = """
    {
      products(first: 50) {
        edges {
          node {
            id
            title
          }
        }
      }
    }
    """
    result = graphql_query(query)

    if 'errors' in result:
        print("GraphQL Errors:", result['errors'])
        return None

    products = result['data']['products']['edges']

    for product in products:
        if product['node']['title'].lower() == title.lower():
            return product['node']['id']
    
    return None

def create_navigation_menu(title):
    """Create a new Navigation Menu in Shopify."""
    query = """
    mutation menuCreate($menu: MenuInput!) {
      menuCreate(menu: $menu) {
        menu {
          id
          title
        }
        userErrors {
          field
          message
        }
      }
    }
    """
    variables = {
        "menu": {
            "title": title
        }
    }
    response = graphql_query(query, variables)
    
    if 'errors' in response:
        print(f"❌ Error creating menu {title}: {response['errors']}")
    else:
        print(f"✅ Created Navigation Menu: {title}")
        
    return response


def find_navigation_menu_id_by_title(title):
    """Find the ID of a Navigation Menu by its Title."""
    query = """
    {
      navigationMenus(first: 50) {
        edges {
          node {
            id
            title
          }
        }
      }
    }
    """
    result = graphql_query(query)

    if 'errors' in result:
        print(f"❌ Error fetching menus: {result['errors']}")
        return None

    menus = result['data']['navigationMenus']['edges']

    for menu in menus:
        if menu['node']['title'].lower() == title.lower():
            return menu['node']['id']
    
    return None

