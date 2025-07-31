import requests
from flask import Flask, render_template, request, redirect, url_for, flash, session
import json
import os
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'chave_super_secreta_padrao_dev')

@app.route("/", methods=["GET"])
def index():
    etapa_url = request.args.get("etapa")

    if not request.referrer:
        session.clear()

    etapa = etapa_url or session.get("etapa", "cadastro")
    return render_template("index.html", etapa=etapa)

@app.route("/cadastro", methods=["POST"])
def cadastro():
    data = request.form
    
    # Log dos dados recebidos (sem senha por segurança)
    logger.info(f"Dados recebidos: username={data.get('username')}, cpf={data.get('cpf')}, telefone={data.get('telefone')}")

    payload = {
        "nome": data.get("username"),
        "sobrenome": "",
        "username": data.get("username"),
        "cpf": data.get("cpf").replace(".", "").replace("-", ""),
        "email": "",
        "telefone": data.get("telefone").replace("(", "").replace(")", "").replace("-", "").replace(" ", ""),
        "genero_id": 0,
        "publicidades": 1,
        "data_nascimento": "",
        "senha": data.get("senha"),
        "action_recaptcha": "REGISTER",
        "latitude": 0,
        "longitude": 0,
        "os": "Linux x86_64",
        "platform": "Brazil",
        "afiliado_id": 1
    }

    try:
        logger.info("Enviando requisição para a API externa...")
        response = requests.post(
            "https://landing-teste.supercacheta.com/supercacheta/sign-up?domain=cadastro.supercacheta.com",
            json=payload,
            timeout=30  # Timeout de 30 segundos
        )

        logger.info(f"📡 Status code: {response.status_code}")

        try:
            result = response.json()
        except ValueError as e:
            logger.error(f"❌ A resposta não é JSON! Erro: {e}")
            logger.error(f"📥 Resposta bruta: {response.text}")
            flash("Erro inesperado no cadastro.")
            return redirect(url_for("index"))

        logger.info(f"📥 Conteúdo da resposta (JSON): {result}")

        if response.status_code == 200 and "token" in result:
            session["token"] = result["token"]
            session["documents"] = result["documents"]
            session["nome"] = data.get("username")
            session["username"] = data.get("username")
            session["cpf"] = data.get("cpf").replace(".", "").replace("-", "")

            for doc in result["documents"]:
                if doc["tipo_documento_id"] == 4:
                    session["id_sms"] = doc["id"]
                elif doc["tipo_documento_id"] == 5:
                    session["id_whatsapp"] = doc["id"]

            flash("Validação da sua conta!", "sucesso")
            return render_template("index.html", etapa="verificacao")
        else:
            mensagem = result.get("user_message", "Erro ao cadastrar.")
            logger.warning(f"Erro da API: {mensagem}")
            flash(f"❌ {mensagem}", "erro")
            return redirect(url_for("index"))

    except requests.exceptions.Timeout:
        logger.error("❌ Timeout na conexão com a API")
        flash("Erro de conexão: tempo limite excedido.")
        return redirect(url_for("index"))
    except requests.exceptions.ConnectionError:
        logger.error("❌ Erro de conexão com a API")
        flash("Erro de conexão com o servidor.")
        return redirect(url_for("index"))
    except Exception as e:
        logger.error(f"❌ Exceção na conexão: {str(e)}")
        flash("Erro de conexão com o servidor.")
        return redirect(url_for("index"))

@app.route("/enviar-codigo", methods=["POST"])
def enviar_codigo():
    metodo = request.form.get("metodo_envio")
    token = session.get("token")

    if not token:
        flash("Token de cadastro não encontrado.", "erro")
        return redirect(url_for("index"))

    validacao_id = session.get("id_sms") if metodo == "sms" else session.get("id_whatsapp") if metodo == "whatsapp" else None

    if not validacao_id:
        flash("Método de envio inválido.", "erro")
        return redirect(url_for("index"))

    payload = {
        "pre_cadastro_validacao_id": validacao_id,
        "token": token
    }

    try:
        logger.info(f"Enviando código via {metodo}...")
        response = requests.post(
            "https://landing-teste.supercacheta.com/supercacheta/sign-up/request-validation?domain=cadastro.supercacheta.com",
            json=payload,
            timeout=30
        )
        result = response.json()

        logger.info(f"📨 Envio do código - Status: {response.status_code}")
        logger.info(f"📨 Resposta da API: {result}")

        if response.status_code == 200:
            flash("📩 Código enviado com sucesso via " + metodo.upper(), "sucesso")
            session["etapa"] = "codigo"
            session["id_validacao"] = validacao_id
        else:
            mensagem = result.get("user_message", "Erro ao enviar código.")
            flash("❌ " + mensagem, "erro")

    except requests.exceptions.Timeout:
        logger.error("❌ Timeout ao enviar código")
        flash("Erro de conexão: tempo limite excedido ao enviar código.", "erro")
    except requests.exceptions.ConnectionError:
        logger.error("❌ Erro de conexão ao enviar código")
        flash("Erro de conexão ao enviar o código.", "erro")
    except Exception as e:
        logger.error(f"❌ Erro ao enviar código: {str(e)}")
        flash("Erro de conexão ao enviar o código.", "erro")

    return redirect(url_for("index"))

