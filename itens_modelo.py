"""
Modelo dos itens do acerto (sem Streamlit): valor por mês, reajustes e edição.

Formato de um item em dados_dashboard_ana.json:
    id, nome
    tipo         "credito" soma ao que a Ana recebe; "debito" abate do acerto
    valor        valor da parcela, ou valor inicial de um item contínuo
    inicio, fim  primeiro e último mês ("jan/25"); em item contínuo, fim é
                 sempre o último mês do horizonte do app
    continuo     True para item sem data fim (ex.: Plano de Saúde)
    reajustes    [{"a_partir_de": "jan/27", "valor": 1702.4}], só em contínuo
    contrato, cronograma, antecipacoes   preservados (ver app.py)

Itens antigos não têm "continuo": contrato.total_parcelas == 0 era a marca de
item recorrente e continua valendo.

Regra central: um reajuste vale a partir de um mês. Os meses anteriores — que
podem já estar quitados — continuam com o valor antigo.
"""

import copy
import uuid


def _brl(valor):
    return f"{abs(float(valor)):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def eh_continuo(item):
    if "continuo" in item:
        return bool(item["continuo"])
    contrato = item.get("contrato") or {}
    return bool(contrato) and not contrato.get("total_parcelas")


def ultimo_mes(item, meses):
    return meses[-1] if eh_continuo(item) else item["fim"]


def meses_do_item(item, meses):
    try:
        ini = meses.index(item["inicio"])
        fim = meses.index(ultimo_mes(item, meses))
    except ValueError:
        return []
    return meses[ini:fim + 1]


def reajustes(item, meses):
    """Reajustes com mês válido, em ordem cronológica."""
    lista = [r for r in item.get("reajustes") or [] if r.get("a_partir_de") in meses]
    return sorted(lista, key=lambda r: meses.index(r["a_partir_de"]))


def vigencias(item, meses):
    """[(desde, valor)]: valor inicial seguido dos reajustes posteriores ao início."""
    base = [(item["inicio"], float(item["valor"]))]
    if not eh_continuo(item) or item["inicio"] not in meses:
        return base
    i_ini = meses.index(item["inicio"])
    return base + [(r["a_partir_de"], float(r["valor"])) for r in reajustes(item, meses)
                   if meses.index(r["a_partir_de"]) > i_ini]


def valor_vigente(item, mes, meses):
    """Valor por mês em vigor no mês (contínuo) ou o valor da parcela."""
    if not eh_continuo(item) or mes not in meses:
        return float(item["valor"])
    i = meses.index(mes)
    valor = float(item["valor"])
    for desde, v in vigencias(item, meses):
        if meses.index(desde) <= i:
            valor = v
    return valor


def serie(item, meses):
    """Valor do item em cada mês, sem antecipações (0 fora do período)."""
    ativos = meses_do_item(item, meses)
    if not ativos:
        return [0.0] * len(meses)
    ini, fim = meses.index(ativos[0]), meses.index(ativos[-1])
    trocas = {meses.index(d): v for d, v in vigencias(item, meses)}
    valor = float(item["valor"])
    resultado = []
    for i in range(len(meses)):
        if i in trocas:
            valor = trocas[i]
        resultado.append(valor if ini <= i <= fim else 0.0)
    return resultado


def antecipacoes_confirmadas(item):
    return [a for a in item.get("antecipacoes") or [] if a.get("status") == "confirmada"]


def serie_no_acerto(item, meses):
    """Valor do item em cada mês como entra no acerto: base + antecipações confirmadas.

    Mesma regra de calcular_dataframe() em app.py.
    """
    valores = serie(item, meses)
    for ant in antecipacoes_confirmadas(item):
        v = float(ant.get("valor_antecipado", 0.0))
        if ant.get("origem") in meses:
            i = meses.index(ant["origem"])
            valores[i] = max(0.0, valores[i] - v)
        if ant.get("destino") in meses:
            i = meses.index(ant["destino"])
            valores[i] += v
    return valores


def meses_quitados_afetados(antes, depois, meses, quitados):
    """Meses já quitados cujo acerto muda ao trocar `antes` por `depois`.

    Use antes=None para um item novo e depois=None para uma exclusão.
    """
    def assinada(item):
        if item is None:
            return [0.0] * len(meses)
        sinal = 1 if item["tipo"] == "credito" else -1
        return [sinal * v for v in serie_no_acerto(item, meses)]

    a, d = assinada(antes), assinada(depois)
    q = set(quitados)
    return [m for i, m in enumerate(meses) if m in q and abs(a[i] - d[i]) > 0.005]


def fim_por_parcelas(inicio, parcelas, meses):
    """Último mês de `parcelas` parcelas a partir de `inicio`, ou None se passar do horizonte."""
    if inicio not in meses or parcelas is None or int(parcelas) < 1:
        return None
    i = meses.index(inicio) + int(parcelas) - 1
    return meses[i] if i < len(meses) else None


def novo_id(itens):
    """Id único. O antigo custom_{quantidade} repetia o id de um item existente após uma exclusão."""
    existentes = {i["id"] for i in itens}
    while True:
        candidato = f"item_{uuid.uuid4().hex[:8]}"
        if candidato not in existentes:
            return candidato


