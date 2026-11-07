# Evidencia de ejecución (curl contra el servidor real)

```
$ curl -s http://127.0.0.1:8000/health
{"status":"ok"}


$ curl -s -i -X POST http://127.0.0.1:8000/clientes -H 'Content-Type: application/json' -d '{"nombre":"Ana Prueba","email":"ana@example.com"}'
HTTP/1.1 201 CREATED
Content-Type: application/json

{"id":1,"nombre":"Ana Prueba","email":"ana@example.com","creado_en":"2026-11-07 00:29:40"}


$ curl -s -i -X POST http://127.0.0.1:8000/clientes -H 'Content-Type: application/json' -d '{"nombre":"Otra","email":"ana@example.com"}'
HTTP/1.1 409 CONFLICT
Content-Type: application/json

{"error":"Ya existe un cliente con ese email"}


$ curl -s http://127.0.0.1:8000/clientes
[{"id":1,"nombre":"Ana Prueba","email":"ana@example.com","creado_en":"2026-11-07 00:29:40"}]


$ curl -s -i -X POST http://127.0.0.1:8000/solicitudes -H 'Content-Type: application/json' -d '{"cliente_id":1,"descripcion":"No llega mi factura"}'
HTTP/1.1 201 CREATED
Content-Type: application/json

{"id":1,"cliente_id":1,"descripcion":"No llega mi factura","estado":"pendiente","creado_en":"2026-11-07 00:29:40","actualizado_en":"2026-11-07 00:29:40"}


$ curl -s -i -X POST http://127.0.0.1:8000/solicitudes -H 'Content-Type: application/json' -d '{"cliente_id":999,"descripcion":"Cliente inexistente"}'
HTTP/1.1 422 UNPROCESSABLE ENTITY
Content-Type: application/json

{"error":"Datos inválidos","detalles":{"cliente_id":"el cliente no existe"}}


$ curl -s -i -X PATCH http://127.0.0.1:8000/solicitudes/1/estado -H 'Content-Type: application/json' -d '{"estado":"en_proceso"}'
HTTP/1.1 200 OK
Content-Type: application/json

{"id":1,"cliente_id":1,"descripcion":"No llega mi factura","estado":"en_proceso","creado_en":"2026-11-07 00:29:40","actualizado_en":"2026-11-07 00:29:40"}


$ curl -s -i -X PATCH http://127.0.0.1:8000/solicitudes/1/estado -H 'Content-Type: application/json' -d '{"estado":"cerrada"}'
HTTP/1.1 422 UNPROCESSABLE ENTITY
Content-Type: application/json

{"error":"Datos inválidos","detalles":{"estado":"debe ser uno de: pendiente, en_proceso, resuelta"}}


$ curl -s -i -X PATCH http://127.0.0.1:8000/solicitudes/42/estado -H 'Content-Type: application/json' -d '{"estado":"resuelta"}'
HTTP/1.1 404 NOT FOUND
Content-Type: application/json

{"error":"Solicitud no encontrada"}


$ curl -s 'http://127.0.0.1:8000/solicitudes?estado=en_proceso'
[{"id":1,"cliente_id":1,"descripcion":"No llega mi factura","estado":"en_proceso","creado_en":"2026-11-07 00:29:40","actualizado_en":"2026-11-07 00:29:40","cliente_nombre":"Ana Prueba"}]


```
