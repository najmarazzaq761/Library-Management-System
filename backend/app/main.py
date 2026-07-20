from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import init_db, seed_data
from app.routers import auth, books, loans, notifications, members


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Run migrations and seed data on startup
    try:
        init_db()
        seed_data()
    except Exception as e:
        print(f"Error during database initialization/seeding: {e}")
    yield


app = FastAPI(title="Library Management API", lifespan=lifespan)

# CORS middleware config
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth.router)
app.include_router(books.router)
app.include_router(loans.router)
app.include_router(notifications.router)
app.include_router(members.router)
