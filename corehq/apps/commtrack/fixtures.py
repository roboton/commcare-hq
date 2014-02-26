from xml.etree import ElementTree
from corehq import Domain
from .models import Product


def product_fixture_generator(user, version, last_sync):
    if not user.domain:
        return []
    domain = Domain.get_by_name(user.domain)
    if not domain or not Domain.get_by_name(user.domain).commtrack_enabled:
        return []

    root = ElementTree.Element('fixture',
                               attrib={'id': 'commtrack:products',
                                       'user_id': user.user_id})
    products = ElementTree.Element('products')
    root.append(products)
    for product_data in Product.by_domain(user.domain):
        product = (ElementTree.Element('product',
                                       {'id': product_data.get_id}))
        products.append(product)
        product_fields = ['name',
                          'unit',
                          'code',
                          'description',
                          'category',
                          'program_id',
                          'cost']
        for product_field in product_fields:
            field = ElementTree.Element(product_field)
            val = getattr(product_data, product_field, None)
            field.text = unicode(val if val is not None else '')
            product.append(field)

    return [root]
