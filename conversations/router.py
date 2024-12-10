from fastapi import APIRouter, Request, Depends, HTTPException, Header, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound
from config.database import get_db
from .models import Conversation
from models import Tenant
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import json
from typing import Optional

router = APIRouter()

def decrypt_data(encrypted_data: bytes, key: bytes):
    # Extract the IV from the first 16 bytes
    iv = encrypted_data[:16]
    encrypted_data = encrypted_data[16:]

    # Ensure the key is in bytes (handle memoryview if needed)
    if isinstance(key, memoryview):
        key = bytes(key)

    # Initialize the cipher
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()

    # Perform decryption
    decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()

    # Remove padding (PKCS#7 padding)
    pad_len = decrypted_data[-1]
    decrypted_data = decrypted_data[:-pad_len]

    return json.loads(decrypted_data.decode())

@router.get("/whatsapp_convo_get/{contact_id}")
async def view_conversation(
    contact_id: Optional[str],
    source: Optional[str] = Query(None),
    bpid: Optional[str] = Query(None),
    x_tenant_id: str = Header(...),
    db: Session = Depends(get_db)
):
    try:
        # Fetch tenant and encryption key
        tenant = db.query(Tenant).filter(Tenant.id == x_tenant_id).one_or_none()
        if not tenant:
            raise HTTPException(status_code=404, detail="Tenant not found")
        encryption_key = tenant.key

        print(contact_id, bpid, source)

        # Query conversations for the contact_id
        conversations = (
            db.query(Conversation)
            .filter(
                Conversation.contact_id == contact_id,
                Conversation.business_phone_number_id == bpid,
                Conversation.source == source,
            )
            .order_by(Conversation.date_time)
            .all()
        )
        
        print("Conversations: ", conversations)

        # Format the conversations
        formatted_conversations = []
        for conv in conversations:
            text_to_append = conv.message_text
            encrypted_text = conv.encrypted_message_text

            if encrypted_text is not None:
                decrypted_text = decrypt_data(bytes(encrypted_text), key=encryption_key)
                print("Decrypted text: ", decrypted_text)
                if decrypted_text:
                    decrypted_text = json.dumps(decrypted_text)
                    text_to_append = decrypted_text.strip('"') if decrypted_text.startswith('"') else decrypted_text

            formatted_conversations.append({
                "text": text_to_append,
                "sender": conv.sender,
            })

        return formatted_conversations

    except NoResultFound:
        raise HTTPException(status_code=404, detail="Data not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error while fetching data: {str(e)}")
