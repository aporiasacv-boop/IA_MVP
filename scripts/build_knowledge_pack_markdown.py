"""Genera el Business Knowledge Pack en knowledge_pack/ (Markdown)."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "knowledge_pack"


def write(path: str, content: str) -> None:
    file_path = ROOT / path
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content.strip() + "\n", encoding="utf-8")


CONCEPTS: dict[str, str] = {
    "cliente": """# Cliente

## Definición
Contraparte comercial que adquiere bienes o servicios de la empresa y genera ingresos o cuentas por cobrar.

## Cuándo aplica
Cuando existe relación comercial de venta, facturación o cobro hacia un tercero identificado como comprador.

## Cuándo no aplica
Cuando la entidad es una cuenta contable, un pasivo laboral, un impuesto o un concepto interno de agrupación sin relación comercial directa.

## Ejemplos
- Distribuidor que compra producto terminado.
- Cadena comercial con código de cliente en el sistema ERP.
- Cliente genérico de facturación masiva cuando el sistema no identifica al comprador final.

## Sinónimos
Comprador, cuenta por cobrar, deudor comercial, contraparte de venta.""",
    "proveedor": """# Proveedor

## Definición
Contraparte que suministra bienes, servicios o insumos a la empresa y genera obligaciones de pago o cuentas por pagar.

## Cuándo aplica
Cuando hay compras, servicios recibidos o pagos a terceros por suministro operativo.

## Cuándo no aplica
Cuando el registro corresponde a una cuenta de pasivo, nómina, impuesto o ajuste contable sin proveedor real.

## Ejemplos
- Proveedor de materia prima.
- Empresa de logística contratada.
- Servicios profesionales externos.

## Sinónimos
Acreedor, cuenta por pagar, vendor, suministrador.""",
    "cuenta-contable": """# Cuenta contable

## Definición
Elemento del catálogo contable que clasifica movimientos económicos según naturaleza, función y reporte financiero.

## Cuándo aplica
En registros del libro mayor, balances, estados de resultados y conciliaciones.

## Cuándo no aplica
Cuando se analiza relación comercial con clientes o proveedores sin distinguir la naturaleza contable del registro.

## Ejemplos
- Cuenta de activo circulante.
- Cuenta de pasivo por pagar.
- Cuenta de gasto operativo.

## Sinónimos
Cuenta del mayor, rubro contable, cuenta GL.""",
    "activo": """# Activo

## Definición
Recurso controlado por la empresa del que se espera obtener beneficio económico futuro.

## Cuándo aplica
En análisis de balance, liquidez, inversión y capacidad operativa.

## Cuándo no aplica
En rankings de clientes o proveedores sin segmentar por naturaleza contable.

## Ejemplos
- Efectivo y equivalentes.
- Inventarios.
- Propiedad, planta y equipo.

## Sinónimos
Recursos, activos económicos.""",
    "pasivo": """# Pasivo

## Definición
Obligación presente de la empresa derivada de eventos pasados que probablemente requiera salida de recursos.

## Cuándo aplica
En análisis de solvencia, deuda, obligaciones laborales y fiscales.

## Cuándo no aplica
Cuando se confunde con contrapartes comerciales en campos de cliente o proveedor del ERP.

## Ejemplos
- Cuentas por pagar a proveedores.
- Pasivos laborales.
- Impuestos por pagar.

## Sinónimos
Obligaciones, deudas, pasivos exigibles.""",
    "ingreso": """# Ingreso

## Definición
Incremento en los beneficios económicos durante un periodo, generalmente asociado a ventas o prestación de servicios.

## Cuándo aplica
En análisis de desempeño comercial, facturación y reconocimiento de ingresos.

## Cuándo no aplica
En movimientos de traspaso interno, ajustes contables o reclasificaciones sin efecto comercial.

## Ejemplos
- Venta de producto terminado.
- Ingresos por servicios.
- Ingresos recurrentes por contrato.

## Sinónimos
Revenue, ventas, ingresos operativos.""",
    "costo": """# Costo

## Definición
Consumo de recursos directamente relacionado con la producción o entrega de bienes y servicios vendidos.

## Cuándo aplica
En análisis de margen, rentabilidad por producto y eficiencia productiva.

## Cuándo no aplica
En gastos administrativos o financieros no vinculados a la producción directa.

## Ejemplos
- Materia prima consumida.
- Mano de obra directa de planta.
- Costos variables de manufactura.

## Sinónimos
Costo de ventas, costo directo, COGS.""",
    "gasto": """# Gasto

## Definición
Salida de recursos o consumo de servicios para operar la empresa, no necesariamente ligada a un producto específico.

## Cuándo aplica
En control presupuestal, estructura de costos fijos y eficiencia administrativa.

## Cuándo no aplica
En costos directamente atribuibles a la producción de un SKU concreto.

## Ejemplos
- Gastos de oficina.
- Servicios generales.
- Depreciación administrativa.

## Sinónimos
Erogación, gasto operativo, expense.""",
    "nomina": """# Nómina

## Definición
Conjunto de obligaciones y pagos relacionados con la compensación del personal y cargas laborales asociadas.

## Cuándo aplica
En análisis de pasivos laborales, flujo de caja de nómina y cumplimiento de obligaciones de seguridad social.

## Cuándo no aplica
Cuando un registro de nómina aparece en campos de proveedor o cliente y debe tratarse como cuenta contable.

## Ejemplos
- Sueldos por pagar.
- Provisiones de aguinaldo o PTU.
- Retenciones laborales.

## Sinónimos
Compensación, payroll, pasivos laborales.""",
    "banco": """# Banco

## Definición
Institución financiera o cuenta bancaria utilizada para administrar liquidez, pagos y cobros de la empresa.

## Cuándo aplica
En conciliaciones, tesorería y análisis de flujo de efectivo.

## Cuándo no aplica
En análisis de relación comercial con clientes o proveedores operativos.

## Ejemplos
- Cuenta de cheques operativa.
- Línea de crédito revolvente.
- Inversiones temporales.

