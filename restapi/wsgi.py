
"""
	wsgi.py
		-- run as flask wrapper as wsgi application
		-- run as non-root user: ~/miniconda3/bin/mod_wsgi-express start-server wsgi.py &
"""
##################
# FOR PRODUCTION
##################

from src.app import app as application

if __name__ == "__main__":
    ####################
    # FOR DEVELOPMENT
    ####################
    application.run(host='0.0.0.0', debug=True)
