import streamlit_authenticator as stauth

hashed_passwords = stauth.Hasher([]).hash('akb123')

print(hashed_passwords)