def resumo(item, meses):
    """Campos que a pessoa edita — para saber se algo mudou de fato."""
    rj = tuple((r["a_partir_de"], round(float(r["valor"]), 2)) for r in reajustes(item, meses)) \
        if eh_continuo(item) else ()
    return (item["nome"].strip(), item["tipo"], round(float(item["valor"]), 2),
            item["inicio"], ultimo_mes(item, meses), rj)


def validar_item(itens, *, nome, tipo, valor, inicio, meses, continuo, parcelas=None,
                 id_atual=None, reajustes=None):
    erros = []
    nome_limpo = (nome or "").strip()
    if not nome_limpo:
        erros.append("Dê um nome ao item.")
    elif any(i["id"] != id_atual and i["nome"].strip().lower() == nome_limpo.lower() for i in itens):
        erros.append(f"Já existe um item chamado {nome_limpo}.")
    if tipo not in ("credito", "debito"):
        erros.append("Escolha se o item soma ao que a Ana recebe ou abate do acerto.")
    if valor is None or float(valor) <= 0:
        erros.append("Informe um valor maior que zero.")
    if inicio not in meses:
        erros.append("Escolha o primeiro mês.")
    elif continuo and reajustes:
        conflitos = [m for m in reajustes if m in meses and meses.index(m) <= meses.index(inicio)]
        if conflitos:
            erros.append(f"Há reajuste em {', '.join(conflitos)}, antes do novo mês de início. "
                         "Remova o reajuste primeiro.")
    elif not continuo and parcelas is not None:
        if int(parcelas) < 1:
            erros.append("Informe ao menos 1 parcela.")
        elif fim_por_parcelas(inicio, parcelas, meses) is None:
            erros.append(f"Com {int(parcelas)} parcelas a partir de {inicio}, o item passaria de "
                         f"{meses[-1]}, o último mês do app.")
    return erros


def validar_reajuste(item, a_partir_de, valor, meses):
    erros = []
    if a_partir_de not in meses or meses.index(a_partir_de) <= meses.index(item["inicio"]):
        erros.append(f"O reajuste precisa começar depois de {item['inicio']}, o primeiro mês do item.")
    if valor is None or float(valor) <= 0:
        erros.append("Informe o novo valor, maior que zero.")
    elif not erros:
        sem_este = dict(item)
        sem_este["reajustes"] = [r for r in item.get("reajustes") or [] if r.get("a_partir_de") != a_partir_de]
        if abs(valor_vigente(sem_este, a_partir_de, meses) - float(valor)) < 0.005:
            erros.append(f"Em {a_partir_de} o valor já é R$ {_brl(valor)}.")
    return erros


def criar_item(itens, *, nome, tipo, valor, inicio, meses, continuo, parcelas=None):
    fim = meses[-1] if continuo else fim_por_parcelas(inicio, parcelas, meses)
    item = {
        "id": novo_id(itens),
        "nome": nome.strip(),
        "valor": round(float(valor), 2),
        "tipo": tipo,
        "inicio": inicio,
        "fim": fim,
        "continuo": bool(continuo),
        "antecipacoes": [],
    }
    if continuo:
        item["reajustes"] = []
    item["contrato"] = {
        "inicio_original": inicio,
        "fim_original": fim,
        "total_parcelas": 0 if continuo else int(parcelas),
        "valor_parcela": item["valor"],
    }
    return item


def editar_item(item, meses, *, nome, tipo, valor=None, inicio=None, parcelas=None):
    """Cópia do item com os campos alterados, preservando antecipações, reajustes e contrato.

    valor/inicio/parcelas = None mantém o que já está gravado (é o caso de itens
    com parcelas antecipadas, em que a interface trava esses campos).
    """
    continuo = eh_continuo(item)
    novo = copy.deepcopy(item)
    novo["nome"] = nome.strip()
    novo["tipo"] = tipo
    if valor is not None:
        novo["valor"] = round(float(valor), 2)
    if inicio is not None:
        novo["inicio"] = inicio
    if continuo:
        novo["continuo"] = True
        novo["fim"] = meses[-1]
        novo["reajustes"] = [r for r in reajustes(novo, meses)
                             if meses.index(r["a_partir_de"]) > meses.index(novo["inicio"])]
    elif parcelas is not None:
        novo["fim"] = fim_por_parcelas(novo["inicio"], parcelas, meses)
    if not antecipacoes_confirmadas(novo):
        contrato = novo.setdefault("contrato", {})
        contrato.update({
            "inicio_original": novo["inicio"],
            "fim_original": novo["fim"],
            "total_parcelas": 0 if continuo else len(meses_do_item(novo, meses)),
            "valor_parcela": novo["valor"],
        })
    return novo


def registrar_reajuste(item, a_partir_de, valor, meses):
    """Cópia do item com o reajuste (substitui um reajuste já registrado no mesmo mês)."""
    novo = copy.deepcopy(item)
    lista = [r for r in reajustes(novo, meses) if r["a_partir_de"] != a_partir_de]
    lista.append({"a_partir_de": a_partir_de, "valor": round(float(valor), 2)})
    novo["reajustes"] = sorted(lista, key=lambda r: meses.index(r["a_partir_de"]))
    novo["continuo"] = True
    novo["fim"] = meses[-1]
    return novo


def remover_reajuste(item, a_partir_de, meses):
    novo = copy.deepcopy(item)
    novo["reajustes"] = [r for r in reajustes(novo, meses) if r["a_partir_de"] != a_partir_de]
    return novo
