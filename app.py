from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.security import check_password_hash
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user
from datetime import datetime, date
from werkzeug.security import generate_password_hash

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
    
    usuario = Usuario.query.filter_by(nome=data.get("nome")).first()

    if usuario and check_password_hash(usuario.senha, data.get("senha")):
        login_user(usuario)
        return jsonify({"message": "Bem vindo ao Medication Control"})
    
    return jsonify({"message": "Credenciais inválidas"}), 401

@app.route('/logout', methods=["POST"])
# @login_required
def logout():
    logout_user()
    return jsonify({"message": "Logout efetuado com sucesso"})

@app.route('/api/medicamento/adicionar', methods=["POST"])
# @login_required
def adicionar_medicamento():
    try:
        data = request.json

        if isinstance(data.get("dataCadastro"), str):
            data["dataCadastro"] = datetime.strptime(data["dataCadastro"], "%Y-%m-%d").date()

        if "dataAtualizacao" in data and isinstance(data["dataAtualizacao"], str):
            data["dataAtualizacao"] = datetime.strptime(data["dataAtualizacao"], "%Y-%m-%d").date()
        else:
            data["dataAtualizacao"] = date.today()

        obrigatorios = ["nome", "nomeGenerico", "quantidade", "medida", "tipoMedida", "dataCadastro", "status"]
        if not all(campo in data for campo in obrigatorios):
            return jsonify({"message": "É necessário preencher todos os dados obrigatórios"}), 400

        medicamento = Medicamento(
            nome=data["nome"],
            nomeGenerico=data["nomeGenerico"],
            quantidade=data["quantidade"],
            medida=data["medida"],
            tipoMedida=data["tipoMedida"],
            dataCadastro=data["dataCadastro"],
            dataAtualizacao=data["dataAtualizacao"],
            status=data["status"]
        )

        db.session.add(medicamento)
        db.session.commit()

        return jsonify({"message": "Medicamento cadastrado com sucesso"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/medicamento/deletar/<int:id>', methods=["DELETE"])
# @login_required
def deletar_medicamento(id):
    try:
        medicamento = Medicamento.query.get(id)
        if not medicamento:
            return jsonify({"message": "Medicamento não encontrado"}), 404
        if medicamento:
            db.session.delete(medicamento)
            db.session.commit()
            return jsonify({"message": "Medicamento deletado com sucesso!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
        


@app.route('/api/medicamento/pesquisar/<int:id>', methods=["GET"])
# @login_required
def pesquisar_medicamento_id(id):
    try:
        medicamento = Medicamento.query.get(id)
        if not medicamento:
            return jsonify({"message": "Medicamento não encontrado"}), 404
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
    except Exception as e:
        return jsonify({"error": "Erro ao processar a requisição", "details": str(e)}), 500

@app.route('/api/medicamento/atualizar/<int:id>', methods=["PUT"])
# @login_required
def atualizar_medicamento(id):
    medicamento = Medicamento.query.get(id)
    if not medicamento:
        return jsonify({"message": "Medicamento não encontrado"}), 404
    
    data = request.json
    
    if not data:
        return jsonify({"message": "Nenhum dado fornecido"}), 400

    if 'nome' in data:
        medicamento.nome = data['nome']

    if 'nomeGenerico' in data:
        medicamento.nomeGenerico = data['nomeGenerico']

    if 'quantidade' in data:
        medicamento.quantidade = data['quantidade']
    
    if 'medida' in data:
        medicamento.medida = data['medida']

    if 'tipoMedida' in data:
        medicamento.tipoMedida = data['tipoMedida']

    if 'status' in data:
        medicamento.status = data['status']

    medicamento.dataAtualizacao = datetime.utcnow()

    try:
        db.session.commit()
        return jsonify({"message": "Medicamento atualizado com sucesso"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Erro ao atualizar medicamento: {str(e)}"}), 500
    
@app.route('/api/medicamentos', methods=['GET'])
# @login_required
def pesquisa_medicamentos():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        medicamentos = Medicamento.query.paginate(page, per_page, error_out=False)

        medicamento_list = []
        for medicamento in medicamentos.items:
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
        
        return jsonify({
            "medicamentos": medicamento_list,
            "total": medicamentos.total,
            "pages": medicamentos.pages,
            "current_page": medicamentos.page
        })

    except Exception as e:
        return jsonify({"message": f"Erro ao recuperar medicamentos: {str(e)}"}), 500


# Definição de rota raiz
@app.route('/')
def hello_world():
    return "Testando Hello"

if __name__ == "__main__":
    app.run(debug=True)