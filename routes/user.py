from flask import Blueprint, render_template, request, redirect, url_for, send_file
from database.models.tables import *
import datetime
import io
from reportlab.platypus import SimpleDocTemplate, Table, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
)
from reportlab.lib.styles import getSampleStyleSheet


user_route = Blueprint('user', __name__)

#Mostrar formulario que registra um uso
@user_route.route('/registro', methods=['GET', 'POST'])
def registrar():
    if request.method == 'POST':
        escola, _ = Escola.get_or_create(nome=request.form['escola'])
        produto, _ = Produto.get_or_create(nome=request.form['produto'])

        Consumo.create(
            data=datetime.date.fromisoformat(request.form['data']),
            escola=escola,
            produto=produto,
            quantidade=int(request.form['quantidade']),
            unidade=request.form['unidade']
        )
        return redirect(url_for('user.todos_os_usos'))

    return render_template('registrar.html')

@user_route.route('/relatorio', methods=['GET'])
def relatorio():
    escolas = Escola.select()
    dados = None

    escola_id = request.args.get('escola')
    inicio = request.args.get('inicio')
    fim = request.args.get('fim')

    if escola_id and inicio and fim:
        dados = (
            Consumo
            .select(
                Produto.nome,
                Consumo.unidade,
                fn.SUM(Consumo.quantidade).alias('total')
            )
            .join(Produto)
            .where((Consumo.escola == escola_id) & (Consumo.data.between(inicio, fim)))
            .group_by(Produto.nome, Consumo.unidade)
        )

    return render_template(
        'relatorio.html',
        escolas=escolas,
        dados=dados
    )

@user_route.route('/relatorio/pdf')
def relatorio_pdf():
    escola_id = request.args['escola']
    inicio = request.args['inicio']
    fim = request.args['fim']
    diretor = request.args['diretor']

    escola = Escola.get_by_id(escola_id)

    dados = (
        Consumo
        .select(
            Produto.nome,
            Consumo.unidade,
            fn.SUM(Consumo.quantidade).alias('total')
        )
        .join(Produto)
        .where((Consumo.escola == escola_id) & (Consumo.data.between(inicio, fim)))
        .group_by(Produto.nome, Consumo.unidade)
    )

    buffer = io.BytesIO()

    pdf = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    estilos = getSampleStyleSheet()
    estilos['Title'].alignment = 1  # Centralizado
    estilos['Normal'].spaceAfter = 8

    elementos = []

    # TÍTULO
    elementos.append(
        Paragraph(f"<b>RELATÓRIO DE CONSUMO</b><br/>{escola.nome}", estilos['Title'])
    )
    elementos.append(Spacer(1, 20))

    # INFORMAÇÕES DO RELATÓRIO
    elementos.append(Paragraph(f"<b>Período:</b> {inicio} a {fim}", estilos['Normal']))
    elementos.append(Spacer(1, 20))

    # TABELA DE DADOS
    tabela = [['Produto', 'Total', 'Unidade']]
    for d in dados:
        tabela.append([d.produto.nome, str(d.total), d.unidade])

    tabela_pdf = Table(tabela, colWidths=[350, 100])
    tabela_pdf.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('TOPPADDING', (0, 0), (-1, 0), 10),
    ]))

    elementos.append(tabela_pdf)
    elementos.append(Spacer(1, 40))

    # ASSINATURAS
    assinaturas = Table(
        [
            [
                "_______________________________",
                "_______________________________"
            ],
            [
                f"Diretor(a): {diretor}",
                "Adrieli de Almeida"
            ]
        ],
        colWidths=[250, 250]
    )

    assinaturas.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('TOPPADDING', (0, 1), (-1, 1), 10),
    ]))

    elementos.append(assinaturas)

    pdf.build(elementos)
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name='relatorio_consumo.pdf',
        mimetype='application/pdf'
    )


@user_route.route('/usos')
def todos_os_usos():
    usos = (
        Consumo
        .select()
        .join(Escola)
        .switch(Consumo)
        .join(Produto)
        .order_by(Consumo.data.desc())
    )

    return render_template('label.html', usos=usos)

