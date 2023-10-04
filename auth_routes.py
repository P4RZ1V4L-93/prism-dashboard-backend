'''
    This script is responsible for user authentication. It contains routes for user registration (signup) and user login
'''

# Import necessary modules and dependencies
from fastapi import APIRouter, status, Depends
from fastapi_jwt_auth import AuthJWT
from schemas import SignUpSchema, LoginSchema,SignUpResponseSchema,LoginResponseSchema, ErrorResonseSchema
from database import Session, engine
from models import User
from fastapi.exceptions import HTTPException
from werkzeug.security import generate_password_hash, check_password_hash
from fastapi.encoders import jsonable_encoder

# Create an APIRouter for authentication-related routes
auth_router = APIRouter(
    prefix='/auth',
    tags=['Authorization End Points']
)

# Create an SQLAlchemy session bound to the engine
session = Session(bind=engine)


# Define a FastAPI route for user registration (signup)
@auth_router.post("/signup",response_model=SignUpResponseSchema, status_code=status.HTTP_201_CREATED, responses={400: {"description": "Bad Request", "model": ErrorResonseSchema}, 201: {"description": "Registered the user"}})
def signup(user: SignUpSchema):
    """
        ## Register the User
        This endpoint requires the following
        - user: SignUpSchema
        
    """

    # check if the provided email already exists in the database
    db_email = session.query(User).filter(User.email == user.email).first()

    if (db_email is not None):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="User with the email already exists")

    # Check if the provided username already exists in the database
    db_username = session.query(User).filter(
        User.username == user.username).first()

    if (db_username is not None):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="User with the username already exists")

    # create the new user

    new_user = User(
        username=user.username,
        email=user.email,
        password=generate_password_hash(user.password),
    )

    # add new user to table
    session.add(new_user)
    session.commit()

    # response object
    response = {
        "id": new_user.id,
        "username": new_user.username,
        "email": new_user.email,
    }

    # return the response in json format
    return response


# Define a FastAPI route for user login (login)
@auth_router.post("/login", responses={400: {"description": "Bad Request", "model": ErrorResonseSchema}})
async def login(user: LoginSchema, Authorize: AuthJWT = Depends()):

    """
        ## Login the User
        This is protected endpoint and requires the following
        - user: LoginSchema

    """

    # Query the database for a user with the provided email
    db_user = session.query(User).filter(User.email == user.email).first()

    # Check if a user with the provided email exists and the password matches
    if db_user and check_password_hash(db_user.password, user.password):
        access_token = Authorize.create_access_token(subject=db_user.email)
        response = {
            "accessToken": access_token
        }
        return jsonable_encoder(response)
    else:
        # Return an error message if authentication fails
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                             detail="Invalid username or password"
                             )
