"""
Demo E-commerce API - Intentionally Buggy for Testing AIQA Platform

This API contains intentional bugs to test AIQA's capabilities:
- Security vulnerabilities
- Performance issues
- Logic errors
- API breaking changes
- Missing validations

DO NOT use this in production!
"""

from fastapi import FastAPI, HTTPException, Depends, Header, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
import time
from datetime import datetime
import hashlib

app = FastAPI(
    title="Demo E-commerce API",
    description="Buggy API for testing AIQA platform",
    version="1.0.0"
)

# CORS - Intentionally too permissive (SECURITY BUG #1)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # BUG: Should be restricted
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# In-Memory Database (Simulated)
# ============================================================================

users_db = {}
products_db = {}
orders_db = {}

# Pre-populate with test data
products_db = {
    1: {"id": 1, "name": "Laptop", "price": 999.99, "stock": 10, "category": "Electronics"},
    2: {"id": 2, "name": "Mouse", "price": 29.99, "stock": 50, "category": "Electronics"},
    3: {"id": 3, "name": "Keyboard", "price": 79.99, "stock": 30, "category": "Electronics"},
    4: {"id": 4, "name": "Monitor", "price": 299.99, "stock": 15, "category": "Electronics"},
    5: {"id": 5, "name": "Desk", "price": 199.99, "stock": 5, "category": "Furniture"},
    6: {"id": 6, "name": "Desk 1", "price": 299.99, "stock": 15, "category": "Furniture"},
}

# ============================================================================
# Models
# ============================================================================

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    
class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    created_at: str

class ProductResponse(BaseModel):
    id: int
    name: str
    price: float
    stock: int
    category: str

class OrderCreate(BaseModel):
    product_id: int
    quantity: int
    
class OrderResponse(BaseModel):
    id: int
    user_id: int
    product_id: int
    quantity: int
    total_price: float
    status: str
    created_at: str

# ============================================================================
# Authentication (Simplified & Buggy)
# ============================================================================

def get_current_user(authorization: Optional[str] = Header(None)):
    """
    BUG #2: No proper JWT validation, just checks if header exists
    BUG #3: Returns None if no auth, doesn't raise exception
    """
    if not authorization:
        return None
    
    # BUG: Assumes format is "Bearer <user_id>" without validation
    try:
        user_id = int(authorization.replace("Bearer ", ""))
        return users_db.get(user_id)
    except:
        return None

# ============================================================================
# ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "running",
        "message": "Demo E-commerce API - Intentionally Buggy",
        "timestamp": datetime.utcnow().isoformat()
    }

# ----------------------------------------------------------------------------
# USER ENDPOINTS
# ----------------------------------------------------------------------------

@app.post("/api/users/register", response_model=UserResponse)
async def register_user(user: UserCreate):
    """
    Register a new user
    
    BUGS:
    - #4: Password stored in plain text (SECURITY)
    - #5: No email validation
    - #6: No duplicate username check
    """
    user_id = len(users_db) + 1
    
    # BUG: Plain text password storage
    new_user = {
        "id": user_id,
        "username": user.username,
        "email": user.email,
        "password": user.password,  # Should be hashed!
        "created_at": datetime.utcnow().isoformat()
    }
    
    users_db[user_id] = new_user
    
    # Remove password from response
    response = new_user.copy()
    del response["password"]
    
    return response

@app.post("/api/users/login")
async def login_user(username: str, password: str):
    """
    Login user
    
    BUGS:
    - #7: SQL Injection vulnerability (simulated)
    - #8: Returns full user object including password
    """
    # BUG: Simulated SQL injection vulnerability
    # In real app, this would be: f"SELECT * FROM users WHERE username='{username}'"
    
    for user in users_db.values():
        if user["username"] == username and user["password"] == password:
            # BUG: Returns password in response
            return {
                "message": "Login successful",
                "user": user,  # Contains password!
                "token": f"Bearer {user['id']}"  # Weak token
            }
    
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/api/users/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """
    Get current user info
    
    BUG #9: Doesn't check if user is authenticated
    """
    # BUG: No authentication check
    if not current_user:
        # Should raise 401, but returns generic message
        raise HTTPException(status_code=400, detail="Not authenticated")
    
    response = current_user.copy()
    if "password" in response:
        del response["password"]
    
    return response

@app.get("/api/users", response_model=List[UserResponse])
async def list_users(limit: int = Query(100, ge=1, le=1000)):
    """
    List all users (Admin only - but no auth check!)
    
    BUG #10: No admin authorization check
    BUG #11: Potential performance issue with large datasets
    """
    # BUG: No admin check!
    # BUG: N+1 query pattern (simulated)
    
    users = []
    for user in users_db.values():
        # Simulate expensive operation for each user
        time.sleep(0.01)  # BUG: Performance issue
        
        user_copy = user.copy()
        if "password" in user_copy:
            del user_copy["password"]
        users.append(user_copy)
    
    return users[:limit]

# ----------------------------------------------------------------------------
# PRODUCT ENDPOINTS
# ----------------------------------------------------------------------------

@app.get("/api/products", response_model=List[ProductResponse])
async def list_products(
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None
):
    """
    List products with optional filters
    
    This endpoint is GOOD - no intentional bugs
    """
    products = list(products_db.values())
    
    if category:
        products = [p for p in products if p["category"] == category]
    
    if min_price is not None:
        products = [p for p in products if p["price"] >= min_price]
    
    if max_price is not None:
        products = [p for p in products if p["price"] <= max_price]
    
    return products

