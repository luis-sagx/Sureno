# Metricas de calidad - SQAP Sureno

Generado automaticamente por `metricas/calcular_metricas.py` el 2026-07-23 20:45.

Norma aplicada: **ISO/IEC 25010** (modelo de calidad del producto). Las formulas toman su forma de **ISO/IEC 25023** (calidad del producto) y **ISO/IEC 25022** (calidad en uso), partes de la misma familia SQuaRE.

## 1. Resultados

| ID | Caracteristica ISO 25010 | Metrica | Formula | Sustitucion | Valor | Umbral | Estado |
|---|---|---|---|---|---|---|---|
| MC-01 | Adecuación funcional / Completitud funcional | Completitud funcional | `X = A / B` | `X = 10 / 10` | **100.00 %** | >= 100.00 % | CUMPLE |
| MC-02 | Adecuación funcional / Corrección funcional | Tasa de éxito de los casos de prueba | `X = A / B` | `X = 24 / 24` | **100.00 %** | >= 95.00 % | CUMPLE |
| MC-03 | Fiabilidad / Madurez | Densidad de fallos de la suite | `X = A / B` | `X = 0 / 231` | **0.00 %** | <= 5.00 % | CUMPLE |
| MC-04 | Fiabilidad / Madurez | Densidad de defectos abiertos | `X = D / KLOC` | `X = 0 / 1.142 KLOC` | **0.00 def/KLOC** | <= 1.00 def/KLOC | CUMPLE |
| MC-05 | Fiabilidad / Disponibilidad | Disponibilidad bajo carga | `X = (N - F) / N` | `X = (2996 - 0) / 2996` | **100.00 %** | >= 99.00 % | CUMPLE |
| MC-06 | Eficiencia de desempeño / Comportamiento temporal | Tiempo de respuesta p95 | `X = p95(t)` | `X = p95 = 200 ms` | **200 ms** | <= 800 ms | CUMPLE |
| MC-07 | Eficiencia de desempeño / Capacidad | Capacidad (rendimiento sostenido) | `X = N / T` | `X = 2996 / 120 s = 25.13 req/s` | **25.13 req/s** | >= 20.00 req/s | CUMPLE |
| MC-08 | Seguridad / Confidencialidad / Integridad | Vulnerabilidades críticas abiertas | `X = V_blocker + V_critical` | `X = 0 (BLOCKER+CRITICAL abiertas)` | **0** | == 0 | CUMPLE |
| MC-09 | Seguridad / Integridad | Índice de remediación de vulnerabilidades | `X = (V_antes - V_despues) / V_antes` | `X = (33 - 0) / 33` | **100.00 %** | >= 90.00 % | CUMPLE |
| MC-10 | Mantenibilidad / Capacidad de ser probado | Cobertura de código backend | `X = L_cubiertas / L_totales` | `X = 690 / 730 lineas` | **94.52 %** | >= 80.00 % | CUMPLE |
| MC-11 | Mantenibilidad / Capacidad de ser probado | Cobertura de código frontend | `X = L_cubiertas / L_totales` | `X = 210 / 210 lineas` | **100.00 %** | >= 80.00 % | CUMPLE |
| MC-12 | Mantenibilidad / Modularidad / Reusabilidad | Densidad de código duplicado | `X = L_duplicadas / L_totales` | `X = 60 / 4876 lineas` | **1.23 %** | <= 3.00 % | CUMPLE |
| MC-13 | Mantenibilidad / Analizabilidad / Modificabilidad | Reducción de deuda técnica (code smells) | `X = (S_antes - S_despues) / S_antes` | `X = (42 - 4) / 42` | **90.48 %** | >= 50.00 % | CUMPLE |
| MC-14 | Usabilidad / Accesibilidad | Barreras de accesibilidad abiertas | `X = sum(issues_a11y_abiertos)` | `X = 0 (ANTES: 52)` | **0** | == 0 | CUMPLE |
| MC-15 | Calidad en uso / Eficacia | Eficacia: tareas de usuario completadas | `X = A / B` | `X = 7 / 7 tareas E2E` | **100.00 %** | >= 95.00 % | CUMPLE |
| MC-16 | Calidad en uso / Eficiencia | Eficiencia: tiempo de la tarea de compra | `X = T_tarea` | `X = 7.7 s (recorrido completo de compra)` | **7.7 s** | <= 30.0 s | CUMPLE |

## 2. Trazabilidad requisito -> caso -> prueba automatizada

