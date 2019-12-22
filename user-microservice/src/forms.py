from pydantic import BaseModel, validator

class NewUser(BaseModel):

    username:str
    password:str
    password_confirmation:str
    email:str

    @validator('password_confirmation')
    def password_has_to_match(cls, v, values):

        if values['password'] != v:
            raise ValueError("Password confirmation does't match password")
        
