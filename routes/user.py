from flask import Blueprint, render_template, request, redirect, url_for, send_file
from database.models.tables import *
import datetime
import io, os, re, locale
from reportlab.platypus import SimpleDocTemplate, Table, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
)
from reportlab.lib.styles import getSampleStyleSheet

locale.setlocale(locale.LC_TIME, "Portuguese_Brazil.1252")

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
    produtos = Escola.select()
    dados = None

    escolax_req = request.args.get('escola')
    ano = request.args.get("ano")

    if escolax_req and ano:
        dados = (
    
        Consumo.select(
            fn.strftime('%m/%Y', Consumo.data).alias('mes'),
            Consumo.unidade,
            fn.SUM(Consumo.quantidade).alias('total_mes')
        )
        .where(
            (Consumo.escola == escolax_req) &
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
        escolas=produtos,
        dados=dados
    )

@user_route.route('/relatorio/produto/pdf')
def relatorio_mensal_pdf():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    PASTA_RELATORIOS = os.path.join(BASE_DIR, 'relatorios')
    os.makedirs(PASTA_RELATORIOS, exist_ok=True)


    escola_id = request.args.get('escola')
    ano = request.args.get('ano')

    if not escola_id or not ano:
        return "Parâmetros obrigatórios ausentes", 400

    escola = Escola.get_by_id(escola_id)

    registros = (
        Consumo
        .select(
            Produto.nome.alias('produto'),
            fn.strftime('%m', Consumo.data).alias('mes'),
            fn.strftime('%d', Consumo.data).alias('dia'),
            Consumo.quantidade,
            Consumo.unidade
        )
        .join(Produto, on=(Consumo.produto == Produto.id))
        .where(
            (Consumo.escola == escola) &
            (fn.strftime('%Y', Consumo.data) == str(ano))
        )
        .order_by(
            fn.strftime('%Y-%m', Consumo.data),
            Produto.nome,
            Consumo.data
        )
        .dicts()
    )

    nome_pdf = f"relatorio_consumo_{escola.nome}_{ano}.pdf"
    nome_escola_limpo = re.sub(r'[^a-zA-Z0-9_-]', '_', escola.nome)
    nome_pdf = f"relatorio_consumo_{nome_escola_limpo}_{ano}.pdf"
    penes = os.path.join(PASTA_RELATORIOS, nome_pdf)

    doc = SimpleDocTemplate(
        penes,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    elementos = []

    # ===== CABEÇALHO =====
    elementos.append(Paragraph(
        "RELATÓRIO DE CONSUMO ANUAL",
        styles['Title']
    ))
    elementos.append(Spacer(1, 12))

    elementos.append(Paragraph(
        f"<b>Escola:</b> {escola.nome}<br/>"
        f"<b>Ano:</b> {ano}<br/>"
        f"<b>Data de emissão:</b> {datetime.date.today().strftime('%d/%m/%Y')}",
        styles['Normal']
    ))

    elementos.append(Spacer(1, 20))

    # ===== ORGANIZAÇÃO POR MÊS =====
    meses = {}
    for r in registros:
        meses.setdefault(r['mes'], []).append(r)

    totais_anuais = {}

    for mes, itens in meses.items():
        nome_mes = datetime.date(1900, int(mes), 1).strftime('%B').capitalize()

        elementos.append(Paragraph(
            nome_mes,
            styles['Heading2']
        ))
        elementos.append(Spacer(1, 8))

        tabela = [['Produto', 'Dia', 'Quantidade', 'Unidade']]

        totais_mes = {}

        for i in itens:
            tabela.append([
                i['produto'],
                i['dia'],
                i['quantidade'],
                i['unidade']
            ])

            chave = (i['produto'], i['unidade'])
            totais_mes[chave] = totais_mes.get(chave, 0) + i['quantidade']
            totais_anuais[chave] = totais_anuais.get(chave, 0) + i['quantidade']

        # Total do mês
        tabela.append(['', '', '', ''])
        for (produto, unidade), total in totais_mes.items():
            tabela.append([
                f"Total ({produto})",
                '',
                total,
                unidade
            ])

        elementos.append(Table(
            tabela,
            colWidths=[200, 60, 80, 80],
            style=[
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ]
        ))

        elementos.append(Spacer(1, 20))

    # ===== TOTAL ANUAL =====
    elementos.append(Paragraph(
        "Total Anual",
        styles['Heading2']
    ))

    tabela_total = [['Produto', 'Quantidade', 'Unidade']]

    for (produto, unidade), total in totais_anuais.items():
        tabela_total.append([produto, total, unidade])

    elementos.append(Table(
        tabela_total,
        colWidths=[240, 120, 80],
        style=[
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ]
    ))

    # ===== ASSINATURA =====
    elementos.append(Spacer(1, 40))
    elementos.append(Paragraph(
        "_____________________________________________<br/>"
        "Assinatura do Diretor",
        styles['Normal']
    ))

    doc.build(elementos)

    return send_file(
        penes,
        as_attachment=True,
        download_name=nome_pdf
    )