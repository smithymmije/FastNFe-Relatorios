from flask import Flask, render_template, request
import xml.etree.ElementTree as ET
from datetime import datetime
import locale

app = Flask(__name__)

# Define o locale para português do Brasil para formatação de datas
try:
    locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
except locale.Error:
    print("Erro ao configurar o locale para pt_BR.UTF-8. Verifique se está instalado no sistema.")

# Função para extrair texto de um elemento XML de forma segura
def safe_find_text(element, path, namespaces=None):
    found = element.find(path, namespaces)
    return found.text if found is not None else "Não encontrado"

# Função para formatar a data no formato brasileiro (dd/mm/aaaa)
def formatar_data_para_brasileiro(data_original):
    try:
        data_formatada = datetime.strptime(data_original.split('T')[0], '%Y-%m-%d').strftime('%d/%m/%Y')
        return data_formatada
    except ValueError:
        return data_original

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_report_select():
    if 'file' not in request.files:
        return "Nenhum arquivo enviado", 400
    file = request.files['file']

    if file.filename == '':
        return "Nenhum arquivo selecionado", 400

    if file:
        try:
            tree = ET.parse(file)
            root = tree.getroot()
            print("XML processado com sucesso!")

            ns = {'nfe': 'http://www.portalfiscal.inf.br/nfe'}

            data = {
                "emitente_nome": safe_find_text(root, ".//nfe:emit/nfe:xNome", ns),
                "emitente_cnpj": safe_find_text(root, ".//nfe:emit/nfe:CNPJ", ns),
                "numero_nota": safe_find_text(root, ".//nfe:ide/nfe:nNF", ns),
                "data_emissao": formatar_data_para_brasileiro(safe_find_text(root, ".//nfe:ide/nfe:dhEmi", ns)),
                "valor_total": safe_find_text(root, ".//nfe:total/nfe:ICMSTot/nfe:vNF", ns),
                "forma_pagamento": safe_find_text(root, ".//nfe:pag/nfe:detPag/nfe:tPag", ns),
                "valor_pagamento": safe_find_text(root, ".//nfe:pag/nfe:detPag/nfe:vPag", ns),
                "frete": safe_find_text(root, ".//nfe:transp/nfe:modFrete", ns),
                "destinatario_nome": safe_find_text(root, ".//nfe:dest/nfe:xNome", ns),
                "destinatario_cnpj": safe_find_text(root, ".//nfe:dest/nfe:CNPJ", ns),
                "destinatario_cpf": safe_find_text(root, ".//nfe:dest/nfe:CPF", ns),
                "destinatario_logradouro": safe_find_text(root, ".//nfe:dest/nfe:enderDest/nfe:xLgr", ns),
                "destinatario_numero": safe_find_text(root, ".//nfe:dest/nfe:enderDest/nfe:nro", ns),
                "destinatario_complemento": safe_find_text(root, ".//nfe:dest/nfe:enderDest/nfe:xCpl", ns),
                "destinatario_bairro": safe_find_text(root, ".//nfe:dest/nfe:enderDest/nfe:xBairro", ns),
                "destinatario_municipio": safe_find_text(root, ".//nfe:dest/nfe:enderDest/nfe:xMun", ns),
                "destinatario_uf": safe_find_text(root, ".//nfe:dest/nfe:enderDest/nfe:UF", ns),
                "destinatario_cep": safe_find_text(root, ".//nfe:dest/nfe:enderDest/nfe:CEP", ns),
                "destinatario_email": safe_find_text(root, ".//nfe:dest/nfe:email", ns),
                "produtos": []
            }

            for item in root.findall(".//nfe:det", ns):
                produto = item.find("nfe:prod", ns)
                if produto is not None:
                    data["produtos"].append({
                        "descricao": safe_find_text(produto, "nfe:xProd", ns),
                        "quantidade": safe_find_text(produto, "nfe:qCom", ns),
                        "valor_unitario": safe_find_text(produto, "nfe:vUnCom", ns),
                        "valor_total_item": safe_find_text(produto, "nfe:vProd", ns)
                    })

            print(f"Dados extraídos para seleção: {data}")
            return render_template('select.html', data=data)
        except ET.ParseError:
            return "Erro ao processar o arquivo XML. Verifique o formato.", 400

