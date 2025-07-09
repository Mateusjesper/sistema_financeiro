import locale
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

def moeda(valor: float) -> str:
    return locale.currency(valor, grouping=True)