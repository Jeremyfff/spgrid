from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/helloworld', methods=['GET'])
def testVue():
    temp = request.values.get("temperature")


    message = f'Hello, world! {temp}'
    return message


app.run(host="0.0.0.0",port=36843)