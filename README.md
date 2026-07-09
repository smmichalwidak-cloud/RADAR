# 📡 RADAR — radar treści do newslettera hotelarskiego

**RADAR automatycznie skanuje branżowe RSS-y (PL / DE / świat), punktuje artykuły
pod kątem marketingu hotelarskiego i generuje gotowy digest w Markdown — trzy razy
w tygodniu, bez ręcznego przeglądania dziesiątek stron.** Napędzany przez GitHub
Actions, opcjonalnie wspierany przez Claude AI przy typowaniu tematów.

## Co robi

- 🔎 **Zbiera** wpisy z feedów RSS zdefiniowanych w `feeds.yml` (do 40 na feed)
- 🎯 **Filtruje** — pomija już widziane wpisy (`seen.json`) i starsze niż 4 dni
- 🏆 **Punktuje** trafność wg ważonych słów kluczowych z `keywords.yml`
- 🗂️ **Grupuje** wyniki po kategoriach, na górze najwyżej punktowane
- 📝 **Generuje** `digest/RRRR-MM-DD.md` gotowy do przejrzenia w „piątkowym rytuale”
- 🤖 **(Opcjonalnie)** proponuje do 5 tematów artykułów przez Claude, jeśli ustawisz `ANTHROPIC_API_KEY`

## Jak to działa

```
feeds.yml + keywords.yml  ─▶  radar.py  ─▶  digest/RRRR-MM-DD.md
         (co poniedziałek / środę / piątek 06:00 UTC, przez GitHub Actions)
```

## Uruchomienie

1. Zrób **fork** lub sklonuj to repo.
2. Dostosuj **`feeds.yml`** (źródła RSS) i **`keywords.yml`** (słowa kluczowe + wagi 1–5).
3. GitHub Actions uruchamia `radar.py` automatycznie w **pon / śr / pt o 06:00 UTC**
   (możesz też odpalić ręcznie: zakładka *Actions* → *RADAR biuletynu* → *Run workflow*).
4. Digest ląduje w folderze **`digest/`**.

### Podpowiedzi tematów od Claude (opcjonalnie)

Dodaj sekret repozytorium `ANTHROPIC_API_KEY`
(*Settings → Secrets and variables → Actions → New repository secret*). Bez klucza
RADAR działa normalnie — po prostu bez sekcji „Propozycje tematów”.

## Konfiguracja

| Plik | Rola |
|------|------|
| `feeds.yml` | Źródła RSS pogrupowane po kategoriach (PL / świat / DE / marketing) |
| `keywords.yml` | Słowa kluczowe z wagami 1–5 do scoringu trafności |
| `seen.json` | Rejestr przetworzonych wpisów (retencja 60 dni) — tworzony automatycznie |

## Lokalne uruchomienie

```bash
pip install feedparser pyyaml
python radar.py
```

## Licencja

MIT — patrz [LICENSE](LICENSE).
