#hello darkness my old friend
from datetime import timedelta
from flask import Flask
from flask_cors import CORS
import os
from models import *
from extensions import db, cache, jwt



def create_app():
    app=Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///parking.db'
    app.config["JWT_SECRET_KEY"] = "l1997"
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)

    #caching
    app.config["CACHE_TYPE"]="RedisCache"
    app.config["CACHE_REDIS_URL"]='redis://localhost:6379/0'
    

    #enabling cors
    CORS(app, supports_credentials=True, resources={
        r"/*": {
            "origins": ["http://localhost:5173"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    #initializing extensions
    db.init_app(app)
    jwt.init_app(app)
    cache.init_app(app)
    
    #registering resources
    from controllers import initialize_resources
    api=initialize_resources(app)

    #creating database
    with app.app_context():
        if not os.path.exists("parking.db"):
            print("Creating database...")
            
            db.create_all()
        from models import create_admin_user
        create_admin_user()
    
    return app

app=create_app()
if __name__=="__main__":
    app.run(debug=True)