from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route('/proxy', methods=['GET', 'POST'])
def proxy():
    # Retrieve the target URL from the request
    target_url = request.args.get('url')
    
    if not target_url:
        return jsonify({"error": "Missing target URL parameter"}), 400

    # Forward the request to the target server
    try:
        if request.method == 'GET':
            response = requests.get(target_url, headers=request.headers)
        elif request.method == 'POST':
            response = requests.post(target_url, headers=request.headers, data=request.get_data())
        else:
            return jsonify({"error": "Unsupported HTTP method"}), 400

        # Return the target server's response to the client
        return response.content, response.status_code, {'Content-Type': response.headers['Content-Type']}
    except requests.RequestException as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