@app.get("/api/products/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int):
    """
    Get product by ID
    
    BUG #12: No error handling for missing product
    """
    # BUG: Will raise KeyError if product doesn't exist
    return products_db[product_id]  # Should check if exists first!

@app.post("/api/products", response_model=ProductResponse)
async def create_product(
    name: str,
    price: float,
    stock: int,
    category: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new product (Admin only)
    
    BUGS:
    - #13: No admin check
    - #14: No input validation (negative price/stock allowed)
    - #15: No duplicate name check
    """
    # BUG: No admin authorization
    # BUG: No validation for negative values
    
    product_id = max(products_db.keys()) + 1 if products_db else 1
    
    new_product = {
        "id": product_id,
        "name": name,
        "price": price,  # Could be negative!
        "stock": stock,  # Could be negative!
        "category": category
    }
    
    products_db[product_id] = new_product
    
    return new_product

@app.put("/api/products/{product_id}")
async def update_product(
    product_id: int,
    price: Optional[float] = None,
    stock: Optional[int] = None
):
    """
    Update product
    
    BUG #16: Response format changed (API Breaking Change)
    Old format: returned ProductResponse
    New format: returns success message with different structure
    """
    if product_id not in products_db:
        raise HTTPException(status_code=404, detail="Product not found")
    
    product = products_db[product_id]
    
    if price is not None:
        product["price"] = price
    
    if stock is not None:
        product["stock"] = stock
    
    # BUG: Changed response format (breaking change)
    return {
        "success": True,
        "message": "Product updated",
        "updated_product": product  # Different from before!
    }

# ----------------------------------------------------------------------------
# ORDER ENDPOINTS
# ----------------------------------------------------------------------------

@app.post("/api/orders", response_model=OrderResponse)
async def create_order(
    order: OrderCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new order
    
    BUGS:
    - #17: Race condition (no atomic stock update)
    - #18: Incorrect total price calculation
    - #19: No authentication check
    """
    # BUG: No auth check
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # BUG: No product existence check
    product = products_db.get(order.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # BUG: Race condition - stock check and update not atomic
    if product["stock"] < order.quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock")
    
    # BUG: Incorrect calculation (using + instead of *)
    total_price = product["price"] + order.quantity  # Should be *
    
    order_id = len(orders_db) + 1
    
    new_order = {
        "id": order_id,
        "user_id": current_user["id"],
        "product_id": order.product_id,
        "quantity": order.quantity,
        "total_price": total_price,
        "status": "pending",
        "created_at": datetime.utcnow().isoformat()
    }
    
    orders_db[order_id] = new_order
    
    # Update stock (race condition here)
    product["stock"] -= order.quantity
    
    return new_order

@app.get("/api/orders/my", response_model=List[OrderResponse])
async def get_my_orders(current_user: dict = Depends(get_current_user)):
    """
    Get current user's orders
    
    BUG #20: Information disclosure - returns all orders if not authenticated
    """
    # BUG: Returns all orders if no authentication
    if not current_user:
        return list(orders_db.values())  # Leaks all orders!
    
    user_orders = [
        order for order in orders_db.values()
        if order["user_id"] == current_user["id"]
    ]
    
    return user_orders

@app.delete("/api/orders/{order_id}")
async def cancel_order(
    order_id: int,
    current_user: dict = Depends(get_current_user)
):
    """
    Cancel an order
    
    BUGS:
    - #21: No ownership verification
    - #22: Doesn't restore stock
    """
    if order_id not in orders_db:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order = orders_db[order_id]
    
    # BUG: No check if order belongs to current user
    # Any user can cancel any order!
    
    order["status"] = "cancelled"
    
    # BUG: Doesn't restore product stock
    
    return {"message": "Order cancelled", "order_id": order_id}

# ----------------------------------------------------------------------------
# ADMIN ENDPOINTS
# ----------------------------------------------------------------------------

@app.get("/api/admin/stats")
async def get_admin_stats():
    """
    Get platform statistics
    
    BUG #23: No admin authorization
    BUG #24: Exposes sensitive information
    """
    # BUG: Anyone can access admin stats!
    
    return {
        "total_users": len(users_db),
        "total_products": len(products_db),
        "total_orders": len(orders_db),
        "users": list(users_db.values()),  # Includes passwords!
        "revenue": sum(order["total_price"] for order in orders_db.values())
    }

@app.post("/api/admin/reset")
async def reset_database():
    """
    Reset database to initial state
    
    BUG #25: No admin authorization
    BUG #26: No confirmation required
    """
    # BUG: Anyone can reset the database!
    
    global users_db, products_db, orders_db
    
    users_db.clear()
    orders_db.clear()
    
    # Reset products to initial state
    products_db.clear()
    products_db.update({
        1: {"id": 1, "name": "Laptop", "price": 999.99, "stock": 10, "category": "Electronics"},
        2: {"id": 2, "name": "Mouse", "price": 29.99, "stock": 50, "category": "Electronics"},
        3: {"id": 3, "name": "Keyboard", "price": 79.99, "stock": 30, "category": "Electronics"},
        4: {"id": 4, "name": "Monitor", "price": 299.99, "stock": 15, "category": "Electronics"},
        5: {"id": 5, "name": "Desk", "price": 199.99, "stock": 5, "category": "Furniture"},
    })
    
    return {"message": "Database reset successfully"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
