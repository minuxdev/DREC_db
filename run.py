from re import DEBUG
from app import app
from controlers.routes import *


if __name__ == "__main__":
    app.run(debug=True)