@app.route("/validar-codigo", methods=["POST"])
def validar_codigo():
    token = session.get("token")
    doc_id = session.get("id_validacao")
    codigo = request.form.get("codigo")

    if not all([token, doc_id, codigo]):
        flash("❌ Dados incompletos para validação.", "erro")
        return redirect(url_for("index"))

    payload = {
        "token": token,
        "pre_cadastro_validacao_id": doc_id,
        "codigo": codigo
    }

    try:
        logger.info("Validando código...")
        response = requests.post(
            "https://landing-teste.supercacheta.com/supercacheta/sign-up/validate?domain=cadastro.supercacheta.com",
            json=payload,
            timeout=30
        )
        result = response.json()

        logger.info(f"✅ Validação do código - Status: {response.status_code}")
        logger.info(f"📥 Resposta da API: {result}")

        if response.status_code == 200:
            flash("✅ Código validado com sucesso!", "sucesso")
            return redirect(url_for("ativar_conta"))
        else:
            mensagem = result.get("user_message", "Erro ao validar o código.")
            flash("❌ " + mensagem, "erro")

    except requests.exceptions.Timeout:
        logger.error("❌ Timeout ao validar código")
        flash("Erro de conexão: tempo limite excedido ao validar código.", "erro")
    except requests.exceptions.ConnectionError:
        logger.error("❌ Erro de conexão ao validar código")
        flash("Erro de conexão ao validar código.", "erro")
    except Exception as e:
        logger.error(f"❌ Erro ao validar código: {str(e)}")
        flash("Erro de conexão ao validar código.", "erro")

    return redirect(url_for("index"))

@app.route("/ativar-conta")
def ativar_conta():
    token = session.get("token")

    if not token:
        flash("❌ Token não encontrado.", "erro")
        return redirect(url_for("index"))

    payload = {
        "token": token,
        "localidade_id": 94,
        "moeda_id": 1,
        "os": "Linux x86_",
        "platform": "Brazil"
    }

    logger.info("📦 Payload enviado para ativação:")
    logger.info(json.dumps(payload, indent=2, ensure_ascii=False))

    try:
        logger.info("Ativando conta...")
        response = requests.post(
            "https://landing-teste.supercacheta.com/supercacheta/sign-up/activate?domain=cadastro.supercacheta.com",
            json=payload,
            timeout=30
        )
        result = response.json()

        logger.info(f"🚀 Ativação - Status: {response.status_code}")
        logger.info(f"🚀 Resultado: {result}")

        if response.status_code == 200:
            flash("🎉 Conta ativada com sucesso!", "sucesso")
            return redirect(url_for("index", etapa="sucesso"))
        else:
            mensagem = result.get("user_message", "Erro ao ativar a conta.")
            flash("❌ " + mensagem, "erro")
            return redirect(url_for("index"))

    except requests.exceptions.Timeout:
        logger.error("❌ Timeout na ativação")
        flash("Erro de conexão: tempo limite excedido ao ativar conta.", "erro")
        return redirect(url_for("index"))
    except requests.exceptions.ConnectionError:
        logger.error("❌ Erro de conexão na ativação")
        flash("Erro ao ativar a conta.", "erro")
        return redirect(url_for("index"))
    except Exception as e:
        logger.error(f"❌ Erro na ativação: {str(e)}")
        flash("Erro ao ativar a conta.", "erro")
        return redirect(url_for("index"))

@app.route("/sucesso")
def sucesso():
    return render_template("sucesso.html")


