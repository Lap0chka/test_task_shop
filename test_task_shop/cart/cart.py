from decimal import Decimal


from shop.models import Product


class Cart:
    """
    Represents a shopping cart for storing and managing products and quantities.
    Allows adding, updating, deleting products, calculating total price, and iterating over cart items.
    """
    def __init__(self, request):
        self.session = request.session
        self.cart = self.cart_init()

    def __iter__(self):
        product_ids = self.cart.keys()
        products = Product.available.filter(id__in=product_ids)
        cart = self.cart.copy()

        for product in products:
            cart[str(product.id)]['product'] = product

        for item in cart.values():
            item['price'] = Decimal(item['price'])
            item['total'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())

    def cart_init(self):
        cart = self.session.get('session_key')
        if not cart:
            cart = self.session['session_key'] = {}
        return cart

    def add(self, product, quantity):
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': quantity, 'price': str(product.price)}
        else:
            self.cart[product_id]['quantity'] += quantity
        self.session.modified = True

    def get_total_price(self):
        total_price = sum([Decimal(item['price'])*item['quantity'] for item in self.cart.values()])
        return total_price

    def update(self, product_id, quantity):
        if product_id in self.cart:
            self.cart[product_id]['quantity'] = quantity
            self.session.modified = True

    def delete(self, product_id, quantity=2):
        if product_id in self.cart:
            if self.cart[product_id]['quantity'] <= quantity:
                del self.cart[product_id]
            else:
                self.cart[product_id]['quantity'] -= quantity
            self.session.modified = True
