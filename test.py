from jose import jwt

SECRET_KEY = '2nXGNMkA_wye3VgbduZtd1YvttLXUrOF4p-qYxQr4lY='
ALGORITHM = 'HS256'
token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwiZXhwIjoxNzQxMDM4Mjg0LCJ0eXBlIjoicmVmZXJyYWwifQ.lZ5mV5-eaG6e-eONPW8e8GvGWX9X4T3ezY-fIw9e9dQ' 
payload = jwt.decode(token, SECRET_KEY, ALGORITHM)

i = payload.get('sub')

print(i)