from dashcelltypeviewer import create_app

###########################################################
# This run.py will work for local testing of the dash app #
###########################################################

if __name__ == "__main__":
    app = create_app()
    app.run_server(port=8050)
