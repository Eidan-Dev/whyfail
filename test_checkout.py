"""A tiny checkout module with three bugs. Run: whyfail examples/test_checkout.py"""


def get_discount(user):
    if user.get("vip"):
        return 0.2
    # Bug: no return for regular users, so the function returns None


def total(prices):
    return sum(prices) * 1.1 - 1  # Bug: a stray "- 1"


def customer_email(order):
    return order["customer"]["email"]  # Bug: no email on guest orders


def test_vip_discount():
    assert get_discount({"vip": True}) == 0.2


def test_regular_discount():
    assert get_discount({}) == 0


def test_total_with_tax():
    assert total([10, 20]) == 33


def test_customer_email():
    assert customer_email({"customer": {"name": "Ana"}}) == "ana@example.com"


def test_empty_cart():
    assert total([]) == 0