## Sinónimos
Cuenta bancaria, tesorería, institución financiera.""",
    "impuesto": """# Impuesto

## Definición
Obligación fiscal derivada de regulación tributaria aplicable a ingresos, nómina, ventas o utilidades.

## Cuándo aplica
En cumplimiento fiscal, provisiones y análisis de flujo de caja neto.

## Cuándo no aplica
En rankings comerciales de clientes o proveedores.

## Ejemplos
- IVA por pagar o acreditable.
- ISR estimado.
- Retenciones fiscales.

## Sinónimos
Tributo, contribución, obligación fiscal.""",
    "centro-de-costo": """# Centro de costo

## Definición
Unidad organizativa o estructura analítica para acumular y controlar gastos o costos por área, planta o función.

## Cuándo aplica
En control presupuestal, rentabilidad por área y asignación de gastos indirectos.

## Cuándo no aplica
En análisis de contrapartes comerciales externas.

## Ejemplos
- Planta de producción.
- Área de ventas.
- Centro de distribución.

## Sinónimos
Centro de responsabilidad, unidad de negocio operativa.""",
    "producto": """# Producto

## Definición
Bien tangible o intangible que la empresa fabrica, comercializa o distribuye.

## Cuándo aplica
En análisis de portafolio, rotación de inventario y rentabilidad por SKU.

## Cuándo no aplica
En movimientos puramente contables sin referencia a un artículo comercial.

## Ejemplos
- Producto terminado para venta.
- Materia prima.
- Producto en proceso.

## Sinónimos
Artículo, SKU, ítem comercial.""",
    "orden-de-compra": """# Orden de compra

## Definición
Documento o registro que autoriza la adquisición de bienes o servicios bajo condiciones acordadas.

## Cuándo aplica
En control de abastecimiento, compromisos de pago y seguimiento de proveedores.

## Cuándo no aplica
En ajustes contables manuales sin proceso de compra formal.

## Ejemplos
- Orden de materia prima.
- Orden de servicios de mantenimiento.
- Orden de empaque.

## Sinónimos
PO, pedido de compra, requisición aprobada.""",
    "inventario": """# Inventario

## Definición
Existencias de materiales, producto en proceso o terminado disponibles para operación o venta.

## Cuándo aplica
En control de almacén, rotación, obsolescencia y costo de ventas.

## Cuándo no aplica
En análisis de relaciones comerciales con clientes.

## Ejemplos
- Inventario de materia prima.
- Producto terminado en almacén.
- Inventario en tránsito.

## Sinónimos
Existencias, stock, almacén.""",
    "produccion": """# Producción

## Definición
Proceso de transformación de insumos en producto terminado conforme a especificaciones y planes operativos.

## Cuándo aplica
En eficiencia de planta, cumplimiento de plan maestro y análisis de capacidad.

## Cuándo no aplica
En transacciones financieras sin vínculo con operación fabril.

## Ejemplos
- Orden de fabricación.
- Consumo de BOM.
- Rendimiento de línea.

## Sinónimos
Manufactura, fabricación, operación productiva.""",
    "calidad": """# Calidad

## Definición
Grado en que un producto, servicio o proceso cumple especificaciones, regulaciones y expectativas del cliente.

## Cuándo aplica
En industrias reguladas, liberación de lotes, auditorías y mejora continua.

## Cuándo no aplica
En clasificación contable de contrapartes o cuentas del mayor.

## Ejemplos
- Control de calidad en recepción.
- Liberación de lote farmacéutico.
- No conformidades y CAPA.

## Sinónimos
QA, QC, conformidad, compliance de producto.""",
    "kpis": """# KPIs

## Definición
Indicadores clave de desempeño que resumen el avance hacia objetivos operativos, comerciales o financieros.

## Cuándo aplica
En tableros ejecutivos, seguimiento periódico y gestión por objetivos.

## Cuándo no aplica
Cuando un indicador no tiene definición, fuente de datos ni periodicidad acordada.

## Ejemplos
- Rotación de inventario.
- Días de cartera.
- Cumplimiento de producción.

## Sinónimos
Indicadores, métricas, OKR operativos.""",
    "riesgo": """# Riesgo

## Definición
Evento o condición que puede afectar negativamente el cumplimiento de objetivos financieros, operativos o de cumplimiento.

## Cuándo aplica
En evaluación de contrapartes, continuidad operativa, concentración y calidad de datos.

## Cuándo no aplica
Cuando se confunde con una oportunidad de mejora sin impacto adverso potencial.

## Ejemplos
- Concentración de ventas en pocos clientes.
- Dependencia de un solo proveedor crítico.
- Datos maestros inconsistentes.

## Sinónimos
Exposición, amenaza, vulnerabilidad.""",
    "oportunidad": """# Oportunidad

## Definición
Condición favorable que puede mejorar desempeño comercial, eficiencia operativa o posición financiera si se aprovecha.

## Cuándo aplica
En priorización comercial, optimización de compras y mejora de procesos.

## Cuándo no aplica
Cuando no existe evidencia suficiente para sustentar una acción concreta.

## Ejemplos
- Cliente con volumen creciente y margen saludable.
- Consolidación de compras con mejor negociación.
- Reducción de inventario obsoleto.

## Sinónimos
Potencial, upside, mejora identificada.""",
    "facturacion": """# Facturación

## Definición
Emisión de comprobantes fiscales o documentos de venta que reconocen ingresos y derechos de cobro.

## Cuándo aplica
En análisis comercial, cumplimiento fiscal y cuentas por cobrar.

## Cuándo no aplica
En movimientos internos sin efecto fiscal o comercial externo.

## Ejemplos
- Factura a cliente comercial.
- Nota de crédito.
- Facturación masiva a cliente genérico.

## Sinónimos
Billing, emisión de CFDI, documento de venta.""",
    "cobranza": """# Cobranza

## Definición
Proceso de gestionar y recuperar montos adeudados por clientes dentro de plazos acordados.

## Cuándo aplica
En gestión de cartera, flujo de caja y riesgo crediticio.

