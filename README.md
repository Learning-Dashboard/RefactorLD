# Refactor LD
Aquest repositori conté els arxius generats durant el Treball de Final de Grau (TFG). Inclou tant les mètriques desenvolupades com els tests associats, organitzats de manera estructurada per facilitar-ne la comprensió i reutilització.

**Estructura del repositori**

La carpeta _metrics_ conté les mètriques desenvolupades en format .properties i .query, a més dels arxius de les metriques existents que es mantenen. Aquesta carpeta s’organitza en quatre subcarpetes:
- **metrics_existing**: Agrupa les mètriques que ja existien prèviament.
- **metrics_integrated**: Inclou les mètriques noves incorporades durant el TFG.
- **metrics_modified**: Conté mètriques existents que han estat modificades i/o redefinides.
- **metrics_proposed**: Agrupa les mètriques proposades per a desenvolupaments futurs.

La carpeta _tests_ inclou els tests en Python realitzats per validar les mètriques. Aquesta carpeta està subdividida segons la naturalesa de les mètriques:
- **metrics_integrated**: Tests de les mètriques incorporades.
- **metrics_modified**: Tests corresponents a mètriques existents que han estat modificades i/o redefinides.
- **metrics_proposed**: Tests de mètriques proposades encara no implementades definitivament.

A més, s'inclouen tres fitxers en format .txt que recullen:
- **categories.txt**: inclou les categories de les mètriques i dels factors
- **factors.txt**: recull la informació detallada dels factors de qualitat, incloent-hi el seu nom, descripció, les mètriques que els componen i la categoria assignada.
- **strategic_indicator.txt**: proporciona la informació relativa als indicadors estratègics, especificant-ne el nom, la descripció i els factors de qualitat que els conformen.