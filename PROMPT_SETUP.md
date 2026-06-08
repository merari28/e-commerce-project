# Prompt reutilizable — Levantar proyecto + datos/imágenes demo + E2E screenshots + resumen

Copiá y pegá el bloque de abajo estando **dentro del directorio del proyecto** que quieras inicializar.
Está redactado para adaptarse al stack que se encuentre (no asume Django).

---

```
Inicializá y dejá funcionando este proyecto de punta a punta, con datos e imágenes demo reales,
pruebas E2E con capturas para portfolio, y un resumen final. Seguí EXACTAMENTE estos pasos:

1) DETECCIÓN E INICIALIZACIÓN
   - Explorá el repo y detectá el stack (framework, lenguaje, gestor de paquetes, base de datos,
     cómo se levanta el server). No asumas tecnología: adaptate a lo que haya.
   - Creá el entorno aislado (venv / node_modules / etc.) e instalá TODAS las dependencias.
   - Si algo no compila o falla en mi versión de runtime, resolvelo o reportá el bloqueo con el error.

2) BASE DE DATOS (NO DESTRUCTIVO)
   - Si la config apunta a una DB remota/productiva (RDS, etc.), NO la toques ni borres credenciales.
   - Hacela conmutable por variable de entorno y usá una DB LOCAL autocontenida para el demo
     (SQLite o equivalente). Corré migraciones.

3) DATOS DEMO (RELLENAR TODO)
   - Si hay fixtures/seeds, cargalos. Si no, generá datos demo realistas y coherentes con el dominio
     del proyecto (usuarios, entidades principales, transacciones/pedidos/pagos, etc.).
   - Dejá credenciales de acceso conocidas y documentadas (usuario normal + admin), todas activas.

4) IMÁGENES Y BRANDING REALES (CERO IMÁGENES ROTAS)
   - Reemplazá placeholders por imágenes REALES y relevantes al dominio (no flyers genéricos).
     Usá fuentes confiables (p. ej. DummyJSON para productos, randomuser.me para fotos de perfil,
     Unsplash para casos puntuales) y VERIFICÁ visualmente que cada imagen corresponde.
   - Respetá los nombres/paths exactos que la BD/plantillas referencian para que todo renderice.
   - Agregá fotos de perfil a los usuarios, imágenes de galería donde aplique, y generá un LOGO
     de marca limpio y montalo en la navegación.
   - Revisá TODAS las plantillas en busca de <img>/src que puedan quedar rotos y cubrí los fallbacks
     (íconos vacíos, estados "sin datos", etc.).

5) LEVANTAR EN UN PUERTO LIBRE
   - Buscá un puerto libre y levantá el server ahí (en background). Confirmá con health-check (HTTP 200)
     en las rutas clave. Dejámelo corriendo y decime la URL exacta.

6) PRUEBAS E2E + CAPTURAS PARA PORTFOLIO
   - Creá una carpeta dedicada (p. ej. e2e_portfolio/) con un script de Playwright que recorra
     TODAS las pantallas de la app (públicas, autenticadas y panel admin), ejecutando los flujos reales
     (login, alta a carrito/entidad, checkout/transacción, confirmación, etc.).
   - Guardá una captura full-page por pantalla, en alta resolución (viewport ~1440px, device_scale_factor=2),
     numeradas y con nombres descriptivos, dentro de e2e_portfolio/screenshots/.
   - Escribí un README en esa carpeta con el índice de pantallas, credenciales demo y cómo reproducirlo.

7) CORREGÍ BUGS QUE BLOQUEEN EL DEMO
   - Si en el camino encontrás errores (500, formularios rotos, textos/labels equivocados,
     inputs no responsive/asimétricos), corregilos y dejá constancia de cada fix.

8) CORREOS (SI APLICA)
   - Si el proyecto manda emails, verificá la conectividad SMTP y enviá los correos demo reales
     (bienvenida, confirmación de orden, etc.). Confirmá el envío sin errores.

9) RESUMEN FINAL
   - Dame un resumen claro de: qué instalaste, URL del server, credenciales, qué datos/imágenes cargaste,
     bugs corregidos, y la lista de capturas generadas.
   - Incluí además un párrafo breve estilo portfolio describiendo el proyecto, el stack tecnológico
     y el despliegue en la nube (basado en lo que esté realmente en el repo; marcá lo que no puedas verificar).
   - Recomendame las 4-5 capturas con más impacto visual para el portfolio.

REGLAS:
- Usá un task list para trackear el progreso.
- Trabajá de forma autónoma; solo preguntame si hay una decisión irreversible o ambigua que no puedas inferir.
- Todo lo que generes (scripts, imágenes, capturas) debe quedar versionado/reutilizable en el repo.
- No expongas ni subas secretos; si encontrás credenciales hardcodeadas, avisame.
```

---

## Tips de uso

- Pegalo tal cual estando dentro del directorio del proyecto.
- Para que los correos demo vayan a una dirección específica, agregá al final:
  `Enviá los correos demo a tu@email.com.`
- Para forzar un stack o puerto concreto, agregalo (ej.: `Usá el puerto 9000`).
- Si el proyecto es grande y querés máxima exhaustividad, antepoé la palabra **`ultracode`**
  para que orqueste el trabajo con múltiples agentes en paralelo.

## Referencia: cómo se resolvió en este proyecto (e-commerce Django)

- **DB conmutable** por `USE_SQLITE=1` sin tocar la config de AWS RDS.
- **Datos demo** desde `data.json` + passwords conocidas (`Demo12345!`).
- **Imágenes reales** vía `scripts/add_real_media.py` (DummyJSON + Unsplash + randomuser.me) y logo generado.
- **Capturas** en `e2e_portfolio/screenshots/` con `e2e_portfolio/capture_screens.py` (Playwright).
- **Correos** verificados/enviados con `scripts/send_demo_emails.py`.