## Cuándo no aplica
En pagos a proveedores o pasivos laborales.

## Ejemplos
- Seguimiento de facturas vencidas.
- Gestión de límites de crédito.
- Conciliación de pagos de clientes.

## Sinónimos
Recuperación de cartera, collections, gestión de CxC.""",
    "cuentas-por-pagar": """# Cuentas por pagar

## Definición
Obligaciones pendientes de pago a proveedores u otros acreedores por bienes o servicios recibidos.

## Cuándo aplica
En tesorería, negociación con proveedores y análisis de pasivo circulante.

## Cuándo no aplica
En cuentas de nómina, impuestos o ajustes sin proveedor operativo.

## Ejemplos
- Facturas de proveedor pendientes.
- Anticipos a proveedores.
- Programación de pagos.

## Sinónimos
CxP, acreedores, pasivo comercial.""",
    "cuentas-por-cobrar": """# Cuentas por cobrar

## Definición
Derechos de cobro pendientes derivados de ventas o servicios facturados a clientes.

## Cuándo aplica
En análisis de cartera, riesgo crediticio y liquidez.

## Cuándo no aplica
En pasivos laborales o cuentas contables sin cliente asociado.

## Ejemplos
- Facturas pendientes de cobro.
- Anticipos de clientes.
- Notas de crédito por aplicar.

## Sinónimos
CxC, deudores, cartera de clientes.""",
    "margen": """# Margen

## Definición
Diferencia entre ingresos y costos asociados, expresada en valor absoluto o relativo.

## Cuándo aplica
En rentabilidad por producto, cliente, canal o periodo.

## Cuándo no aplica
Sin segregación adecuada de costos directos e indirectos.

## Ejemplos
- Margen bruto por producto.
- Margen por cliente.
- Margen de contribución.

## Sinónimos
Rentabilidad unitaria, spread comercial.""",
    "flujo-de-efectivo": """# Flujo de efectivo

## Definición
Entradas y salidas netas de efectivo derivadas de operación, inversión y financiamiento.

## Cuándo aplica
En tesorería, planeación financiera y evaluación de liquidez.

## Cuándo no aplica
En rankings de contrapartes sin contexto de caja.

## Ejemplos
- Cobros de clientes.
- Pagos a proveedores.
- Pago de nómina e impuestos.

## Sinónimos
Cash flow, flujo de caja.""",
    "conciliacion-bancaria": """# Conciliación bancaria

## Definición
Proceso de comparar registros contables de bancos con extractos bancarios para detectar diferencias.

## Cuándo aplica
En cierre contable, control de tesorería y detección de errores.

## Cuándo no aplica
En análisis comercial de clientes o proveedores.

## Ejemplos
- Partidas en tránsito.
- Comisiones bancarias no registradas.
- Depósitos en tránsito.

## Sinónimos
Bank reconciliation, cuadre de bancos.""",
    "presupuesto": """# Presupuesto

## Definición
Plan financiero y operativo que establece metas de ingresos, costos, gastos e inversiones para un periodo.

## Cuándo aplica
En control de gestión, variaciones y planeación anual o rolling forecast.

## Cuándo no aplica
En consultas puntuales sin baseline presupuestal definido.

## Ejemplos
- Presupuesto de ventas por canal.
- Presupuesto de gastos por área.
- Capex planificado.

## Sinónimos
Budget, plan financiero, forecast.""",
    "entidad-canónica": """# Entidad canónica

## Definición
Representación unificada de una contraparte o concepto empresarial consolidando alias, códigos y variaciones de nombre.

## Cuándo aplica
En master data, análisis transaccional y generación de evidencia empresarial consistente.

## Cuándo no aplica
Cuando cada alias se trata como entidad distinta sin reglas de consolidación.

## Ejemplos
- Variantes de nombre de una misma cadena comercial.
- RFC o código maestro como ancla de identidad.
- Clasificación final como cliente, proveedor o cuenta.

## Sinónimos
Golden record, entidad maestra, identidad canónica.""",
    "contraparte": """# Contraparte

## Definición
Tercero o entidad con la que la organización mantiene relación económica, contractual o contable.

## Cuándo aplica
En análisis de clientes, proveedores, bancos, autoridades y empleados.

## Cuándo no aplica
Cuando el registro es solo un rubro contable sin tercero real asociado.

## Ejemplos
- Cliente comercial.
- Proveedor de insumos.
- Cuenta contable mal asignada como contraparte.

