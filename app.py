from flask import Flask, jsonify, request

from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce.db'

db = SQLAlchemy(app)

# Modelagem
# Medicamento (id, nome, nomeGenerico, quantidade, medida, tipoMedida, dataCadastro, status)

class Medicamento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False)
    nomeGenerico = db.Column(db.String(50), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)
    medida = db.Column(db.Integer, nullable=False)
    tipoMedida = db.Column(db.String(10), nullable=False) 
    dataCadastro = db.Column(db.Date, nullable=False)
    dataAtualizacao = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(10), nullable=False)

@app.route('/api/medicamento/adicionar', methods=["POST"])
def adicionar_medicamento():
    data = request.json
    if 'nome'in data and 'nomeGenerico' in data and 'quantidade' in data and 'medida' in data and 'tipoMedida' in data and 'dataCadastro' in data:
        medicamento = Medicamento(nome=data["nome"], nomeGenerico=data["nomeGenerico"], quantidade=data["quantidade"], medida=data["medida"], tipoMedida=data["tipoMedida"], dataCadastro=data["dataCadastro"], status="Ativo")
        db.session.add(medicamento)
        db.session.commit()
        return jsonify({"message": "Medicamento cadastrado com sucesso"}), 200
    return jsonify({"message": "É necessário preencher os dados obrigatórios"}), 400

@app.route('/api/medicamento/deletar<int:id>', methods=["DELETE"])
def deletar_medicamento(id):
    medicamento = Medicamento.query.get(id)
    if medicamento:
        db.session.delete(medicamento)
        db.session.commit()
        return jsonify({"message": "Medicamento deletado com sucesso!"})
    return jsonify({"message": "Medicamento não encontrado"}), 404

@app.route('/api/medicamento/pesquisar<int:id>', methods=["GET"])
def pesquisar_medicamento_id(id):
    medicamento = Medicamento.query.get(id)
    if medicamento:
        return jsonify({
            "id": medicamento.id,
            "nome": medicamento.nome,
            "nomeGenerico": medicamento.nomeGenerico,
            "quantidade": medicamento.quantidade,
            "medida": medicamento.medida,
            "tipoMedida": medicamento.tipoMedida,
            "dataCadastro": medicamento.dataCadastro,
            "dataAtualizacao": medicamento.dataAtualizacao,
            "status": medicamento.status
        })
    return jsonify({"message": "Medicamento não encontrado"}), 404

@app.route('/api/medicamento/atualizar<int:id>', methods=["PUT"])
def atualizar_medicamento(id):
    medicamento = Medicamento.query.get(id)
    if not medicamento:
        return jsonify({"message": "Medicamento não encontrado"}), 404
    
    data = request.json
    if 'nome' in data:
        medicamento.nome = data['nome']

    if 'nomeGenerico' in data:
        medicamento.nomeGenerico = data['nomeGenerico']

    if 'quantidade' in data:
        medicamento.quantidade = data['quantidade']
    
    if 'medida'in data:
        medicamento.medida = data['medida']

    if 'tipoMedida'in data:
        medicamento.tipoMedida = data['tipoMedida']

    if 'dataAtualizacao'in data:
        medicamento.dataAtualizacao = data['dataAtualizacao']

    if 'status'in data:
        medicamento.status = data['status']

    db.session.commit()
    return jsonify({"message": "Medicamento atualizado com sucesso"})

@app.route('/api/medicamentos', methods=['GET'])
def pequisa_medicamentos():
    medicamentos = Medicamento.query.all()
    medicamento_list = []
    for medicamento in medicamentos:
        medicamento_data = {
            "id": medicamento.id,
            "nome": medicamento.nome,
            "nomeGenerico": medicamento.nomeGenerico,
            "quantidade": medicamento.quantidade,
            "medida": medicamento.medida,
            "tipoMedida": medicamento.tipoMedida,
            "dataCadastro": medicamento.dataCadastro,
            "dataAtualizacao": medicamento.dataAtualizacao,
            "status": medicamento.status
        }
        medicamento_list.append(medicamento_data)
    
    return jsonify(medicamento_list)
# Definição de rota raiz
@app.route('/')
def hello_world():
    return "Testando Hello"

if __name__ == "__main__":
    app.run(debug=True)