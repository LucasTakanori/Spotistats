from flask import jsonify
from flask import dumps
import flask

@app.route("/api/v1/users", methods=['GET'])
def fetch_users():
    try:
        query_params = helper_module.parse_query_params(request.query_string)
        if query_params:
            query = {k: int(v) if isinstance(v, str) and v.isdigit() else v for k, v in query_params.items()}
            records_fetched = collection.find(query)
            if records_fetched.count() > 0:
                return dumps(records_fetched)
            else:
                return "", 404
        else:
            if collection.find().count() > 0:
                return dumps(collection.find())
            else:
                return jsonify([])
    except:
        return "", 500

@app.errorhandler(404)
def page_not_found(e):
    message = {
        "err":
            {
                "msg": "This route is currently not supported. Please refer API documentation."
            }
    }
    resp = jsonify(message)
    resp.status_code = 404
    return resp