## Sinónimos
Tercero, party, entidad relacionada.""",
}

GLOSSARY_TERMS = [
    ("Activo", "Recurso que la empresa controla y del que espera beneficio futuro."),
    ("Pasivo", "Obligación actual que probablemente requiera salida de recursos."),
    ("Capital", "Aportación de los propietarios más resultados acumulados."),
    ("Ingreso", "Entrada de beneficios económicos por ventas o servicios."),
    ("Costo", "Recursos consumidos para producir lo vendido."),
    ("Gasto", "Consumo de recursos para operar la empresa."),
    ("Margen", "Diferencia entre ingresos y costos asociados."),
    ("Liquidez", "Capacidad de cumplir obligaciones de corto plazo."),
    ("Solvencia", "Capacidad de cumplir obligaciones totales en el tiempo."),
    ("Flujo de caja", "Entradas y salidas netas de efectivo."),
    ("Cliente", "Quien compra bienes o servicios a la empresa."),
    ("Proveedor", "Quien suministra bienes o servicios a la empresa."),
    ("Cuenta contable", "Clasificador de movimientos en el mayor general."),
    ("Centro de costo", "Estructura para acumular gastos por área o planta."),
    ("Inventario", "Existencias disponibles para operación o venta."),
    ("Producción", "Transformación de insumos en producto terminado."),
    ("Calidad", "Cumplimiento de especificaciones y regulaciones."),
    ("KPI", "Indicador clave para medir desempeño."),
    ("Riesgo", "Posible efecto adverso sobre objetivos."),
    ("Oportunidad", "Condición favorable aprovechable con evidencia."),
    ("Facturación", "Emisión de documentos de venta o ingreso."),
    ("Cobranza", "Gestión de pagos pendientes de clientes."),
    ("Cuentas por cobrar", "Derechos de cobro a clientes."),
    ("Cuentas por pagar", "Obligaciones con proveedores."),
    ("Conciliación", "Cuadre entre dos fuentes de información."),
    ("Presupuesto", "Plan financiero para un periodo."),
    ("Forecast", "Proyección actualizada de resultados o caja."),
    ("ERP", "Sistema integrado de gestión empresarial."),
    ("Libro mayor", "Registro contable de todas las cuentas."),
    ("Diario general", "Registro cronológico de pólizas contables."),
    ("Contraparte", "Tercero con relación económica con la empresa."),
    ("Entidad canónica", "Identidad unificada de una contraparte."),
    ("Alias", "Variante de nombre de una misma entidad."),
    ("Ranking", "Ordenamiento de entidades por un criterio medible."),
    ("Concentración", "Dependencia elevada de pocas entidades o rubros."),
    ("Estacionalidad", "Variación recurrente por temporada o calendario."),
    ("Rotación", "Velocidad con que un recurso se renueva."),
    ("Días de cartera", "Tiempo promedio de cobro a clientes."),
    ("Días de pago", "Tiempo promedio de pago a proveedores."),
    ("Compliance", "Cumplimiento de normas y políticas aplicables."),
    ("Auditoría", "Revisión sistemática de registros y controles."),
    ("Data mart", "Conjunto de datos preparado para análisis."),
    ("Evidencia", "Hecho verificable que sustenta una conclusión."),
    ("Limitación", "Restricción o vacío que impide concluir con certeza."),
    ("Confianza", "Grado de certeza asociado a un hallazgo."),
    ("Escenario", "Contexto de análisis con objetivo y preguntas típicas."),
    ("Ontología", "Clasificación semántica de entidades y roles."),
    ("Perfil de entidad", "Resumen de comportamiento transaccional."),
    ("Objeto de conocimiento", "Paquete estructurado de hechos y señales."),
    ("Razonamiento empresarial", "Conclusiones derivadas de reglas sobre evidencia."),
    ("Paquete de evidencia", "Contrato estructurado para consumo por IA."),
    ("Asistente empresarial", "Interfaz que responde con base en evidencia disponible."),
]

FAQ_ITEMS = [
    (
        "¿Cómo te llamas?",
        "Soy Olnatura Intelligence, el asistente de inteligencia empresarial desarrollado "
        "para transformar datos corporativos en conocimiento confiable que apoye la toma de decisiones.",
    ),
    (
        "¿Quién eres?",
        "Soy Olnatura Intelligence. Respondo utilizando evidencia empresarial, no invento "
        "información, diferencio hechos de recomendaciones e indico limitaciones cuando la "
        "evidencia es insuficiente.",
    ),
    (
        "¿Qué puedes hacer?",
        "Puedo ayudarte a explorar información empresarial estructurada: clientes, proveedores, "
        "cuentas contables, indicadores y análisis ejecutivos, siempre con base en evidencia disponible.",
    ),
    (
        "¿Cómo obtienes la información?",
        "Obtengo la información a partir de datos corporativos estructurados, perfiles de entidades, "
        "ontología empresarial y paquetes de evidencia preparados para cada consulta.",
    ),
    ("¿Qué información analizas?", "Analizo datos transaccionales, perfiles de entidades, clasificaciones semánticas y reglas empresariales genéricas aplicables a empresas manufactureras y farmacéuticas."),
    ("¿Qué es un cliente?", "Es una contraparte que compra bienes o servicios y puede generar ingresos o cuentas por cobrar."),
    ("¿Qué es un proveedor?", "Es una contraparte que suministra bienes o servicios y puede generar cuentas por pagar."),
    ("¿Qué es una cuenta contable?", "Es un clasificador del catálogo contable para registrar movimientos económicos en el mayor general."),
    ("¿Por qué una cuenta contable no es un proveedor?", "Porque representa un rubro contable, no necesariamente un tercero comercial real. Aparecer en un campo de proveedor del ERP no convierte automáticamente la cuenta en proveedor."),
    ("¿Qué significa un riesgo?", "Es una condición o evento que puede afectar negativamente objetivos financieros, operativos o de cumplimiento."),
    ("¿Qué significa una oportunidad?", "Es una condición favorable identificada con evidencia que podría mejorar desempeño comercial u operativo."),
    ("¿Cómo calculas los rankings?", "Los rankings ordenan entidades por un criterio medible, por ejemplo volumen de movimientos o montos, excluyendo cuando corresponda cuentas contables o conceptos internos."),
    ("¿Puedes inventar datos?", "No. Si la evidencia es insuficiente, debo indicarlo explícitamente."),
    ("¿Usas SQL directamente en las respuestas?", "No en la capa de respuesta ejecutiva. La evidencia se entrega en paquetes estructurados preparados previamente."),
    ("¿Qué es PUBLICO EN GENERAL?", "Es un concepto de cliente genérico frecuente en ERP cuando no se identifica al comprador final en la transacción."),
    ("¿Qué es una entidad canónica?", "Es la identidad unificada de una contraparte consolidando alias y códigos."),
    ("¿Qué es un KPI?", "Es un indicador clave de desempeño con meta, fuente y periodicidad definidas."),
    ("¿Qué es concentración?", "Es la dependencia elevada de pocas entidades, productos o rubros en el total."),
    ("¿Qué es estacionalidad?", "Es la variación recurrente de actividad por temporada, calendario fiscal o ciclos de demanda."),
    ("¿Qué es liquidez?", "Es la capacidad de la empresa para cumplir obligaciones de corto plazo."),
    ("¿Qué es margen?", "Es la diferencia entre ingresos y costos asociados a una venta, producto o cliente."),
    ("¿Qué es nómina por pagar?", "Es un pasivo laboral que refleja obligaciones de pago al personal, no un proveedor comercial."),
    ("¿Por qué excluir nómina de rankings de proveedores?", "Porque distorsiona el análisis comercial al mezclar pasivos laborales con contrapartes de suministro."),
    ("¿Qué es un cliente estratégico?", "Es un cliente con recurrencia, continuidad e impacto económico relevante según criterios definidos por la empresa."),
    ("¿Qué preguntas no debes responder sin evidencia?", "Cualquier pregunta que requiera cifras, políticas internas o conclusiones no sustentadas en el paquete de evidencia."),
    ("¿Qué es un escenario de análisis?", "Es un contexto con objetivo, preguntas típicas y conocimiento requerido, por ejemplo análisis de clientes o liquidez."),
    ("¿Qué es calidad de datos?", "Es el grado en que los datos maestros y transaccionales son completos, consistentes y confiables."),
    ("¿Qué es un alias de entidad?", "Es una variante de nombre que puede resolverse a una entidad canónica."),
    ("¿Qué es una regla empresarial?", "Es una directriz genérica que guía clasificación, exclusión o interpretación de datos."),
    ("¿Qué es evidencia?", "Es un hecho verificable con origen, confianza y trazabilidad."),
    ("¿Qué es una limitación?", "Es una restricción o vacío que impide responder con certeza."),
    ("¿Qué es un perfil de entidad?", "Es un resumen de comportamiento transaccional y señales asociadas a una entidad."),
    ("¿Qué es ontología empresarial?", "Es la clasificación semántica de roles y naturalezas de entidades."),
    ("¿Qué diferencia hay entre costo y gasto?", "El costo se asocia directamente a lo vendido; el gasto sostiene la operación general."),
    ("¿Qué es una orden de compra?", "Es la autorización formal para adquirir bienes o servicios."),
    ("¿Qué es inventario?", "Son existencias de materiales o producto disponibles para operación o venta."),
    ("¿Qué es producción?", "Es el proceso de transformar insumos en producto terminado."),
    ("¿Qué es compliance?", "Es el cumplimiento de normas, regulaciones y controles aplicables."),
    ("¿Qué es un data mart?", "Es un conjunto de datos preparado para consultas y análisis empresariales."),
    ("¿Qué es un movimiento contable?", "Es un registro en el diario general que afecta una o más cuentas."),
    ("¿Qué es un centro de costo?", "Es una unidad para acumular y controlar gastos por área o planta."),
    ("¿Qué es cuentas por cobrar?", "Son derechos de cobro pendientes de clientes."),
    ("¿Qué es cuentas por pagar?", "Son obligaciones pendientes con proveedores."),
    ("¿Qué es conciliación bancaria?", "Es el cuadre entre registros contables y extractos bancarios."),
    ("¿Qué es presupuesto?", "Es el plan financiero y operativo de un periodo."),
    ("¿Qué es forecast?", "Es una proyección actualizada de resultados o flujo de caja."),
    ("¿Qué es un pasivo laboral?", "Es una obligación relacionada con compensación o cargas del personal."),
    ("¿Qué es un impuesto por pagar?", "Es una obligación fiscal pendiente de liquidación."),
    ("¿Qué es un concepto interno?", "Es una entidad de agrupación operativa o contable sin contraparte comercial externa."),
    ("¿Qué es trazabilidad?", "Es la capacidad de seguir el origen de un dato o conclusión."),
    ("¿Qué es confianza en un hallazgo?", "Es el grado de certeza asociado a la evidencia disponible. También puede aparecer como confidence en metadatos técnicos."),
    ("¿Qué significa confidence?", "Es el nivel de confianza numérico (0 a 1) asociado a una respuesta o hallazgo según la evidencia disponible."),
    ("¿Qué significa una recomendación?", "Es una sugerencia de acción derivada de hechos verificables. Debe distinguirse claramente de los datos confirmados."),
    ("¿Qué hace el planificador semántico?", "Interpreta la intención de la pregunta y determina qué conocimiento y razonamiento se requiere."),
    ("¿Qué es el paquete de evidencia?", "Es el contrato estructurado que alimenta respuestas de IA sin exponer SQL."),
]

RULES = [
    ("excluir-cuentas-contables-ranking-clientes", "Excluir cuentas contables de rankings de clientes", "Las cuentas del mayor general no representan contrapartes comerciales y distorsionan rankings de clientes."),
    ("excluir-cuentas-contables-ranking-proveedores", "Excluir cuentas contables de rankings de proveedores", "Los rubros contables registrados erróneamente como proveedor no deben competir con proveedores reales."),
    ("excluir-nomina-ranking-proveedores", "Excluir nómina y pasivos laborales de rankings de proveedores", "La nómina por pagar es un pasivo laboral, no un proveedor de suministro."),
    ("excluir-impuestos-ranking-comercial", "Excluir impuestos de rankings comerciales", "Las obligaciones fiscales no son clientes ni proveedores operativos."),
    ("cliente-estrategico-recurrencia", "Cliente estratégico: recurrencia", "Un cliente estratégico suele presentar recurrencia en el tiempo, no solo un pico aislado."),
    ("cliente-estrategico-continuidad", "Cliente estratégico: continuidad", "La continuidad de relación comercial es señal de relevancia estratégica."),
    ("cliente-estrategico-impacto", "Cliente estratégico: impacto económico", "El impacto económico relativo debe evaluarse frente al total, sin umbrales fijos universales."),
    ("proveedor-critico-dependencia", "Proveedor crítico por dependencia", "Alta dependencia de un solo proveedor para insumo crítico constituye riesgo de continuidad."),
    ("concepto-interno-no-comercial", "Tratar conceptos internos aparte", "Los conceptos internos o puente deben analizarse en contexto, no como clientes comerciales típicos."),
    ("cliente-generico-bucket", "Cliente genérico como bucket especial", "Clientes genéricos de facturación masiva deben separarse o etiquetarse en análisis comercial."),
    ("alias-resolver-canonical", "Resolver alias a entidad canónica", "Variantes de nombre deben consolidarse antes de comparar o rankear."),
    ("codigo-numerico-cuenta", "Código numérico largo sugiere cuenta", "Códigos numéricos de ocho dígitos en campos de tercero suelen ser cuentas contables mal ubicadas."),
    ("prefijo-cliente-comercial", "Prefijos comerciales de cliente", "Prefijos tipo C### en catálogos ERP suelen indicar cliente comercial, sujeto a validación."),
    ("validar-naturaleza-antes-ranking", "Validar naturaleza antes de rankear", "Siempre clasificar la entidad antes de ordenar por volumen o monto."),
    ("no-mezclar-pasivo-comercial", "No mezclar pasivo con comercial", "Pasivos laborales y comerciales responden a preguntas distintas."),
    ("evidencia-antes-conclusion", "Conclusión solo con evidencia", "No emitir recomendaciones sin hechos verificables en el paquete."),
    ("declarar-limitaciones", "Declarar limitaciones explícitas", "Si falta EKO, ERO o entidad resuelta, indicarlo como limitación."),
    ("separar-hecho-interpretacion", "Separar hecho de interpretación", "Los hechos transaccionales deben distinguirse de conclusiones ejecutivas."),
    ("ranking-por-criterio-declarado", "Declarar criterio de ranking", "Todo ranking debe indicar si ordena por movimientos, montos u otro criterio."),
    ("excluir-ajustes-contables", "Excluir ajustes contables de análisis comercial", "Ajustes y reclasificaciones no deben tratarse como ventas o compras."),
    ("concentracion-requiere-contexto", "Concentración requiere contexto", "La concentración debe interpretarse con el total y el periodo analizado."),
    ("estacionalidad-periodo", "Estacionalidad por periodo", "Comparar periodos homogéneos al evaluar estacionalidad."),
    ("liquidez-no-es-ventas", "Liquidez no equivale a ventas", "Flujo de caja y facturación responden a dinámicas diferentes."),
    ("calidad-dato-previo", "Calidad de dato previo al análisis", "Inconsistencias maestras deben resolverse o declararse antes de concluir."),
    ("riesgo-vs-oportunidad", "Distinguir riesgo de oportunidad", "Un mismo hallazgo puede ser riesgo u oportunidad según perspectiva y evidencia."),
    ("no-inferir-politica-interna", "No inferir políticas internas", "Sin reglas oficiales adoptadas, usar solo directrices genéricas."),
    ("tercero-vs-rubro", "Tercero versus rubro contable", "Verificar si existe tercero real antes de asignar rol comercial."),
    ("movimiento-no-es-entidad", "Movimiento no es entidad", "Un movimiento elevado no define por sí solo la naturaleza de la entidad."),
    ("perfil-complementa-ranking", "Perfil complementa ranking", "El ranking debe complementarse con perfil y señales."),
    ("ontologia-guia-clasificacion", "Ontología guía clasificación", "La ontología empresarial orienta roles y secciones de conocimiento."),
    ("ero-sobre-eko", "Razonamiento sobre conocimiento", "Las recomendaciones deben apoyarse en conocimiento estructurado previo."),
    ("excluir-duplicados-alias", "Excluir duplicados por alias", "No contar dos veces la misma entidad canónica por alias distintos."),
    ("proveedor-servicios-vs-bienes", "Proveedor de servicios versus bienes", "Segmentar análisis según tipo de suministro cuando sea relevante."),
    ("inventario-no-cliente", "Inventario no es cliente", "Existencias y contrapartes comerciales son dominios distintos."),
    ("produccion-no-finanzas", "Producción no es finanzas", "KPIs de planta no deben confundirse con KPIs de tesorería."),
    ("impuesto-no-proveedor", "Impuesto no es proveedor", "Obligaciones fiscales tienen tratamiento de compliance, no de abastecimiento."),
    ("banco-no-proveedor-operativo", "Banco no es proveedor operativo", "Instituciones financieras se analizan en tesorería."),
    ("cobranza-requiere-cxc", "Cobranza requiere cuentas por cobrar", "Gestión de cobranza necesita cartera identificada."),
    ("compras-requiere-proveedor", "Compras requiere proveedor real", "Análisis de abastecimiento excluye cuentas mal clasificadas."),
    ("transparencia-en-exclusiones", "Transparencia en exclusiones", "Documentar qué se excluyó y por qué en rankings y escenarios."),
    ("neutralidad-sectorial", "Neutralidad sectorial", "Usar lenguaje aplicable a manufactura y farmacéutica sin supuestos de marca."),
    ("sustituible-por-politica", "Reglas sustituibles por política oficial", "Estas reglas son genéricas y deben reemplazarse por políticas adoptadas por la empresa."),
]

EXECUTIVE = {
    "director-general.md": """# Expectativas de un Director General

