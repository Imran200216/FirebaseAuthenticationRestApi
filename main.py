from fastapi import FastAPI
from pydantic import BaseModel
from firebase_config import db
from firebase_admin import auth
from datetime import datetime
import uuid

app = FastAPI()


@app.get("/hello_world")
def hello_world():
    return {"message": "Firebase Guest and Google Auth in FastAPI"}


# guest user modal
class GuestUser(BaseModel):
    uid: str


# sign in with guest auth
@app.post("/signInWithGuest")
def sign_in_with_guest():
    try:
        # Create a random UID
        random_uid = f"guest_{uuid.uuid4().hex}"

        # Create Firebase user
        user = auth.create_user(uid=random_uid)

        # current time stamp
        singed_in_at = datetime.utcnow()

        # Store in Firestore
        db.collection("guests").document(random_uid).set({
            "uid": random_uid,
            "type": "anonymous",
            "signedInAt": singed_in_at.isoformat(),
        })

        return {
            "message": "Guest user created successfully",
            "uid": random_uid,
            "signedInAt": singed_in_at.isoformat()
        }

    except Exception as e:
        return {
            "error": str(e),
            "message": "Guest sign-in failed"
        }


class GoogleToken(BaseModel):
    id_token: str


# sign in with google auth
@app.post("/signInWithGoogle")
def sign_in_with_google(payload: GoogleToken):
    try:
        print("Received ID Token:", payload.id_token)  # Debugging line

        decoded_token = auth.verify_id_token(payload.id_token)
        print("Decoded token:", decoded_token)  # Debugging line

        uid = decoded_token.get("uid")
        email = decoded_token.get("email")
        name = decoded_token.get("name")
        picture = decoded_token.get("picture")

        user_doc_ref = db.collection("googleUsers").document(uid)
        doc = user_doc_ref.get()

        if not doc.exists:
            user_doc_ref.set({
                "uid": uid,
                "email": email,
                "name": name,
                "picture": picture,
                "type": "google"
            })

        return {
            "message": "Google sign-in successful",
            "uid": uid,
            "email": email,
            "name": name,
            "picture": picture
        }

    except Exception as e:
        print("Google sign-in error:", str(e))
        return {
            "message": "Google sign-in failed",
            "error": str(e)
        }