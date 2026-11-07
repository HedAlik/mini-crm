# Evidencia: pruebas automatizadas

```
$ python -m pytest -v
============================= test session starts ==============================
platform linux -- Python 3.13.18, pytest-9.1.1, pluggy-1.6.0 -- /usr/local/bin/python3
rootdir: mini-crm
plugins: platformdirs-4.13.5, anyio-4.15.1
collecting ... collected 13 items

tests/test_api.py::test_flujo_completo_cliente_solicitud_y_cambio_de_estado PASSED [  7%]
tests/test_api.py::test_listar_clientes_y_filtrar_solicitudes_por_estado PASSED [ 15%]
tests/test_api.py::test_rechaza_solicitud_con_cliente_inexistente PASSED [ 23%]
tests/test_api.py::test_rechaza_estado_invalido_al_actualizar PASSED     [ 30%]
tests/test_api.py::test_rechaza_estado_invalido_al_crear PASSED          [ 38%]
tests/test_api.py::test_actualizar_solicitud_inexistente_devuelve_404 PASSED [ 46%]
tests/test_api.py::test_email_duplicado_devuelve_409 PASSED              [ 53%]
tests/test_api.py::test_cliente_con_datos_invalidos_devuelve_422[body0] PASSED [ 61%]
tests/test_api.py::test_cliente_con_datos_invalidos_devuelve_422[body1] PASSED [ 69%]
tests/test_api.py::test_cliente_con_datos_invalidos_devuelve_422[body2] PASSED [ 76%]
tests/test_api.py::test_cuerpo_no_json_devuelve_400 PASSED               [ 84%]
tests/test_api.py::test_cliente_id_booleano_es_rechazado PASSED          [ 92%]
tests/test_api.py::test_la_base_de_datos_tambien_impone_las_restricciones PASSED [100%]

============================== 13 passed in 0.26s ==============================
```
