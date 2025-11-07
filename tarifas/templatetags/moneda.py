from django import template

register = template.Library()

@register.filter
def formato_moneda(valor):
    """
    Formatea un número como moneda chilena.
    """
    if valor is None:
        return ""
    return f"${valor:,.0f}".replace(",", ".")
