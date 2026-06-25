import re
from dataclasses import dataclass

from app.services.intent_router import Intent


@dataclass(frozen=True)
class SynonymRule:
    pattern: str
    replacement: str
    intent_hint: str | None = None


class BusinessSynonyms:
    # Orden: patrones más largos primero para evitar reemplazos parciales.
    REPLACEMENT_RULES: tuple[SynonymRule, ...] = (
        # Cobertura temporal
        SynonymRule(
            r"\bde que fecha a que fecha tienes informacion\b",
            "cobertura de datos",
            Intent.DATA_COVERAGE.value,
        ),
        SynonymRule(
            r"\bde que fecha a que fecha sabes\b",
            "cobertura de datos",
            Intent.DATA_COVERAGE.value,
        ),
        SynonymRule(
            r"\bhasta que fecha estas actualizado\b",
            "cobertura de datos",
            Intent.DATA_COVERAGE.value,
        ),
        SynonymRule(
            r"\bhasta donde llegan tus datos\b",
            "cobertura de datos",
            Intent.DATA_COVERAGE.value,
        ),
        SynonymRule(
            r"\bdesde cuando tienes informacion\b",
            "cobertura de datos",
            Intent.DATA_COVERAGE.value,
        ),
        SynonymRule(
            r"\bhasta cuando tienes datos\b",
            "cobertura de datos",
            Intent.DATA_COVERAGE.value,
        ),
        SynonymRule(
            r"\bhasta que fecha sabes\b",
            "cobertura de datos",
            Intent.DATA_COVERAGE.value,
        ),
        SynonymRule(
            r"\bque periodo manejas\b",
            "cobertura de datos",
            Intent.DATA_COVERAGE.value,
        ),
        SynonymRule(
            r"\bque periodo cubres\b",
            "cobertura de datos",
            Intent.DATA_COVERAGE.value,
        ),
        SynonymRule(
            r"\bque rango cubres\b",
            "cobertura de datos",
            Intent.DATA_COVERAGE.value,
        ),
        SynonymRule(
            r"\bque anos tienes\b",
            "cobertura de datos",
            Intent.DATA_COVERAGE.value,
        ),
        SynonymRule(
            r"\bque años tienes\b",
            "cobertura de datos",
            Intent.DATA_COVERAGE.value,
        ),
        SynonymRule(r"\bcobertura de datos\b", "cobertura de datos", Intent.DATA_COVERAGE.value),
        # Metaconocimiento
        SynonymRule(
            r"\bque tipo de informacion tienes\b",
            "que informacion tienes",
            Intent.CAPABILITY_DISCOVERY.value,
        ),
        SynonymRule(
            r"\bque informacion tienes\b",
            "que informacion tienes",
            Intent.CAPABILITY_DISCOVERY.value,
        ),
        SynonymRule(r"\bque sabes\b", "que informacion tienes", Intent.CAPABILITY_DISCOVERY.value),
        SynonymRule(r"\bque datos tienes\b", "que informacion tienes", Intent.CAPABILITY_DISCOVERY.value),
        SynonymRule(r"\bque conoces\b", "que informacion tienes", Intent.CAPABILITY_DISCOVERY.value),
        SynonymRule(
            r"\bque puedes responder\b",
            "que puedes hacer",
            Intent.CAPABILITY_DISCOVERY.value,
        ),
        SynonymRule(
            r"\bque puedes hacer\b",
            "que puedes hacer",
            Intent.CAPABILITY_DISCOVERY.value,
        ),
        # Concentración del negocio
        SynonymRule(
            r"\bdonde esta la mayor concentracion\b",
            "donde esta concentrado el negocio",
            Intent.BUSINESS_CONCENTRATION.value,
        ),
        SynonymRule(
            r"\bdonde se concentra el negocio\b",
            "donde esta concentrado el negocio",
            Intent.BUSINESS_CONCENTRATION.value,
        ),
        SynonymRule(
            r"\bdonde esta la mayor actividad\b",
            "donde esta concentrado el negocio",
            Intent.BUSINESS_CONCENTRATION.value,
        ),
        SynonymRule(
            r"\bquien mueve mas dinero\b",
            "donde esta concentrado el negocio",
            Intent.BUSINESS_CONCENTRATION.value,
        ),
        SynonymRule(
            r"\bdonde esta el negocio\b",
            "donde esta concentrado el negocio",
            Intent.BUSINESS_CONCENTRATION.value,
        ),
        # Insights ejecutivos
        SynonymRule(
            r"\bque hallazgos encontraste\b",
            "que hallazgos detectaste",
            Intent.EXECUTIVE_INSIGHTS.value,
        ),
        SynonymRule(
            r"\bque encontraste raro\b",
            "que hallazgos detectaste",
            Intent.EXECUTIVE_INSIGHTS.value,
        ),
        SynonymRule(
            r"\bque paso raro\b",
            "que hallazgos detectaste",
            Intent.EXECUTIVE_INSIGHTS.value,
        ),
        SynonymRule(
            r"\bque viste interesante\b",
            "que hallazgos detectaste",
            Intent.EXECUTIVE_INSIGHTS.value,
        ),
        SynonymRule(
            r"\bque descubriste\b",
            "que hallazgos detectaste",
            Intent.EXECUTIVE_INSIGHTS.value,
        ),
        SynonymRule(
            r"\bque detectaste\b",
            "que hallazgos detectaste",
            Intent.EXECUTIVE_INSIGHTS.value,
        ),
        SynonymRule(
            r"\bque insights tienes\b",
            "que hallazgos detectaste",
            Intent.EXECUTIVE_INSIGHTS.value,
        ),
        # Clientes
        SynonymRule(
            r"\bquien es el cliente principal\b",
            "mejor cliente",
            Intent.TOP_CLIENTES.value,
        ),
        SynonymRule(
            r"\bquien nos compra mas\b",
            "mejor cliente",
            Intent.TOP_CLIENTES.value,
        ),
        SynonymRule(r"\bquien compra mas\b", "mejor cliente", Intent.TOP_CLIENTES.value),
        SynonymRule(r"\bcliente mas grande\b", "mejor cliente", Intent.TOP_CLIENTES.value),
        SynonymRule(r"\bcliente mas fuerte\b", "mejor cliente", Intent.TOP_CLIENTES.value),
        SynonymRule(
            r"\bcliente mas importante\b",
            "mejor cliente",
            Intent.TOP_CLIENTES.value,
        ),
        SynonymRule(
            r"\bcliente mas fuerte del ano\b",
            "mejor cliente",
            Intent.TOP_CLIENTES.value,
        ),
        SynonymRule(
            r"\bcliente mas fuerte del anio\b",
            "mejor cliente",
            Intent.TOP_CLIENTES.value,
        ),
        SynonymRule(r"\bcliente principal\b", "mejor cliente", Intent.TOP_CLIENTES.value),
        SynonymRule(r"\bcliente dominante\b", "mejor cliente", Intent.TOP_CLIENTES.value),
        # Proveedores
        SynonymRule(r"\bquien nos vende mas\b", "mejor proveedor", Intent.TOP_PROVEEDORES.value),
        SynonymRule(r"\bquien vende mas\b", "mejor proveedor", Intent.TOP_PROVEEDORES.value),
        SynonymRule(
            r"\bproveedor mas fuerte\b",
            "mejor proveedor",
            Intent.TOP_PROVEEDORES.value,
        ),
        SynonymRule(
            r"\bproveedor mas importante\b",
            "mejor proveedor",
            Intent.TOP_PROVEEDORES.value,
        ),
        SynonymRule(r"\bproveedor principal\b", "mejor proveedor", Intent.TOP_PROVEEDORES.value),
        SynonymRule(
            r"\bproveedor dominante\b",
            "mejor proveedor",
            Intent.TOP_PROVEEDORES.value,
        ),
        # Riesgos y oportunidades
        SynonymRule(r"\bque te preocupa\b", "que riesgos detectas", Intent.RISKS.value),
        SynonymRule(r"\bque podria salir mal\b", "que riesgos detectas", Intent.RISKS.value),
        SynonymRule(r"\bdonde ves riesgos\b", "que riesgos detectas", Intent.RISKS.value),
        SynonymRule(
            r"\bque oportunidades observas\b",
            "que oportunidades detectas",
            Intent.OPPORTUNITIES.value,
        ),
        SynonymRule(
            r"\bdonde podemos crecer\b",
            "que oportunidades detectas",
            Intent.OPPORTUNITIES.value,
        ),
        SynonymRule(
            r"\bque hallazgos positivos encontraste\b",
            "que oportunidades detectas",
            Intent.OPPORTUNITIES.value,
        ),
        # Resumen ejecutivo ampliado
        SynonymRule(
            r"\bhaz un resumen ejecutivo\b",
            "resumen ejecutivo",
            Intent.EXECUTIVE_SUMMARY.value,
        ),
        SynonymRule(
            r"\bresumen empresarial\b",
            "resumen ejecutivo",
            Intent.EXECUTIVE_SUMMARY.value,
        ),
        SynonymRule(
            r"\bdame un resumen general\b",
            "resumen ejecutivo",
            Intent.EXECUTIVE_SUMMARY.value,
        ),
        SynonymRule(
            r"\bresumen del ano\b",
            "resumen ejecutivo",
            Intent.EXECUTIVE_SUMMARY.value,
        ),
        SynonymRule(
            r"\bresumen del anio\b",
            "resumen ejecutivo",
            Intent.EXECUTIVE_SUMMARY.value,
        ),
        # Bottom rankings
        SynonymRule(r"\bpeor cliente\b", "peor cliente", Intent.BOTTOM_CLIENTES.value),
        SynonymRule(
            r"\bcual es nuestro peor cliente\b",
            "peor cliente",
            Intent.BOTTOM_CLIENTES.value,
        ),
        SynonymRule(
            r"\bcliente menos importante\b",
            "peor cliente",
            Intent.BOTTOM_CLIENTES.value,
        ),
        SynonymRule(
            r"\bcliente con menos actividad\b",
            "peor cliente",
            Intent.BOTTOM_CLIENTES.value,
        ),
        SynonymRule(
            r"\bcliente que menos compra\b",
            "peor cliente",
            Intent.BOTTOM_CLIENTES.value,
        ),
        SynonymRule(
            r"\bquien nos compra menos\b",
            "peor cliente",
            Intent.BOTTOM_CLIENTES.value,
        ),
        SynonymRule(
            r"\bquien aporta menos\b",
            "peor cliente",
            Intent.BOTTOM_CLIENTES.value,
        ),
        SynonymRule(
            r"\bcliente mas pequeno\b",
            "peor cliente",
            Intent.BOTTOM_CLIENTES.value,
        ),
        SynonymRule(r"\bpeor proveedor\b", "peor proveedor", Intent.BOTTOM_PROVEEDORES.value),
        SynonymRule(
            r"\bproveedor menos activo\b",
            "peor proveedor",
            Intent.BOTTOM_PROVEEDORES.value,
        ),
        SynonymRule(
            r"\bproveedor mas pequeno\b",
            "peor proveedor",
            Intent.BOTTOM_PROVEEDORES.value,
        ),
        SynonymRule(
            r"\bquien nos vende menos\b",
            "peor proveedor",
            Intent.BOTTOM_PROVEEDORES.value,
        ),
        SynonymRule(
            r"\bcuenta menos utilizada\b",
            "cuenta menos utilizada",
            Intent.BOTTOM_CUENTAS.value,
        ),
        SynonymRule(
            r"\bcuenta con menor actividad\b",
            "cuenta menos utilizada",
            Intent.BOTTOM_CUENTAS.value,
        ),
        SynonymRule(
            r"\bcuenta menos usada\b",
            "cuenta menos utilizada",
            Intent.BOTTOM_CUENTAS.value,
        ),
        # Meses
        SynonymRule(r"\bmejor mes\b", "mejor mes", Intent.BEST_MONTH.value),
        SynonymRule(
            r"\bmes mas fuerte\b",
            "mejor mes",
            Intent.BEST_MONTH.value,
        ),
        SynonymRule(
            r"\bmes con mejor desempeno\b",
            "mejor mes",
            Intent.BEST_MONTH.value,
        ),
        SynonymRule(r"\bmes mas activo\b", "mejor mes", Intent.BEST_MONTH.value),
        SynonymRule(r"\bpeor mes\b", "peor mes", Intent.WORST_MONTH.value),
        SynonymRule(r"\bmes mas debil\b", "peor mes", Intent.WORST_MONTH.value),
        SynonymRule(
            r"\bmes con menor actividad\b",
            "peor mes",
            Intent.WORST_MONTH.value,
        ),
        SynonymRule(r"\bmes mas bajo\b", "peor mes", Intent.WORST_MONTH.value),
        # Crecimiento y caída
        SynonymRule(
            r"\bcliente que mas crecio\b",
            "cliente que mas crecio",
            Intent.CLIENTE_CRECIMIENTO.value,
        ),
        SynonymRule(
            r"\bcliente con mayor crecimiento\b",
            "cliente que mas crecio",
            Intent.CLIENTE_CRECIMIENTO.value,
        ),
        SynonymRule(
            r"\bquien esta creciendo mas\b",
            "cliente que mas crecio",
            Intent.CLIENTE_CRECIMIENTO.value,
        ),
        SynonymRule(
            r"\bque cliente crecio mas\b",
            "cliente que mas crecio",
            Intent.CLIENTE_CRECIMIENTO.value,
        ),
        SynonymRule(
            r"\bcliente que mas cayo\b",
            "cliente que mas cayo",
            Intent.CLIENTE_CAIDA.value,
        ),
        SynonymRule(
            r"\bcliente con menor crecimiento\b",
            "cliente que mas cayo",
            Intent.CLIENTE_CAIDA.value,
        ),
        SynonymRule(
            r"\bcliente en declive\b",
            "cliente que mas cayo",
            Intent.CLIENTE_CAIDA.value,
        ),
        SynonymRule(
            r"\bproveedor que mas crecio\b",
            "proveedor que mas crecio",
            Intent.PROVEEDOR_CRECIMIENTO.value,
        ),
        SynonymRule(
            r"\bproveedor con mayor crecimiento\b",
            "proveedor que mas crecio",
            Intent.PROVEEDOR_CRECIMIENTO.value,
        ),
        SynonymRule(
            r"\bproveedor que mas cayo\b",
            "proveedor que mas cayo",
            Intent.PROVEEDOR_CAIDA.value,
        ),
        SynonymRule(
            r"\bproveedor en declive\b",
            "proveedor que mas cayo",
            Intent.PROVEEDOR_CAIDA.value,
        ),
    )

    CANONICAL_BY_INTENT: dict[str, str] = {
        Intent.CAPABILITY_DISCOVERY.value: "¿Qué puedes hacer?",
        Intent.LIMITATIONS.value: "¿Qué limitaciones tienes?",
        Intent.FEATURE_SUPPORT.value: "¿Puedes hacer gráficas?",
        Intent.DATA_COVERAGE.value: "¿Cuál es la cobertura de datos?",
        Intent.TOP_CLIENTES.value: "¿Quién es nuestro mejor cliente?",
        Intent.TOP_PROVEEDORES.value: "¿Cuál es el proveedor principal?",
        Intent.BUSINESS_CONCENTRATION.value: "¿Dónde está concentrado el negocio?",
        Intent.EXECUTIVE_INSIGHTS.value: "¿Qué hallazgos detectaste?",
        Intent.BOTTOM_CLIENTES.value: "¿Cuál es nuestro peor cliente?",
        Intent.BOTTOM_PROVEEDORES.value: "¿Cuál es el peor proveedor?",
        Intent.BOTTOM_CUENTAS.value: "¿Cuál es la cuenta menos utilizada?",
        Intent.BEST_MONTH.value: "¿Cuál fue el mejor mes?",
        Intent.WORST_MONTH.value: "¿Cuál fue el peor mes?",
        Intent.CLIENTE_CRECIMIENTO.value: "¿Qué cliente creció más?",
        Intent.CLIENTE_CAIDA.value: "¿Qué cliente cayó más?",
        Intent.PROVEEDOR_CRECIMIENTO.value: "¿Qué proveedor creció más?",
        Intent.PROVEEDOR_CAIDA.value: "¿Qué proveedor cayó más?",
        Intent.EXECUTIVE_SUMMARY.value: "¿Cuál es el resumen ejecutivo?",
        Intent.RISKS.value: "¿Qué riesgos detectas?",
        Intent.OPPORTUNITIES.value: "¿Qué oportunidades detectas?",
    }

    def apply(self, text: str) -> tuple[str, str | None]:
        normalized = text.strip()
        intent_hint: str | None = None
        lowered = self._strip_accents(normalized.lower())

        for rule in self.REPLACEMENT_RULES:
            if re.search(rule.pattern, lowered):
                normalized = re.sub(rule.pattern, rule.replacement, normalized, flags=re.IGNORECASE)
                lowered = self._strip_accents(normalized.lower())
                if rule.intent_hint:
                    intent_hint = rule.intent_hint

        return normalized, intent_hint

    def canonical_question(self, intent: str) -> str | None:
        return self.CANONICAL_BY_INTENT.get(intent)

    @staticmethod
    def _strip_accents(text: str) -> str:
        import unicodedata

        decomposed = unicodedata.normalize("NFD", text)
        return "".join(char for char in decomposed if unicodedata.category(char) != "Mn")