| CP | Titulo | Requisitos | Caracteristica ISO 25010 | Estado | Pruebas que lo implementan |
|---|---|---|---|---|---|
| CP-01 | Registro exitoso con datos validos | RF-01 | Adecuacion funcional / Completitud funcional | PASS | [pytest] passed: Tests/integracion/test_api.py::test_api_signup_crea_usuario |
| CP-02 | Registro rechazado con email duplicado | RF-01 | Adecuacion funcional / Correccion funcional | PASS | [pytest] passed: Tests/integracion/test_api.py::test_api_signup_email_duplicado |
| CP-03 | Registro rechazado con campos vacios | RF-01 | Adecuacion funcional / Correccion funcional | PASS | [pytest] passed: Tests/integracion/test_api_extra.py::test_api_signup_faltan_campos |
| CP-04 | Login exitoso con credenciales de cliente | RF-02 | Adecuacion funcional / Completitud funcional | PASS | [pytest] passed: Tests/integracion/test_api.py::test_api_login_exitoso<br>[playwright] passed: login exitoso con credenciales válidas redirige fuera de /login |
| CP-05 | Login rechazado con contrasena incorrecta | RF-02 | Seguridad / Autenticidad | PASS | [pytest] passed: Tests/integracion/test_api.py::test_api_login_password_incorrecta<br>[playwright] passed: login fallido muestra error inline sin redirigir |
| CP-06 | Login de administrador va al panel | RF-02 | Adecuacion funcional / Correccion funcional | PASS | [pytest] passed: Tests/integracion/test_casos_sqap.py::test_cp06_login_admin_redirige_al_panel |
| CP-07 | Cliente/anonimo NO accede al panel admin | RF-02, RNF-02 | Seguridad / Confidencialidad | PASS | [pytest] passed: Tests/integracion/test_api.py::test_api_admin_stats_sin_sesion_401<br>[pytest] passed: Tests/integracion/test_api.py::test_api_admin_stats_cliente_403<br>[playwright] passed: redirige panel administrativo al login sin sesión |
| CP-08 | Crear producto como administrador | RF-03 | Adecuacion funcional / Completitud funcional | PASS | [pytest] passed: Tests/integracion/test_api_extra.py::test_create_product_201 |
| CP-09 | Editar producto existente | RF-03 | Adecuacion funcional / Completitud funcional | PASS | [pytest] passed: Tests/integracion/test_api_extra.py::test_update_product_200 |
| CP-10 | Eliminar producto | RF-03 | Adecuacion funcional / Completitud funcional | PASS | [pytest] passed: Tests/integracion/test_api_extra.py::test_delete_product_200<br>[vitest] passed: bindDeleteDialog > deletes the row and closes the dialog on a successful response |
| CP-11 | Agregar producto al carrito | RF-04 | Adecuacion funcional / Completitud funcional | PASS | [pytest] passed: Tests/integracion/test_api.py::test_api_cart_guarda<br>[vitest] passed: bindAddToCartButtons > adds the product read from the dataset to the cart |
| CP-12 | Carrito rechaza cantidad cero | RF-04 | Adecuacion funcional / Correccion funcional | PASS | [pytest] passed: Tests/integracion/test_api.py::test_api_cart_cantidad_invalida_400 |
| CP-13 | Carrito rechaza cantidad negativa | RF-04 | Adecuacion funcional / Correccion funcional | PASS | [pytest] passed: Tests/integracion/test_casos_sqap.py::test_cp13_carrito_rechaza_cantidad_negativa |
| CP-14 | Checkout completo (E2E) con direccion | RF-05 | Adecuacion funcional / Completitud funcional | PASS | [pytest] passed: Tests/integracion/test_api_extra.py::test_order_create_exitoso_201<br>[playwright] passed: agregar producto al carrito y completar checkout |
| CP-15 | Checkout sin direccion de envio | RF-05 | Adecuacion funcional / Correccion funcional | PASS | [pytest] passed: Tests/integracion/test_api_extra.py::test_order_create_falta_campo_400 |
| CP-16 | Historial de pedidos del cliente | RF-06 | Seguridad / Confidencialidad | PASS | [pytest] passed: Tests/integracion/test_api.py::test_api_compras_autenticado_lista |
| CP-17 | Administrador visualiza los pedidos | RF-07 | Adecuacion funcional / Completitud funcional | PASS | [pytest] passed: Tests/integracion/test_api_extra.py::test_order_get_all_orders_admin_200 |
| CP-18 | Contrasena almacenada hasheada (bcrypt) | RNF-01 | Seguridad / Confidencialidad | PASS | [pytest] passed: Tests/unitarias/test_models.py::test_cp18_user_create_hashea_password |
| CP-19 | Acceso a compra/checkout sin sesion | RNF-02 | Seguridad / Confidencialidad | PASS | [pytest] passed: Tests/integracion/test_api.py::test_api_compras_sin_sesion_401<br>[playwright] passed: logout cierra la sesión y bloquea rutas protegidas |
| CP-20 | API /api/user sin sesion devuelve 401 | RNF-02 | Seguridad / Confidencialidad | PASS | [pytest] passed: Tests/integracion/test_casos_sqap.py::test_cp20_api_user_sin_sesion_401 |
| CP-21 | Registro rechaza email con formato invalido | RF-01 | Adecuacion funcional / Correccion funcional | PASS | [pytest] passed: Tests/integracion/test_api.py::test_cp21_api_signup_email_con_formato_invalido<br>[playwright] passed: rechaza un correo con formato inválido |
| CP-22 | Registro valida la identificacion (cedula o RUC) | RF-01 | Adecuacion funcional / Correccion funcional | PASS | [pytest] passed: Tests/integracion/test_api.py::test_cp22_api_signup_identificacion_con_formato_invalido<br>[pytest] passed: Tests/integracion/test_api.py::test_api_signup_con_ruc_valido_crea_usuario<br>[pytest] passed: Tests/unitarias/test_validators.py::test_identificacion_acepta_cedula_valida<br>[pytest] passed: Tests/unitarias/test_validators.py::test_identificacion_acepta_ruc_valido<br>[pytest] passed: Tests/unitarias/test_validators.py::test_identificacion_rechaza_formato_arbitrario<br>[playwright] passed: rechaza una cédula o RUC inválido |
| CP-23 | No se puede comprar con carrito vacio | RF-05 | Adecuacion funcional / Correccion funcional | PASS | [pytest] passed: Tests/integracion/test_api_extra.py::test_cp23_order_create_carrito_vacio_400 |
| CP-24 | El total no se puede manipular desde el cliente | RF-05, RNF-03 | Seguridad / Integridad | PASS | [pytest] passed: Tests/integracion/test_api.py::test_api_cart_ignora_precio_y_total_manipulados |

## 3. Veredicto

- Metricas que cumplen: **16/16**
- Casos de prueba PASS: **24/24**
- Pruebas automatizadas ejecutadas: backend 166, frontend 47, E2E 18

**Veredicto automatico: APTO** (criterios de salida del SQAP, seccion 5.2).
