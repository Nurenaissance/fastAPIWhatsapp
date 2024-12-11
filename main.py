from fastapi import FastAPI
from config.database import engine, Base
from config.middleware import add_cors_middleware
import contacts.router, node_templates.router, scheduled_events.router, whatsapp_tenant.router
import product.router, dynamic_models.router
import conversations.router, emails

newEvent = False
app = FastAPI()

add_cors_middleware(app)

# Create database tables
Base.metadata.create_all(bind=engine)

app.include_router(contacts.router.router)
app.include_router(node_templates.router.router)
app.include_router(whatsapp_tenant.router.router)
app.include_router(scheduled_events.router.router)
app.include_router(product.router.router)
app.include_router(dynamic_models.router.router)
app.include_router(conversations.router.router)
app.include_router(emails.router)

@app.get("/")
def read_root():
    return {"message": "FastAPI server is running"}