@user_route.route('/usos/excluir/<int:id>', methods=['DELETE'])
def remove(id):
    uso = Consumo.get_or_none(Consumo.id == id)

    if uso:
        uso.delete_instance()

    return {'deleted': 'ok'}

@user_route.route('/relatorio/produto', methods=['GET'])
def relatorio_mensal():
    produtos = Produto.select()
    dados = None

    produto_req = request.args.get('produto')
    ano = request.args.get("ano")

    if produto_req and ano:
        dados = (
    
        Consumo.select(
            fn.strftime('%m/%Y', Consumo.data).alias('mes'),
            Consumo.unidade,
            fn.SUM(Consumo.quantidade).alias('total_mes')
        )
        .where(
            (Consumo.produto == produto_req) &
            (fn.strftime('%Y', Consumo.data) == str(ano))
        )
        .group_by(
            fn.strftime('%m/%Y', Consumo.data),
            Consumo.unidade
        )
        .order_by(fn.strftime('%Y-%m', Consumo.data))
    )


    return render_template(
        'perproduto.html',
        produtos=produtos,
        dados=dados
    )

@user_route.route('/relatorio/produto/pdf')
def relatorio_mensal_pdf():

    produto_id = request.args.get('produto')
    ano = request.args.get('ano')

    produto = Produto.get_by_id(produto_id)

    # ================= QUERY PRINCIPAL =================
    query = (
        Consumo
        .select(
            fn.strftime('%m/%Y', Consumo.data).alias('mes'),
            Escola.nome.alias('escola'),
            Consumo.unidade.alias('unidade'),
            fn.SUM(Consumo.quantidade).alias('total_mes')
        )
        .join(Escola, on=(Consumo.escola == Escola.id))
        .where(
            (Consumo.produto == produto) &
            (fn.strftime('%Y', Consumo.data) == str(ano))
        )
        .group_by(
            fn.strftime('%m/%Y', Consumo.data),
            Escola.nome,
            Consumo.unidade
        )
        .order_by(
            fn.strftime('%Y-%m', Consumo.data),
            Escola.nome
        )
        .dicts()
    )



    # ================= TOTAL GERAL =================
    totais = (
        Consumo
        .select(
            Consumo.unidade,
            fn.SUM(Consumo.quantidade).alias('total')
        )
        .where(
            (Consumo.produto == produto) &
            (fn.strftime('%Y', Consumo.data) == str(ano))
        )
        .group_by(Consumo.unidade)
    )

    # ================= PDF =================
    nome_pdf = f"relatorio_{produto.nome}_{ano}.pdf"

    doc = SimpleDocTemplate(nome_pdf, pagesize=A4)
    styles = getSampleStyleSheet()
    elementos = []

    # -------- TÍTULO --------
    elementos.append(Paragraph(
        "RELATÓRIO MENSAL DE CONSUMO POR PRODUTO",
        styles['Title']
    ))
    elementos.append(Spacer(1, 12))

    # -------- CABEÇALHO --------
    elementos.append(Paragraph(
        f"<b>Produto:</b> {produto.nome}<br/>"
        f"<b>Ano:</b> {ano}<br/>"
        f"<b>Data de emissão:</b> {datetime.date.today().strftime('%d/%m/%Y')}",
        styles['Normal']
    ))

    elementos.append(Spacer(1, 20))

    # -------- TABELA --------
    tabela = [['Mês/Ano', 'Escola', 'Quantidade']]

    for r in query:
        tabela.append([
            r['mes'],
            r['escola'],
            f"{r['total_mes']} {r['unidade']}"
        ])


    elementos.append(Table(tabela, hAlign='LEFT'))
    elementos.append(Spacer(1, 20))

    # -------- TOTAL --------
    elementos.append(Paragraph("<b>Total Geral do Produto no Ano:</b>", styles['Heading2']))

    for t in totais:
        elementos.append(
            Paragraph(f"{t.total} {t.unidade}", styles['Normal'])
        )

    # -------- ASSINATURA --------
    elementos.append(Spacer(1, 40))
    elementos.append(Paragraph(
        "_____________________________________________<br/>"
        "               Adrieli de Almeida",
        styles['Normal']
    ))

    doc.build(elementos)

    return send_file(nome_pdf, as_attachment=True)

