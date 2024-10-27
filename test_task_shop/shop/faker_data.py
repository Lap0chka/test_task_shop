import os
import random

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test_task_shop.settings')
django.setup()

from faker import Faker
from shop.models import Product, Category
from django.utils.text import slugify

fake = Faker()

categories = []
for _ in range(2):
    name = fake.word()
    slug = slugify(name)
    category = Category.objects.create(name=name, slug=slug)
    categories.append(category)

for _ in range(30):
    title = fake.sentence(nb_words=3)
    slug = slugify(title)
    brand = fake.company()
    description = fake.text()
    price = round(random.uniform(10, 500), 2)
    available = True
    category = random.choice(categories)

    Product.objects.create(
        title=title,
        slug=slug,
        brand=brand,
        description=description,
        price=price,
        is_available=available,
        category=category
    )