## Enfoque habitual
- Visión consolidada de ingresos, márgenes y concentración.
- Riesgos relevantes que amenazan continuidad o crecimiento.
- Oportunidades priorizadas con impacto económico y viabilidad.

## Preguntas típicas
- ¿Quiénes son los principales clientes y cómo evolucionan?
- ¿Dónde está la mayor exposición o dependencia?
- ¿Qué decisiones requieren atención inmediata?

## Indicadores de interés general
- Tendencia de ingresos y margen.
- Concentración de clientes y proveedores.
- Señales de riesgo y calidad de datos.""",
    "director-financiero.md": """# Expectativas de un Director Financiero

## Enfoque habitual
- Liquidez, flujo de caja y cumplimiento de obligaciones.
- Calidad del dato contable y reclasificaciones necesarias.
- Variaciones frente a presupuesto o forecast.

## Preguntas típicas
- ¿Cómo está la posición de caja?
- ¿Qué pasivos concentran mayor salida de recursos?
- ¿Hay cuentas mal clasificadas que distorsionan análisis?

## Indicadores de interés general
- Flujo de operación.
- Cuentas por cobrar y por pagar.
- Pasivos laborales e impuestos.""",
    "gerente-operaciones.md": """# Expectativas de un Gerente de Operaciones

## Enfoque habitual
- Cumplimiento de producción y abastecimiento.
- Inventarios, rotación y cuellos de botella.
- Calidad y continuidad de suministro.

