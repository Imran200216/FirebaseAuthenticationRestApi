import firebase_admin
from firebase_admin import credentials, firestore

# service account
cred = credentials.Certificate("serviceAccountKey.json")

# initialize the firebase app once
firebase_admin.initialize_app(cred, {
    "projectId": "mathpuzzle-a9cc3",
})

# firestore db instance
db = firestore.client()