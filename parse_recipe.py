import yaml
from dataclasses import dataclass
from typing import List, Dict, Optional
import re

import math

def almost_equal(a, b, tolerance=1e-9):
    return abs(a - b) < tolerance

@dataclass
class FlameType:
    name: str
    angle: int
    temperature: int

@dataclass
class Ingredient:
    name: str
    quantity: Optional[float] = None
    unit: Optional[str] = None
    note: Optional[str] = None
    sub_ingredients: Optional[List['Ingredient']] = None

@dataclass
class Step:
    instruction: str
    note: Optional[str]=None
    time: Optional[int] = None
    flame_type: Optional[str] = None

@dataclass
class Recipe:
    name: str
    serve_quantity: Optional[float]
    serve_unit: Optional[str]
    ingredients: List[Ingredient]
    steps: List[Step]

def extract_quantity_unit(data):
    if not data: return None, None
    data=str(data)
    pattern = r"(?P<quantity>\d+\.?\d*)\s*(?P<unit>.*)"
    match = re.search(pattern, data)
    
    if match:
        quantity = match.group("quantity")
        unit = match.group("unit")
        return quantity, unit
    else:
        return None, None

def extract_item_note(data):
    pattern = r"(.*?)\[(.*?)\]"
    match = re.search(pattern, data)
    if match:
        item = match.group(1)
        note=match.group(2)
    else:
        item = data
        note = None
    return item, note