@app.route('/report', methods=['POST'])
def generate_report():
    selected_options = request.form.getlist('info')
    data = request.form
    report_data = {}

    if "emitente_nome" in selected_options:
        report_data["Emitente Nome"] = data["emitente_nome"]
    if "emitente_cnpj" in selected_options:
        report_data["Emitente CNPJ"] = data["emitente_cnpj"]
    if "numero_nota" in selected_options:
        report_data["Número da Nota"] = data["numero_nota"]
    if "data_emissao" in selected_options:
        report_data["Data de Emissão"] = formatar_data_para_brasileiro(data["data_emissao"])
    if "valor_total" in selected_options:
        report_data["Valor Total"] = data["valor_total"]
    if "forma_pagamento" in selected_options:
        report_data["Forma de Pagamento"] = data["forma_pagamento"]
        report_data["Valor Pago"] = data["valor_pagamento"]
    if "frete" in selected_options:
        report_data["Frete"] = data["frete"]
    if "destinatario_nome" in selected_options:
        report_data["Destinatário Nome"] = data["destinatario_nome"]
    if "destinatario_cnpj" in selected_options:
        report_data["Destinatário CNPJ"] = data["destinatario_cnpj"]
    if "destinatario_cpf" in selected_options:
        report_data["Destinatário CPF"] = data["destinatario_cpf"]
    if "destinatario_logradouro" in selected_options:
        report_data["Destinatário Logradouro"] = data["destinatario_logradouro"]
    if "destinatario_numero" in selected_options:
        report_data["Destinatário Número"] = data["destinatario_numero"]
    if "destinatario_complemento" in selected_options:
        report_data["Destinatário Complemento"] = data["destinatario_complemento"]
    if "destinatario_bairro" in selected_options:
        report_data["Destinatário Bairro"] = data["destinatario_bairro"]
    if "destinatario_municipio" in selected_options:
        report_data["Destinatário Município"] = data["destinatario_municipio"]
    if "destinatario_uf" in selected_options:
        report_data["Destinatário UF"] = data["destinatario_uf"]
    if "destinatario_cep" in selected_options:
        report_data["Destinatário CEP"] = data["destinatario_cep"]
    if "destinatario_email" in selected_options:
        report_data["Destinatário Email"] = data["destinatario_email"]

    produtos = []
    produtos_maior_valor = []
    if "produtos" in selected_options:
        for i in range(len(data.getlist("descricao_produto"))):
            quantidade_formatada = str(int(float(data.getlist("quantidade_produto")[i]))).zfill(2)
            valor_unitario = float(data.getlist("valor_unitario_produto")[i])
            produto = {
                "descricao": data.getlist("descricao_produto")[i],
                "quantidade": quantidade_formatada,
                "valor_unitario": valor_unitario,
                "valor_total_item": data.getlist("valor_total_item_produto")[i]
            }
            produtos.append(produto)

        produtos_maior_valor = sorted(produtos, key=lambda x: x["valor_unitario"], reverse=True)[:2]

        report_data["Produtos"] = produtos

    motivo = ""
    if produtos_maior_valor and "Número da Nota" in report_data and "Emitente Nome" in report_data:
        descricoes_maior_valor = [f'{produto["quantidade"]} {produto["descricao"]}' for produto in produtos_maior_valor]
        motivo = f'Motivo: {", ".join(descricoes_maior_valor)}, alocados no almoxarifado, para atender demanda de filiais - NF {report_data["Número da Nota"]} Fornecedor {report_data["Emitente Nome"]}'
    report_data["motivo"] = motivo
    report_data["justificativa"] = motivo

    print(f"Dados do relatório final: {report_data}")
    return render_template('report.html', report_data=report_data)

if __name__ == '__main__':
    app.run(debug=True)