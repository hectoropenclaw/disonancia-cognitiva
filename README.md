# Disonancia Cognitiva

Blog personal y espacio de videos breves de Héctor. La idea editorial es poner convicciones, decisiones y sistemas frente a preguntas honestas, con temas de pensamiento, trabajo, tecnología y vida cotidiana.

## Publicación del blog

Los textos fuente viven en content/posts.json. Después de editarlos, ejecuta:

    python3 scripts/build_site.py

El resultado público se genera en docs/. GitHub Pages publica esa carpeta desde la rama main.

## Videos para Instagram

Los guiones y captions están en content/reels.json y social/instagram-launch-kit.md. Los Reels de lanzamiento son piezas verticales 1080 x 1920 con texto en pantalla, sin voz ni música. Para volver a renderizarlos:

    python3 scripts/render_reels.py

Los MP4 quedan en media/reels y el constructor los copia al sitio. Antes de publicar, abre cada archivo, confirma la cuenta propietaria y añade voz o música solo si Héctor lo decide.

## Instagram

Nombre sugerido: Disonancia Cognitiva. El usuario @disonanciacognitiva es solo una propuesta; su disponibilidad no está confirmada y el perfil aún requiere alta y verificación del titular. No se debe enlazar como cuenta activa hasta verificarlo.

## Hosting

El sitio usa GitHub Pages en un repositorio público para no requerir una contratación de hosting ni un dominio nuevo. El código del sitio y los textos publicados son públicos. La URL prevista es:

    https://hectoropenclaw.github.io/disonancia-cognitiva/

Si después Héctor paga por un dominio propio, se puede conectar sin rehacer el sitio.
