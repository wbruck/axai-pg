"""Sample data fixtures for testing."""

SAMPLE_USERS = [
    {
        "username": "john_doe",
        "email": "john@example.com",
        "full_name": "John Doe",
        "age": 30
    },
    {
        "username": "jane_smith",
        "email": "jane@example.com",
        "full_name": "Jane Smith",
        "age": 25
    },
    {
        "username": "bob_wilson",
        "email": "bob@example.com",
        "full_name": "Bob Wilson",
        "age": 40
    }
]

SAMPLE_PRODUCTS = [
    {
        "name": "Product A",
        "price": 19.99,
        "description": "Description for Product A",
        "stock": 100
    },
    {
        "name": "Product B",
        "price": 29.99,
        "description": "Description for Product B",
        "stock": 50
    },
    {
        "name": "Product C",
        "price": 39.99,
        "description": "Description for Product C",
        "stock": 25
    }
]

SAMPLE_ORDERS = [
    {
        "user_id": 1,
        "product_id": 1,
        "quantity": 2,
        "total_price": 39.98
    },
    {
        "user_id": 2,
        "product_id": 2,
        "quantity": 1,
        "total_price": 29.99
    },
    {
        "user_id": 3,
        "product_id": 3,
        "quantity": 3,
        "total_price": 119.97
    }
] 