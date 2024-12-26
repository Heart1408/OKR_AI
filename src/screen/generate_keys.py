import streamlit_authenticator as stauth

hashed_passwords = stauth.Hasher([]).hash('password') # change password to the password you want to hash

print(hashed_passwords)
