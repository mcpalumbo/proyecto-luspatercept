# Simulador económico: biosimilar de luspatercept

Proyecto del curso de Biofármacos (UNSAM, 2026): desarrollo y evaluación económica de un biosimilar de luspatercept (Reblozyl®, BMS) para el mercado de EE. UU.

Esta página permite cambiar los supuestos del proyecto (mercado, precio, producción, costos, programa clínico y fecha de lanzamiento) y ver al instante el flujo de fondos, el VAN, la TIR, la inversión máxima, el recupero y el cronograma. También resume el producto, el proceso de fabricación, las patentes y las fuentes.

**Ver online:** https://TU-USUARIO.github.io/NOMBRE-DEL-REPO/

## Uso

- Abrir `index.html` en el navegador: no requiere instalación. La primera vez necesita internet para descargar Pyodide, que permite correr Python en el navegador.
- Los botones cargan los dos escenarios del proyecto:
  - Escenario 2 · base: lanzamiento en 2036, VAN USD 33,1 M, TIR 14,9 %.
  - Escenario 1 · objetivo: lanzamiento en 2034, VAN USD 117,0 M, TIR 34,4 %.
- La dirección de la página guarda los cambios, así que copiándola se comparte un escenario.

## Archivos

| Archivo | Qué es |
|---|---|
| `index.html` | El simulador completo, en un único archivo. |
| `modelo.py` | El modelo en Python, para usarlo fuera del navegador (`python modelo.py`). |

## Alcance

Trabajo académico. Los supuestos son hipótesis de trabajo, no cotizaciones, y el análisis de patentes no reemplaza un estudio formal de libertad de operación.
