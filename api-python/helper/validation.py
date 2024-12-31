from pydantic import BaseModel, Field, condecimal, validator
from typing import Optional


# Product Validation Schema
class ProductSchema(BaseModel):
    productId: str  # Product ID is required and should be a string
    name: str  # Name is required
    category: Optional[str] = None  # Category is optional and can be None or empty
    subcategory: Optional[str] = None  # Subcategory is optional and can be None or empty
    price: Optional[float] = Field(..., gt=0)  # Price is required and must be > 0
    keywords: str  # Keywords are required and should be a string

    # Additional validation configuration
    class Config:
        anystr_min_length = 3 


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
    minPrice: Optional[float] = Field(default=None, gt=0)  # Minimum price is optional and must be > 0
    maxPrice: Optional[float] = Field(default=None, gt=0)  # Maximum price is optional and must be > 0

    # Validate price range
    @validator('minPrice', 'maxPrice', pre=True, always=True)
    def validate_price_range(cls, v, values, field):
        if field.name == 'minPrice' and v is not None:
            max_price = values.get('maxPrice')
            if max_price is not None and v > max_price:
                raise ValueError("minPrice cannot be greater than maxPrice")
        if field.name == 'maxPrice' and v is not None:
            min_price = values.get('minPrice')
            if min_price is not None and v < min_price:
                raise ValueError("maxPrice cannot be less than minPrice")
        return v


class CartItem(BaseModel):
    userId: str
    productId: str
    quantity: Optional[int] = 1  # Default quantity to 1 if not provided

    # Validation for quantity
    @validator('quantity', pre=True, always=True)
    def validate_quantity(cls, v):
        if v <= 0:
            raise ValueError('Quantity must be greater than 0')
        return v


# Validation Functions
def validate_product(product_data: dict) -> ProductSchema:
    return ProductSchema(**product_data)  # Validates product data against the product schema


def validate_user(user_data: dict) -> UserSchema:
    return UserSchema(**user_data)  # Validates user data against the user schema


def validate_query_params(query_params: dict) -> QuerySchema:
    return QuerySchema(**query_params)  # Validates query parameters against the query schema


def validate_cart_item(cart_item_data: dict) -> CartItem:
    return CartItem(**cart_item_data)  # Validates cart item data against the cart item schema


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