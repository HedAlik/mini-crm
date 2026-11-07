# Evidencia: pruebas automatizadas

```
$ python -m pytest -v
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.1.1, pluggy-1.7.0 -- mini-crm\.venv\Scripts\python.exe
rootdir: mini-crm
collecting ... collected 18 items

tests/test_api.py::test_flujo_completo_cliente_solicitud_y_cambio_de_estado PASSED [  5%]
tests/test_api.py::test_listar_clientes_y_filtrar_solicitudes_por_estado PASSED [ 11%]
tests/test_api.py::test_rechaza_solicitud_con_cliente_inexistente PASSED [ 16%]
tests/test_api.py::test_rechaza_estado_invalido_al_actualizar PASSED     [ 22%]
tests/test_api.py::test_rechaza_estado_invalido_al_crear PASSED          [ 27%]
tests/test_api.py::test_actualizar_solicitud_inexistente_devuelve_404 PASSED [ 33%]
tests/test_api.py::test_email_duplicado_devuelve_409 PASSED              [ 38%]
tests/test_api.py::test_cliente_con_datos_invalidos_devuelve_422[body0] PASSED [ 44%]
tests/test_api.py::test_cliente_con_datos_invalidos_devuelve_422[body1] PASSED [ 50%]
tests/test_api.py::test_cliente_con_datos_invalidos_devuelve_422[body2] PASSED [ 55%]
tests/test_api.py::test_cuerpo_no_json_devuelve_400 PASSED               [ 61%]
tests/test_api.py::test_cliente_id_booleano_es_rechazado PASSED          [ 66%]
tests/test_api.py::test_ids_fuera_de_rango_no_provocan_error_500[get-/solicitudes?cliente_id=%C2%B2-None-422] PASSED [ 72%]
tests/test_api.py::test_ids_fuera_de_rango_no_provocan_error_500[get-/solicitudes?cliente_id=9223372036854775808-None-422] PASSED [ 77%]
tests/test_api.py::test_ids_fuera_de_rango_no_provocan_error_500[post-/solicitudes-body2-422] PASSED [ 83%]
tests/test_api.py::test_ids_fuera_de_rango_no_provocan_error_500[patch-/solicitudes/9223372036854775808/estado-body3-404] PASSED [ 88%]
tests/test_api.py::test_seed_es_idempotente PASSED                       [ 94%]
tests/test_api.py::test_la_base_de_datos_tambien_impone_las_restricciones PASSED [100%]

============================= 18 passed in 1.17s ==============================
```
