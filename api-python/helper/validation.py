from pydantic import BaseModel, Field, condecimal
from typing import Optional


# Product Validation Schema
class ProductSchema(BaseModel):
    productId: str  # Product ID is required and should be a string
    name: str  # Name is required
    category: Optional[str] = None  # Category is optional and can be None or empty
    subcategory: Optional[str] = None  # Subcategory is optional and can be None or empty
    price: condecimal(gt=0)  # Price is required and must be a positive number
    keywords: str  # Keywords are required and should be a string

    # Additional validation
    class Config:
        min_anystr_length = 3  # Enforces a minimum length of 3 for string fields


# User Validation Schema
class UserSchema(BaseModel):
    name: str  # Name is required
    email: str  # Email is required
    password: str  # Password is required
    shippingAddress: str  # Shipping address is required

    # Enforcing additional validation
    @classmethod
    def validate(cls, values):
        if len(values.get('password', '')) < 6:
            raise ValueError('Password must be at least 6 characters long')
        if len(values.get('shippingAddress', '')) < 5:
            raise ValueError('Shipping address must be at least 5 characters long')
        return values


# Query Parameters Validation Schema
class QuerySchema(BaseModel):
    keywords: str  # Keywords are required and should be a string
    category: Optional[str] = None  # Category is optional and can be None or empty
    subcategory: Optional[str] = None  # Subcategory is optional and can be None or empty
    minPrice: Optional[condecimal(gt=0)] = None  # Minimum price is optional and should be a positive number
    maxPrice: Optional[condecimal(gt=0)] = None  # Maximum price is optional and should be a positive number


# Cart Item Validation Schema
class CartItemSchema(BaseModel):
    userId: str  # User ID is required and should be a string
    productId: str  # Product ID is required and should be a string
    quantity: Optional[int] = 1  # Quantity is optional with a default value of 1

    # Ensure that quantity is always a positive number
    @classmethod
    def validate(cls, values):
        if values.get('quantity') <= 0:
            raise ValueError('Quantity must be a positive number')
        return values


# Validation Functions
def validate_product(product_data: dict) -> ProductSchema:
    return ProductSchema(**product_data)  # Validates product data against the product schema


def validate_user(user_data: dict) -> UserSchema:
    return UserSchema(**user_data)  # Validates user data against the user schema


def validate_query_params(query_params: dict) -> QuerySchema:
    return QuerySchema(**query_params)  # Validates query parameters against the query schema


def validate_cart_item(cart_item_data: dict) -> CartItemSchema:
    return CartItemSchema(**cart_item_data)  # Validates cart item data against the cart item schema


# Example usage (to test the functions):
try:
    product = validate_product({
        'productId': '1234',
        'name': 'Laptop',
        'category': 'Electronics',
        'subcategory': 'Computers',
        'price': 1200.50,
        'keywords': 'laptop, computer, electronics'
    })
    print("Product is valid:", product)
except ValueError as e:
    print(f"Product validation failed: {e}")