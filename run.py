import connexion
from flask.ext.cors import CORS

app = connexion.App(__name__, specification_dir='swagger/')
app.add_api('swagger.yaml')
#application = app.app
cors = CORS(app.app, resources={r"/v1/*": {"origins": "*"}})
app.run(port=80)