## Preguntas típicas
- ¿Hay proveedores críticos con alta dependencia?
- ¿Cómo se comporta el inventario?
- ¿Qué señales operativas requieren acción?

## Indicadores de interés general
- Cumplimiento de plan de producción.
- Rotación de inventario.
- Incidencias de calidad y suministro.""",
    "indicadores-ejecutivos.md": """# Indicadores que suelen revisar los ejecutivos

## Comerciales
- Ingresos por canal o cliente.
- Concentración y recurrencia.
- Margen por producto o contraparte.

## Financieros
- Flujo de caja operativo.
- Liquidez y obligaciones de corto plazo.
- Variación presupuestal.

## Operativos
- Cumplimiento de producción.
- Inventario y rotación.
- Calidad y cumplimiento regulatorio.

## De datos
- Completitud de maestros.
- Consistencia de clasificación.
- Trazabilidad de evidencia.""",
}

SCENARIOS = [
    ("analisis-clientes", "Análisis de clientes", "Evaluar desempeño, concentración y señales de clientes comerciales.", ["¿Quiénes son los principales clientes?", "¿Hay concentración?", "¿Cuál cliente es estratégico?"], ["cliente", "ranking", "concentración", "perfil de entidad"]),
    ("analisis-proveedores", "Análisis de proveedores", "Evaluar abastecimiento, dependencia y comportamiento de proveedores reales.", ["¿Quiénes son los principales proveedores?", "¿Hay dependencia crítica?"], ["proveedor", "cuentas por pagar", "riesgo"]),
    ("analisis-financiero", "Análisis financiero", "Revisar ingresos, costos, gastos y margen con segregación adecuada.", ["¿Cómo evolucionan los ingresos?", "¿Cuál es el margen?"], ["ingreso", "costo", "gasto", "margen"]),
    ("concentracion", "Concentración", "Identificar dependencia de pocas entidades o rubros.", ["¿En qué se concentra la actividad?", "¿Es riesgo o normalidad?"], ["concentración", "riesgo", "cliente", "proveedor"]),
    ("estacionalidad", "Estacionalidad", "Detectar variaciones recurrentes por periodo.", ["¿Hay patrones estacionales?", "¿Qué meses concentran actividad?"], ["estacionalidad", "KPIs", "ingreso"]),
    ("liquidez", "Liquidez", "Evaluar capacidad de cumplir obligaciones de corto plazo.", ["¿Cómo está la liquidez?", "¿Qué sale de caja pronto?"], ["liquidez", "flujo de efectivo", "banco"]),
    ("produccion", "Producción", "Analizar cumplimiento y eficiencia de manufactura.", ["¿Se cumple el plan?", "¿Hay cuellos de botella?"], ["producción", "inventario", "calidad"]),
    ("compras", "Compras", "Revisar órdenes, proveedores y compromisos de pago.", ["¿Qué se compra más?", "¿A quién se le debe más?"], ["orden de compra", "proveedor", "cuentas por pagar"]),
    ("cobranza", "Cobranza", "Gestionar recuperación de cartera de clientes.", ["¿Qué clientes deben más?", "¿Qué facturas están vencidas?"], ["cobranza", "cuentas por cobrar", "cliente"]),
    ("inventario", "Inventario", "Controlar existencias, rotación y obsolescencia.", ["¿Qué inventario está detenido?", "¿Cuál es la rotación?"], ["inventario", "producto", "costo"]),
    ("calidad-y-cumplimiento", "Calidad y cumplimiento", "Revisar conformidad de producto y procesos regulados.", ["¿Hay no conformidades?", "¿Qué lotes están en revisión?"], ["calidad", "compliance", "riesgo"]),
    ("nomina-y-personal", "Nómina y personal", "Analizar pasivos laborales sin confundirlos con proveedores.", ["¿Qué obligaciones laborales existen?", "¿Por qué aparece nómina en proveedores?"], ["nómina", "pasivo", "cuenta contable"]),
    ("impuestos", "Impuestos", "Revisar obligaciones fiscales y su efecto en caja.", ["¿Qué impuestos están por pagar?"], ["impuesto", "pasivo", "flujo de efectivo"]),
    ("clasificacion-entidades", "Clasificación de entidades", "Distinguir clientes, proveedores y cuentas contables.", ["¿Por qué esta entidad no es proveedor?", "¿Cómo se clasifica?"], ["entidad canónica", "ontología", "cuenta contable"]),
    ("rankings-empresariales", "Rankings empresariales", "Ordenar entidades por criterio declarado con exclusiones.", ["¿Cómo se calcula el ranking?", "¿Qué se excluye?"], ["ranking", "reglas de exclusión"]),
    ("riesgos-empresariales", "Riesgos empresariales", "Identificar exposiciones con evidencia.", ["¿Cuáles son los principales riesgos?"], ["riesgo", "concentración", "calidad de datos"]),
    ("oportunidades-comerciales", "Oportunidades comerciales", "Detectar potencial de crecimiento o mejora.", ["¿Dónde hay oportunidad?"], ["oportunidad", "cliente estratégico", "margen"]),
    ("presupuesto-vs-real", "Presupuesto versus real", "Comparar desempeño contra plan financiero.", ["¿Dónde hay desviación?"], ["presupuesto", "forecast", "KPIs"]),
    ("tesoreria", "Tesorería", "Coordinar cobros, pagos y posición bancaria.", ["¿Cuál es la posición de caja?"], ["banco", "conciliación bancaria", "flujo de efectivo"]),
    ("auditoria-de-datos", "Auditoría de datos", "Detectar inconsistencias maestras antes de decidir.", ["¿Los datos son confiables?", "¿Hay cuentas mal ubicadas?"], ["calidad de datos", "entidad canónica", "reglas"]),
]

EXAMPLES = {
    "publico-en-general.md": """# Ejemplo: PUBLICO EN GENERAL

