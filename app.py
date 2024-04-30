from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'teste123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce.db'

login_manager = LoginManager()
db = SQLAlchemy(app)
login_manager.init_app(app)
login_manager.login_view = 'login'
CORS(app)

# Modelagem
# Usuário ( id, nome, senha)
class Usuario(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80), nullable=False, unique=True)
    senha = db.Column(db.String(80), nullable=False)


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

# Rotas
# Autenticação
@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(user_id)

@app.route('/login', methods=["POST"])
def login():
    data = request.json
    
    usuario = Usuario.query.filter_by(nome = data.get("nome")).first()

    if usuario and data.get("senha") == usuario.senha:
            login_user(usuario)
            return jsonify({"message": "Bem vindo ao Medication Control"})
    return jsonify({"message": "Credenciais inválidas"}), 401

@app.route('/logout', methods=["POST"])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logout efetuado com sucesso"})

@app.route('/api/medicamento/adicionar', methods=["POST"])
@login_required
def adicionar_medicamento():
    data = request.json
    if 'nome'in data and 'nomeGenerico' in data and 'quantidade' in data and 'medida' in data and 'tipoMedida' in data and 'dataCadastro' in data:
        medicamento = Medicamento(nome=data["nome"], nomeGenerico=data["nomeGenerico"], quantidade=data["quantidade"], medida=data["medida"], tipoMedida=data["tipoMedida"], dataCadastro=data["dataCadastro"], status="Ativo")
        db.session.add(medicamento)
        db.session.commit()
        return jsonify({"message": "Medicamento cadastrado com sucesso"}), 200
    return jsonify({"message": "É necessário preencher os dados obrigatórios"}), 400

@app.route('/api/medicamento/deletar<int:id>', methods=["DELETE"])
@login_required
def deletar_medicamento(id):
    medicamento = Medicamento.query.get(id)
    if medicamento:
        db.session.delete(medicamento)
        db.session.commit()
        return jsonify({"message": "Medicamento deletado com sucesso!"})
    return jsonify({"message": "Medicamento não encontrado"}), 404

@app.route('/api/medicamento/pesquisar<int:id>', methods=["GET"])
@login_required
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
@login_required
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
@login_required
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