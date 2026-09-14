"""
Antecipação de parcelas (sem Streamlit).

Antecipar = registrar que uma parcela foi paga em outro mês: o valor sai do mês
em que ela venceria (origem) e entra no acerto do mês em que foi paga (destino).
Destino depois da origem é um adiamento — permitido, mas nomeado como tal.

Os registros mantêm o formato de backend_antecipacao.py:
    id_antecipacao, id_parcela, origem, destino, mes_original_parcela,
    valor_antecipado, usuario, timestamp, motivo, status
    (+ cancelado_por, cancelado_em quando status == "cancelada")
"""

import copy
import uuid
from datetime import datetime

import itens_modelo as modelo


def pode_antecipar(item):
    """Só parcelas de itens que abatem do acerto; item contínuo não tem parcelas."""
    return item.get("tipo") == "debito" and not modelo.eh_continuo(item)


def _origens_ocupadas(item):
    ocupadas = set()
    for a in modelo.antecipacoes_confirmadas(item):
        ocupadas.add(a.get("origem"))
        ocupadas.add(a.get("mes_original_parcela") or a.get("origem"))
    return ocupadas


def numero_parcela(item, mes, meses):
    """(número, total) da parcela no período do item, ou (None, total) fora dele."""
    periodo = modelo.meses_do_item(item, meses)
    if mes in periodo:
        return periodo.index(mes) + 1, len(periodo)
    return None, len(periodo)


def parcelas_disponiveis(item, meses, quitados):
    """Parcelas que ainda podem ser antecipadas: não quitadas e não antecipadas."""
    if not pode_antecipar(item):
        return []
    ocupadas = _origens_ocupadas(item)
    q = set(quitados)
    base = modelo.serie(item, meses)
    return [m for m in modelo.meses_do_item(item, meses)
            if base[meses.index(m)] > 0.005 and m not in q and m not in ocupadas]


def adiadas(origens, destino, meses):
    """Parcelas cujo mês de pagamento vem depois do vencimento."""
    if destino not in meses:
        return []
    i = meses.index(destino)
    return [m for m in origens if m in meses and meses.index(m) < i]


def validar(item, origens, destino, meses, quitados):
    erros = []
    if not origens:
        erros.append("Escolha ao menos uma parcela.")
    if destino not in meses:
        erros.append("Escolha o mês em que as parcelas foram pagas.")
    elif destino in origens:
        erros.append(f"{destino} é uma das parcelas escolhidas. Escolha outro mês de pagamento.")
    disponiveis = set(parcelas_disponiveis(item, meses, quitados))
    fora = [m for m in origens if m not in disponiveis]
    if fora:
        erros.append(f"Estas parcelas não estão mais em aberto: {', '.join(fora)}.")
    return erros


def _restaurar_fim(item):
    """Mesma regra de backend_antecipacao.encurtar_fluxo_item: o fim volta ao do contrato."""
    fim = (item.get("contrato") or {}).get("fim_original")
    if fim:
        item["fim"] = fim


def antecipar(item, origens, destino, meses, *, motivo="", usuario="usuario_logado", agora=None):
    """Cópia do item com uma antecipação confirmada por parcela de origem."""
    novo = copy.deepcopy(item)
    base = modelo.serie(item, meses)
    momento = (agora or datetime.now()).isoformat()
    registros = novo.setdefault("antecipacoes", [])
    for m in sorted(origens, key=meses.index):
        registros.append({
            "id_antecipacao": str(uuid.uuid4()),
            "id_parcela": f"{item['id']}_{m}",
            "origem": m,
            "destino": destino,
            "mes_original_parcela": m,
            "valor_antecipado": round(base[meses.index(m)], 2),
            "usuario": usuario,
            "timestamp": momento,
            "motivo": (motivo or "").strip(),
            "status": "confirmada",
        })
    _restaurar_fim(novo)
    return novo


def cancelar(item, id_antecipacao, *, usuario="usuario_logado", agora=None):
    """Cópia do item com a antecipação marcada como cancelada."""
    novo = copy.deepcopy(item)
    for a in novo.get("antecipacoes") or []:
        if a.get("id_antecipacao") == id_antecipacao and a.get("status") == "confirmada":
            a["status"] = "cancelada"
            a["cancelado_por"] = usuario
            a["cancelado_em"] = (agora or datetime.now()).isoformat()
            break
    else:
        raise ValueError("Antecipação não encontrada ou já cancelada.")
    _restaurar_fim(novo)
    return novo


def totais(itens, meses):
    """Acerto de cada mês (créditos menos débitos), com antecipações."""
    resultado = [0.0] * len(meses)
    for item in itens:
        sinal = 1 if item["tipo"] == "credito" else -1
        for i, v in enumerate(modelo.serie_no_acerto(item, meses)):
            resultado[i] += sinal * v
    return resultado


def efeito(itens, antes, depois, meses):
    """[(mês, acerto antes, acerto depois)] dos meses cujo acerto muda."""
    base = totais(itens, meses)
    sa = modelo.serie_no_acerto(antes, meses)
    sd = modelo.serie_no_acerto(depois, meses)
    sinal = 1 if antes["tipo"] == "credito" else -1
    return [(m, base[i], base[i] + sinal * (sd[i] - sa[i]))
            for i, m in enumerate(meses) if abs(sd[i] - sa[i]) > 0.005]
