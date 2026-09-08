# -*- coding: utf-8 -*-
u"""
Somando com os Dedinhos — gera o dicionário FALAS (toda frase que a voz diz), grava-o
no index.html entre /*FALAS-INI*/ e /*FALAS-FIM*/, escreve o falas.json e o mapa VOZOK.
Mesmo padrão do UNO e da Folha Viva (app à mão): a chave é a djb2 base 36 do texto
normalizado (igual ao `chaveVoz` do motor); o entregar.yml grava `audio/dd_<chave>.mp3`.

As frases DINÂMICAS (3 dedos e mais 2 dedos...) são enumeradas AQUI, uma vez, para
todas as combinações que o jogo pode sortear — o JS só lê FALAS[k]. Assim não há
frase sem mp3 e não há divergência entre o que o Python grava e o que o JS fala.

Uso: python3 _dedos/gerar_falas.py
"""
import io, json, os, re

AQUI = os.path.dirname(os.path.abspath(__file__))
IDX = os.path.join(AQUI, "index.html")

NUM = [u"zero", u"um", u"dois", u"três", u"quatro", u"cinco", u"seis", u"sete", u"oito", u"nove", u"dez"]
NUMF = [u"zero", u"uma", u"duas", u"três", u"quatro", u"cinco", u"seis", u"sete", u"oito", u"nove", u"dez"]


def dedos(n):
    return u"um dedo" if n == 1 else u"%s dedos" % NUM[n]


def chave(s):
    s = re.sub(r"\s+", " ", s or "").strip().lower()
    hh = 5381
    for ch in s:
        hh = (hh * 33 + ord(ch)) & 0xFFFFFFFF
    if hh == 0:
        return "0"
    d = "0123456789abcdefghijklmnopqrstuvwxyz"
    out = ""
    while hh:
        out = d[hh % 36] + out
        hh //= 36
    return out


F = {}
# ---- fixas
F.update({
    "capa": u"Somando com os dedinhos! Escreva o seu nome ali embaixo e toque em Começar.",
    "nomeOk": u"Que nome bonito! Agora toque em Começar.",
    "vozOn": u"Narração ligada!",
    "p1enun": u"Conte os dedos das duas mãos e digite quantos são ao todo. Toque no quadradinho para escrever.",
    "p2enun": u"Agora as mãos mostram mais dedos. Conte todos, até dez, e digite quanto dá.",
    "p3enun": u"Ligue cada dupla de mãos ao número de dedos. Toque nas mãos e depois no número, ou puxe uma linha.",
    "p4enun": u"Agora é você quem mostra! Toque nos dedos das duas mãos para levantar a quantidade que eu pedir, e depois toque em Pronto.",
    "p5enun": u"Uma mão já mostra alguns dedos. Levante dedos na outra mão até juntar a quantidade que eu pedir, e toque em Pronto.",
    "quase": u"Quase! Conte de novo, dedo por dedo.",
    "essaNao": u"Essa não. Conte os dedos das duas mãos de novo.",
    "digite": u"Toque num quadradinho e digite o número.",
    "ligue": u"Primeiro toque nas mãos, depois no número.",
    "paginaPronta": u"Página pronta! Vamos para a próxima.",
    "faltam": u"Ainda falta responder nesta página. Olhe os quadradinhos tracejados.",
    "fim": u"Você somou tudo com os dedinhos! Parabéns!",
    "fimRel": u"Relatório do professor aberto.",
    "retomar": u"Você estava no meio da folha. Quer continuar de onde parou?",
    "novaFolha": u"Folha nova! Os dedinhos mudaram. Vamos de novo?",
    "pronto": u"Pronto!",
    "levanteMais": u"Levante mais dedos.",
    "abaixeUns": u"Abaixe alguns dedos.",
})
for n in range(0, 11):
    F["n%d" % n] = NUM[n]
    F["mostre%d" % n] = u"Mostre %s com as mãos." % dedos(n) if n else u"Mostre nenhum dedo: abaixe todos."
    F["levantou%d" % n] = u"Você levantou %s." % dedos(n)
for k in range(1, 10):
    F["faltam%d" % k] = u"Falta %s." % dedos(k) if k == 1 else u"Faltam %s." % dedos(k)
    F["sobram%d" % k] = u"Sobra %s. Abaixe um." % dedos(k) if k == 1 else u"Sobram %s. Abaixe %s." % (dedos(k), NUM[k])
# ---- somas a + b (mão a, mão b), 1..5 cada
for a in range(1, 6):
    for b in range(1, 6):
        F["soma%d_%d" % (a, b)] = u"%s e mais %s. Quantos dedos ao todo?" % (dedos(a).capitalize(), dedos(b))
        F["certo%d_%d" % (a, b)] = u"Isso! %s mais %s são %s." % (NUM[a].capitalize(), NUM[b], NUM[a + b])
        seq = u", ".join(NUM[i] for i in range(1, a + 1)) + u"... " + u", ".join(NUM[i] for i in range(a + 1, a + b + 1)) + u"!"
        F["conte%d_%d" % (a, b)] = u"Conte comigo: %s" % seq
        F["par%d_%d" % (a, b)] = u"%s e mais %s." % (dedos(a).capitalize(), dedos(b))
# ---- quantos faltam: mão A fixa (1..5) até T (A+1..A+5, <= 10)
for a in range(1, 6):
    for t in range(a + 1, min(10, a + 5) + 1):
        F["falta%d_%d" % (a, t)] = u"Já tem %s. Levante dedos na outra mão até juntar %s." % (dedos(a), NUM[t])
        F["fechou%d_%d" % (a, t)] = u"Isso! %s mais %s são %s." % (NUM[a].capitalize(), NUM[t - a], NUM[t])

# ---- grava no index
html = io.open(IDX, encoding="utf-8").read()
bloco = "/*FALAS-INI*/\nvar FALAS = " + json.dumps(F, ensure_ascii=False, indent=1, sort_keys=True) + ";\n/*FALAS-FIM*/"
novo, n = re.subn(r"/\*FALAS-INI\*/.*?/\*FALAS-FIM\*/", lambda m: bloco, html, flags=re.S)
if n != 1:
    raise SystemExit("index.html sem as marcas /*FALAS-INI*/ ... /*FALAS-FIM*/")

falas, vistos = [], set()
for k in sorted(F):
    t = re.sub(r"\s+", " ", F[k]).strip()
    c = chave(t)
    if c in vistos:
        continue
    vistos.add(c)
    falas.append({"id": "dd_" + c, "texto": t})
io.open(os.path.join(AQUI, "falas.json"), "w", encoding="utf-8").write(json.dumps(falas, ensure_ascii=False, indent=1) + "\n")
if not os.path.exists(os.path.join(AQUI, "voz.txt")):
    io.open(os.path.join(AQUI, "voz.txt"), "w", encoding="utf-8").write("pt-BR-AntonioNeural\n")
mapa = "var VOZOK = " + json.dumps({f["id"][3:]: 1 for f in falas}, separators=(",", ":")) + ";"
novo, n2 = re.subn(r"/\*VOZOK-INI\*/.*?/\*VOZOK-FIM\*/", "/*VOZOK-INI*/" + mapa + "/*VOZOK-FIM*/", novo, flags=re.S)
if n2 != 1:
    raise SystemExit("index.html sem as marcas /*VOZOK-INI*/ ... /*VOZOK-FIM*/")
io.open(IDX, "w", encoding="utf-8").write(novo)
print("FALAS: %d frases; falas.json: %d fala(s); VOZOK gravado" % (len(F), len(falas)))
