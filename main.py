import time
from unicodedata import category
from fastapi import FastAPI, HTTPException, Depends
from datetime import datetime
from schemas import Register, Login, Category, TicketAssignment
from database import get_db_connection
from database import init_db
from auth import create_token, get_current_user, hash_password, verify_password

app = FastAPI()

@app.on_event("startup")
def on_startup():
    init_db()


@app.post("/register")
def register_user(user:Register):
    hashed_password=hash_password(user.password)
    try:
        with get_db_connection() as cur:
            cur.execute("INSERT INTO users (name, email,password,role,created_at,updated_at) VALUES (%s, %s, %s,%s,%s,%s) Returning id", (user.username, user.email, hashed_password,user.role,
                                                                                                                     datetime.now(),datetime.now()))
            return {"message": "User registered successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/login")
def login_user(user: Login):
    try:
        with get_db_connection() as cur:
            cur.execute("SELECT id, password FROM users WHERE email=%s", (user.email,))
            result = cur.fetchone()
            if not result or not verify_password(user.password, result[1]):
                raise HTTPException(status_code=401, detail="Invalid credentials")
            user_id = result[0]
            token = create_token(user_id)
            return {"message": "Login successful", "token": token}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/categories")
def create_category(category: Category, user: int = Depends(get_current_user)):
    try:
        with get_db_connection() as cur:
            # Check if name is provided
            if not category.name:
                raise HTTPException(status_code=400, detail="Category name is required")
                
            cur.execute(
                """
                INSERT INTO categories (user_id, name, description, is_active) 
                VALUES (%s, %s, %s, %s) 
                RETURNING id
                """, 
                (
                    user, 
                    category.name, 
                    category.description, 
                    category.is_active
                )
            )
            category_id = cur.fetchone()[0]
            return {"message": "Category created successfully", "id": category_id}
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# i want to create an endpoint for ticket assignments
@app.post("/ticket_assignments")
def assign_ticket(ticket_assignment: TicketAssignment, user: int = Depends(get_current_user)):
    try:
        with get_db_connection() as cur:
            cur.execute(
                """
                INSERT INTO ticket_assignments (ticket_id, agent_id, assigned_by_id)
                VALUES (%s, %s, %s)
                RETURNING id
                """,
                (
                    ticket_assignment.ticket_id,
                    ticket_assignment.agent_id,
                    user
                )
            )
            assignment_id = cur.fetchone()[0]
            return {"message": "Ticket assigned successfully", "id": assignment_id}
    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e)
        if "foreign key constraint" in error_msg.lower():
            raise HTTPException(status_code=400, detail="Invalid ticket_id or agent_id (referenced record does not exist)")
        raise HTTPException(status_code=500, detail=error_msg)
