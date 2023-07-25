from flask import Flask, request, jsonify
from sqlalchemy import create_engine, Column, Integer, String, LargeBinary
from sqlalchemy.orm import declarative_base, sessionmaker

from flask_cors import CORS

import base64

app = Flask(__name__)
CORS(app)
Base = declarative_base()

engine = create_engine('sqlite:///northwind.db')
Session = sessionmaker(bind=engine)

class Categoria(Base):
    __tablename__ = 'categories'
    CategoryID = Column(Integer, primary_key=True)
    CategoryName = Column(String)
    Description = Column(String, nullable=True)
    Picture = Column(LargeBinary, nullable=True)

Base.metadata.create_all(engine)


#Consultar
@app.route('/', methods=['GET'])
def obtener_categorias():
    session = Session()
    categorias = session.query(Categoria).all()
    session.close()
    result = []
    for cat in categorias:
        if cat.Picture is not None:
            picture_base64 = base64.b64encode(cat.Picture).decode('utf-8')
        else:
            picture_base64 = None
        
        result.append({
            "CategoryID": cat.CategoryID,
            "CategoryName": cat.CategoryName,
            "Description": cat.Description,
            "Picture": picture_base64
        })
    return jsonify(result)

@app.route('/<int:id>', methods=['GET'])
def obtener_categoria(id):
    session = Session()
    categoria = session.query(Categoria).filter_by(CategoryID=id).first()
    session.close()
    if categoria:
        result = []
        if categoria.Picture is not None:
            picture_base64 = base64.b64encode(categoria.Picture).decode('utf-8')
        else:
            picture_base64 = None
        
        result.append({
            "CategoryID": categoria.CategoryID,
            "CategoryName": categoria.CategoryName,
            "Description": categoria.Description,
            "Picture": picture_base64
        })
        return jsonify(result)
    return jsonify({"mensaje": "Categoría no encontrada"}), 404


# Crear
@app.route('/', methods=['POST'])
def crear_categoria():
    data = request.get_json()
    if 'CategoryName' in data:
        nueva_categoria = Categoria(CategoryName=data['CategoryName'])
        if 'Description' in data:
            nueva_categoria.Description = data['Description']
        if 'Picture' in data:
            nueva_categoria.Picture = base64.b64decode(data['Picture'])
        session = Session()
        session.add(nueva_categoria)
        session.commit()

        nueva_categoria_data = {
            "CategoryID": nueva_categoria.CategoryID,
            "CategoryName": nueva_categoria.CategoryName,
            "Description": nueva_categoria.Description,
            "Picture": base64.b64encode(nueva_categoria.Picture).decode('utf-8') if nueva_categoria.Picture else None
        }

        session.close()

        return jsonify(nueva_categoria_data), 201
    return jsonify({"mensaje": "El campo 'CategoryName' es requerido"}), 400


# Actualizar
@app.route('/<int:id>', methods=['PUT'])
def actualizar_categoria(id):
    data = request.get_json()
    session = Session()
    categoria = session.query(Categoria).filter_by(CategoryID=id).first()
    if categoria:
        if 'CategoryName' in data:
            categoria.CategoryName = data['CategoryName']
        if 'Description' in data:
            categoria.Description = data['Description']
        if 'Picture' in data and data['Picture']:
            categoria.Picture = base64.b64decode(data['Picture'])

        categoria_actualizada = session.merge(categoria)
        session.commit()

        categoria_actualizada = session.query(Categoria).filter_by(CategoryID=id).first()
        session.close()

        return jsonify({
            "CategoryID": categoria_actualizada.CategoryID,
            "CategoryName": categoria_actualizada.CategoryName,
            "Description": categoria_actualizada.Description,
            "Picture": base64.b64encode(categoria_actualizada.Picture).decode('utf-8') if categoria_actualizada.Picture else None
        }), 200 

    session.close()
    return jsonify({"mensaje": "Categoría no encontrada"}), 404

# Eliminar
@app.route('/<int:id>', methods=['DELETE'])
def eliminar_categoria(id):
    session = Session()
    categoria = session.query(Categoria).filter_by(CategoryID=id).first()
    if categoria:
        session.delete(categoria)
        session.commit()
        session.close()
        return jsonify({"mensaje": "Categoría eliminada correctamente"})
    session.close()
    return jsonify({"mensaje": "Categoría no encontrada"}), 404

if __name__ == '__main__':
    app.run(debug=True)
