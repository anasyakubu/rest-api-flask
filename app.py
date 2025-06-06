from flask import Flask

app = Flask(__name__)

stores = [
  {
    'name': 'My Wonderful Store',
    'items': [
      {
        'name': 'My Item',
        'price': 15.99
      },
      {
        'name': 'My Item 2',
        'price': 16.99
      },
      {
        'name': 'My Item 3',
        'price': 17.99
      },
    ]
  },
]

@app.get("/stores") # http://127.0.0.1:5000/stores
def get_stores():
    return {'stores': stores}