class RecipeParser:
    def __init__(self, yaml_content: str):
        self.data = yaml.safe_load(yaml_content)
        self.flames = self._parse_flames(self.data.get('flames', {}))

        self.spice_keywords = {
            'masala', 'spice', 'मसला', 'मसाला',  # masala
            'salt', 'nun', 'नुन', 'नमक',  # salt
            'sugar', 'chini', 'चिनी', 'शक्कर',  # sugar
            
            # Turmeric
            'haldi', 'besar', 'बेसार', 'हल्दी', 'turmeric',
            
            # Chilies and Pepper
            'chilli',
            'khursani', 'खुर्सानी',  # chili (Nepali)
            'mirch', 'मिर्च',  # chili (Hindi)
            'pepper', 'मरिच', 'marich',  # pepper
            'dalchini', 'दालचिनी',  # cinnamon
            
            # Cumin and Coriander
             'jira', 'jeera', 'जीरा', 'cumin', 'जिरा',
            'dhania', 'धनिया', 'coriander', 'धनिया',
            
            # Cardamom
            'cardamom', 'elaichi', 'इलाइची', 'एलैची',
            'सुकमेल', 'sukumel',  # black cardamom
            
            # Ginger and Garlic
            'adhuwa', 'अदुवा', 'अदरक', 'ginger',
            'lasun', 'लसुन', 'garlic', 'लहसुन',
            
            # Other common spices
            'methi', 'मेथी', 'fenugreek',
            'tej patta', 'तेजपत्ता', 'bay leaf',
            'javitri', 'जावित्री', 'mace',
            'jaifal', 'जायफल', 'nutmeg',
            'laung', 'लौंग', 'clove',
            'saunf', 'सौंफ', 'fennel',
            'ajwain', 'अजवाइन', 'carom',
            'kalonji', 'कलौंजी', 'nigella',
            'hing', 'हिंग', 'asafoetida'
        }
        
        # Oil keywords in multiple languages
        self.oil_keywords = {
            # Basic oils
            'tel', 'तेल', 'oil',
            
            # other fats
            'ghee', 'घी', 'घृत', 
            'butter', 'makhan', 'मक्खन', 'नौनी',            
        }
        
    def _parse_flames(self, flames_data: Dict) -> Dict[str, FlameType]:
        flame_types = {}
        for flame_type, details in flames_data.items():
            name = details[0]
            angle = details[1]
            temp = details[2]
            flame_types[flame_type] = FlameType(
                name=name,
                angle=angle,
                temperature=temp
            )
            # for alias in name.split('/'):
            #     flame_types[alias.lower()] = flame_types[flame_type]
        return flame_types
    

    def list_recipe(self):
        recipes={}
        for key,value in self.data.items():
            if key=="flames": continue
            recipes[key]=extract_quantity_unit(value.get('serve', None))
        return recipes

    
    def parse_recipe(self, recipe_name: str) -> Recipe:
        recipe_data = self.data.get(recipe_name, {})
        servings = serve_quantity = serve_unit = str(recipe_data.get('serve', None))
        if servings: serve_quantity, serve_unit = extract_quantity_unit(servings)
        ingredients = self._parse_ingredients(recipe_data.get('ingreds', []))
        steps = self._parse_steps(recipe_data.get('steps', []))
        return Recipe(
            name=recipe_name,
            serve_quantity=serve_quantity,
            serve_unit=serve_unit, 
            ingredients=ingredients,
            steps=steps
        ), self.flames

    def _parse_ingredients(self, ingredients_data: List[Dict]) -> List[Ingredient]:
        ingredients = []
        for ingredient_data in ingredients_data:
            quantity=unit=None
            if isinstance(ingredient_data, str):
                name,note=extract_item_note(ingredient_data)
                ingredients.append(Ingredient(name=name, quantity=quantity, unit=unit, note=note))
            else:
                for key,value in ingredient_data.items():
                    if isinstance(value,list):
                        name,note=extract_item_note(key)
                        sub_ingredients=self._parse_ingredients(value)
                        ingredients.append(Ingredient(name=name, note=note, sub_ingredients=sub_ingredients))
                    else:
                        name,note=extract_item_note(key)
                        quantity, unit=extract_quantity_unit(str(value))
                        ingredients.append(Ingredient(name=name, quantity=quantity, unit=unit, note=note))
        return ingredients
    
    def _parse_steps(self, steps_data: List[Dict]) -> List[Step]:
        steps = []
        last_flame_type=None
        for step_data in steps_data:
            instruction=note=time=new_flame_type=None
            step_data=step_data.split(',')
            instruction, note=extract_item_note(step_data[0])
            if len(step_data) == 2:
                time_or_flame=step_data[1].strip()
                try:
                    time=float(time_or_flame)
                except:
                    new_flame_type=time_or_flame
            elif len(step_data) >= 3:
                try:
                    time=float(step_data[-1])
                    new_flame_type=None
                except:
                    try:
                        time=float(step_data[-2])
                        new_flame_type=step_data[-1]
                    except:
                        time=None
                        new_flame_type=step_data[-1]
                # time=step_data[1].strip()
                # new_flame_type=step_data[2].strip()
            if not new_flame_type:
                new_flame_type = last_flame_type
            else: last_flame_type = new_flame_type = new_flame_type.strip()
            corresponding_flame_name=self.flames.get(new_flame_type, None)
            if corresponding_flame_name: new_flame_type = corresponding_flame_name.name
            else: new_flame_type = None
            if time == None and new_flame_type == None:
                instruction, note=extract_item_note(','.join(step_data))
            steps.append(Step(instruction=instruction, note=note, time=time, flame_type=new_flame_type))
        return steps


    def _scale_ingredient(self, ingredient, scale):
        name =  ingredient.name
        quantity = float(ingredient.quantity)
        scaled_quantity = quantity * float(scale)
        if any(masala for masala in self.spice_keywords if masala in name):
            scaled_quantity *= 0.7
        elif any(oil for oil in self.oil_keywords if oil in name):
            scaled_quantity *= 0.8 
        return scaled_quantity
    
    def scale_recipe(self, recipe, scale):
        scaled_recipe=recipe
        for ingredient in scaled_recipe.ingredients:
            if ingredient.sub_ingredients:
                for sub_ingredient in ingredient.sub_ingredients:
                    if sub_ingredient.quantity:
                        sub_ingredient.quantity = self._scale_ingredient(sub_ingredient, scale)
            if ingredient.quantity:
                ingredient.quantity = self._scale_ingredient(ingredient, scale)
        for step in scaled_recipe.steps:
            if step.time:
                step.time = round(float(step.time) ** .5, 2) 
        return scaled_recipe
            

def get_recipe(recipe_name: str, required_serving_quantity: int=None):
    with open('recipes.yaml', 'r') as f:
        parser = RecipeParser(f.read())
        recipe, flames = parser.parse_recipe(recipe_name)
        json_flames={}
        for f in flames:
            flame=flames[f]
            json_flames[flame.name]={"a":flame.angle,"t":flame.temperature}
        if not recipe.steps:
            return None, None
        if not recipe.serve_quantity or not required_serving_quantity or float(required_serving_quantity) <=0:
            return recipe, json_flames
        recipe_serving_quantity=float(recipe.serve_quantity)
        if not almost_equal(float(required_serving_quantity), float(recipe_serving_quantity)):
            scale = float(required_serving_quantity) / recipe_serving_quantity
            scaled_recipe = parser.scale_recipe(recipe, scale)
            scaled_recipe.serve_quantity=required_serving_quantity
            return scaled_recipe, json_flames
        return recipe, json_flames

def list_recipe():
    with open('recipes.yaml', 'r') as f:
        parser = RecipeParser(f.read())
        return parser.list_recipe()
