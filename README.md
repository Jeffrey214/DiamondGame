# DiamondGame

DiamondGame je aplikace v Pythonu založená na Tkinteru, kde hráči navigují dynamickou deskou plnou zdí a diamantů. Vyberte si z několika herních režimů a vyzvěte sami sebe, abyste nasbírali diamanty na nejkratší cestě od Startu do Cíle!

## Funkce

### Herní režimy
- **Volný režim:**  
  Automaticky najde nejkratší cestu od Startu do Cíle. Mezi všemi cestami stejné délky vybere trasu, která nasbírá nejvíce diamantů.
- **Všechny režim:**  
  Vypočítá minimální počet kroků potřebných k nasbírání *všech* diamantů na desce před dokončením.
- **Cíl režim:**  
  Umožňuje hráčům zadat přesný počet diamantů, které chtějí nasbírat. Hra vypočítá nejkratší trasu, která nasbírá přesně tento počet diamantů.

### Dynamické generování desky
- Zvýšená hustota zdí pro větší výzvu, přičemž je zajištěna platná cesta od Startu do Cíle a dosažitelnost všech diamantů.
- Náhodné umístění zdí a diamantů zaručuje jedinečný zážitek při každé hře.

### Grafická vylepšení
- Vlastní grafika pro zdi, diamanty a hráče integrovaná pomocí Pillow.
- Buňky Start a Cíl jsou jasně zvýrazněny a označeny („Start“ a „Konec“).
- Animovaný pohyb hráče ukazuje vypočítanou cestu a postup sbírání diamantů.

### Vylepšení uživatelského rozhraní
- Intuitivní GUI založené na Tkinteru s jasně označenými tlačítky a stavovými zprávami.
- Možnosti výběru herních režimů a nastavení cílového počtu diamantů v režimu Cíl.
- Tlačítko Start je po jednom použití na desce deaktivováno, aby se zabránilo opakovanému spuštění, s vyhrazeným tlačítkem Reset pro generování nové desky.

### Balení do spustitelného souboru
- Lze zabalit jako samostatný spustitelný soubor pro Windows (`DiamondGame.exe`) pomocí PyInstaller.
- Podpora vlastních ikon: konečný spustitelný soubor zobrazuje ikonu s diamantovým motivem.
- Po spuštění se nezobrazuje žádné příkazové okno – pouze GUI Tkinter.

## Opravy chyb a vylepšení
- **Opravy trasování:**  
  - Vyřešeny problémy, kdy cesta v režimu Všechny zbytečně couvala.
  - Zajištěno, že v režimu Cíl hra nasbírá přesně zadaný počet diamantů.
  - Tlačítko Start je znovu povoleno, pokud nebyla nalezena žádná platná cesta, aby uživatelé mohli zkusit znovu bez resetování desky.
- **Robustní validace desky:**  
  - Vylepšeno generování desky tak, aby bylo zaručeno, že každý diamant je dosažitelný a buňka Cíl zůstává přístupná, čímž se zabrání slepým uličkám.

## Budoucí plány
- Prozkoumat další velikosti desek a nastavení obtížnosti.
- Implementovat přizpůsobitelné motivy a další grafické možnosti.
- Zlepšit efektivitu hledání cest pro větší nebo složitější desky.
