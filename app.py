from flask import Flask, render_template, request, redirect, url_for
from parse_recipe import get_recipe, list_recipe
import json
from dataclasses import asdict

app = Flask(__name__)

@app.route('/')
def home():
    data = list_recipe()
    print(data)
    return render_template('home.html', data=data)

@app.route('/recipe/<path:recipe_name>')
def recipe(recipe_name):
    serve = request.args.get('serve')
    recipe, flames = get_recipe(recipe_name, serve)
    if not recipe:
        return redirect(url_for('home'))
    return render_template('recipe.html',recipe=json.dumps(asdict(recipe), indent=4), flames=flames)

if __name__ == '__main__':
    app.run(debug=True)