## Datos observados en el dataset
- Código: `C0003`
- Nombre: **PUBLICO EN GENERAL**
- Clasificación documentada: concepto interno o puente / cliente genérico

## Por qué aparece
En muchos ERP, cuando no se identifica al comprador final en una transacción masiva, se usa un cliente genérico de facturación.

## Implicación analítica
No debe tratarse igual que un cliente comercial nominal en rankings sin contexto. Suele concentrar volumen alto de movimientos.

## Naturaleza recomendada
Cliente genérico o bucket especial, no cuenta contable.""",
    "nueva-walmart.md": """# Ejemplo: NUEVA WALMART DE MEXICO

## Datos observados en el dataset
- Código comercial: `C0027`
- Variantes de nombre: **NUEVA WAL MART DE MEXICO**, **NUEVA WALMART DE MEXICO S DE RL DE CV**
- RFC asociado en catálogo: `NWM9709244` (variantes documentadas)

## Por qué es cliente comercial
Presenta patrón de código cliente (`C####`) y comportamiento de contraparte comercial en el catálogo de entidades.

## Implicación analítica
Los alias deben resolverse a una entidad canónica antes de rankear o evaluar riesgo.

## Naturaleza recomendada
Cliente comercial / empresa.""",
    "costco-de-mexico.md": """# Ejemplo: COSTCO DE MEXICO

## Datos observados en el dataset
- Código: `C0026`
- Nombre: **COSTCO DE MEXICO**
- Variante legal: **COSTCO DE MEXICO SA DE CV** (`CME910715U`)

## Por qué es cliente comercial
Código con prefijo de cliente comercial y presencia en dimensiones de cliente del datamart.

## Implicación analítica
Útil para ejemplos de ranking comercial y análisis de concentración.

## Naturaleza recomendada
Cliente comercial.""",
    "nomina-por-pagar.md": """# Ejemplo: NOMINA POR PAGAR

## Datos observados en el dataset
- Código: `20401001`
- Nombres observados: **20401001 NOMINA POR PAGAR**, **PASIVO NOMINA POR PAGAR**
- Aparece documentado en dimensiones de proveedor y en cuentas contables

## Por qué NO es proveedor comercial
Representa un pasivo laboral, no un tercero de suministro. Su alta actividad en campo proveedor es un caso típico de misclasificación.

## Implicación analítica
Debe excluirse de rankings de proveedores y analizarse en contexto de nómina y tesorería.

## Naturaleza recomendada
Pasivo laboral / cuenta contable.""",
    "proveedores-nacionales.md": """# Ejemplo: PROVEEDORES NACIONALES

## Datos observados en el dataset
- Código: `20101001`
- Nombre: **PROVEEDORES NACIONALES TASA 16%**

## Por qué es cuenta contable
Es un rubro del catálogo contable de proveedores agregado, no un proveedor individual identificable.

## Implicación analítica
No debe confundirse con un proveedor operativo en análisis de abastecimiento.

## Naturaleza recomendada
Cuenta contable.""",
    "genomma-laboratories.md": """# Ejemplo: GENOMMA LABORATORIES MEXICO

## Datos observados en el dataset
- Código: `C0004`
- Nombre: **GENOMMA LABORATORIES MEXICO**

## Por qué es cliente comercial
Código de cliente comercial en catálogo con comportamiento de contraparte de venta.

## Implicación analítica
Ejemplo de cliente nominal en sector farmacéutico/comercial sin asumir políticas internas.

## Naturaleza recomendada
Cliente comercial.""",
    "clasificacion-resumen.md": """# Resumen: clientes, proveedores y cuentas contables

## Clientes comerciales (ejemplos reales)
- PUBLICO EN GENERAL (`C0003`) — genérico
- NUEVA WALMART DE MEXICO (`C0027`)
- COSTCO DE MEXICO (`C0026`)
- GENOMMA LABORATORIES MEXICO (`C0004`)

## Cuentas contables (ejemplos reales)
- NOMINA POR PAGAR (`20401001`)
- PROVEEDORES NACIONALES TASA 16% (`20101001`)

## Regla práctica
Antes de rankear o recomendar, validar: ¿existe tercero real?, ¿el código es comercial o contable?, ¿el nombre sugiere pasivo, impuesto o nómina?""",
}


def build_glossary() -> str:
    lines = ["# Glosario ejecutivo", "", "Lenguaje sencillo para usuarios de negocio.", ""]
    for i, (term, definition) in enumerate(GLOSSARY_TERMS, 1):
        lines.append(f"## {i}. {term}")
        lines.append(definition)
        lines.append("")
    return "\n".join(lines)


def build_faq() -> str:
    lines = ["# Preguntas frecuentes", "", "Respuestas neutrales y genéricas.", ""]
    for q, a in FAQ_ITEMS:
        lines.append(f"## {q}")
        lines.append(a)
        lines.append("")
    return "\n".join(lines)


def build_scenario(slug: str, title: str, objective: str, questions: list[str], knowledge: list[str]) -> str:
    lines = [f"# {title}", "", "## Objetivo", objective, "", "## Preguntas frecuentes"]
    for q in questions:
        lines.append(f"- {q}")
    lines.extend(["", "## Conocimiento requerido"])
    for k in knowledge:
        lines.append(f"- {k}")
    return "\n".join(lines)


def main() -> None:
    for slug, content in CONCEPTS.items():
        write(f"concepts/{slug}.md", content)

    write("glossary/glosario-ejecutivo.md", build_glossary())
    write("faq/preguntas-frecuentes.md", build_faq())

    for slug, title, body in RULES:
        write(
            f"rules/{slug}.md",
            f"# {title}\n\n## Regla\n{body}\n\n## Aplicación\nDirectriz genérica sustituible por política oficial de la empresa.",
        )

    for filename, content in EXECUTIVE.items():
        write(f"executive/{filename}", content)

    for item in SCENARIOS:
        write(f"scenarios/{item[0]}.md", build_scenario(*item))

    for filename, content in EXAMPLES.items():
        write(f"examples/{filename}", content)

    print("Knowledge pack generated.")


if __name__ == "__main__":
    main()
