# RADAR — instrukcja uruchomienia (krok po kroku)

**Co budujemy:** automat, który w poniedziałki, środy i piątki o poranku sam przegląda kilkanaście źródeł branżowych (PL, świat, DE), odsiewa nowości, punktuje je pod kątem biuletynu i zapisuje gotowy plik przeglądowy (digest). Opcjonalnie Claude API dorzuca do każdego digestu 5 propozycji tematów.

**Po czym poznasz, że skończyliśmy:** w Twoim repozytorium na GitHubie, w folderze `digest/`, sam z siebie pojawia się plik z dzisiejszą datą i listą materiałów.

**Koszt:** 0 zł (GitHub Actions w publicznym/prywatnym repo hobbystycznym wystarcza z ogromnym zapasem). Selekcja Claude: grosze za uruchomienie, opcjonalna.

---

## KROK 1 — konto i nowe repozytorium

**Co:** zaloguj się na github.com (masz konto z prac nad dashboardem; jeśli nie — załóż). Kliknij zielony przycisk **New** (lub plus w prawym górnym rogu → New repository). Nazwa: `radar-biuletyn`. Zaznacz **Private**. Kliknij **Create repository**.
**Sukces:** widzisz pustą stronę repozytorium z napisem „Quick setup".

## KROK 2 — wgranie plików

**Co:** rozpakuj paczkę `radar.zip` u siebie. Na stronie repozytorium kliknij **uploading an existing file** (link w sekcji Quick setup). Przeciągnij WSZYSTKO z rozpakowanego folderu: `radar.py`, `feeds.yml`, `keywords.yml`, `PIATEK_PROMPT.md`, `README_SETUP.md` **oraz folder `.github`** (uwaga: to folder ukryty — jeśli przeciąganie go nie łapie, patrz „Plan B" niżej). Na dole kliknij **Commit changes**.
**Sukces:** na głównej stronie repo widzisz listę plików, w tym folder `.github`.

**Plan B (gdy `.github` nie chce się wgrać):** w repo kliknij **Add file → Create new file**, w polu nazwy wpisz dokładnie `.github/workflows/radar.yml` (ukośniki tworzą foldery), wklej zawartość pliku `radar.yml` z paczki, **Commit changes**.

## KROK 3 — pierwsze uruchomienie ręczne

**Co:** zakładka **Actions** (górne menu repo) → po lewej „RADAR biuletynu" → przycisk **Run workflow** → zielony **Run workflow**.
**Sukces:** po 1–2 minutach obok uruchomienia pojawia się zielony haczyk, a na głównej stronie repo jest nowy folder `digest/` z plikiem `RRRR-MM-DD.md`. Otwórz go — to Twój pierwszy digest.

## KROK 4 — przegląd martwych feedów (jednorazowo)

**Co:** w pierwszym digeście zjedź na sam dół do sekcji „⚠ Feedy do sprawdzenia". Adresy feedów zgadywałem wg standardu WordPressa — część oznaczona `[SPRAWDŹ]` może nie działać. Dla każdego martwego: wejdź na stronę serwisu, poszukaj ikony RSS lub dopisz `/feed/` do adresu, popraw linijkę w `feeds.yml` (ołówek ✏ przy pliku na GitHubie → edycja → Commit). Nie znajdziesz feedu — usuń linijkę albo wrzuć problem do mnie.
**Sukces:** po kolejnym ręcznym uruchomieniu (Krok 3) sekcja „Feedy do sprawdzenia" jest pusta lub prawie pusta.

## KROK 5 (OPCJONALNY) — selekcja tematów przez Claude

**Co:** w repo: **Settings → Secrets and variables → Actions → New repository secret**. Nazwa: `ANTHROPIC_API_KEY`, wartość: Twój klucz API z console.anthropic.com (Settings → API Keys → Create Key).
**Sukces:** w następnym digeście pojawia się sekcja „🎯 Propozycje tematów (selekcja Claude)".
**Bez tego kroku:** wszystko działa, po prostu digest nie ma sekcji propozycji — selekcję robimy razem w piątek.

## KROK 6 — powiadomienia (żeby nie zaglądać do repo)

**Co:** na stronie repo kliknij **Watch → Custom → zaznacz nic poza domyślnym** — GitHub i tak wyśle mail przy nieudanym workflow. Prościej: dodaj sobie przypomnienie w kalendarzu na piątek rano „RADAR → artykuł". Digesty zawsze czekają w folderze `digest/`.
**Sukces:** masz piątkowy rytuał w kalendarzu.

---

## Rytuał piątkowy (10 minut Twojej pracy)

1. Otwórz w repo 2–3 najnowsze pliki z `digest/` (pon+śr+pt bieżącego tygodnia).
2. Skopiuj ich treść (przycisk „Copy raw file" przy każdym pliku).
3. Wklej do rozmowy ze mną razem z promptem z pliku `PIATEK_PROMPT.md`.
4. Dostajesz: wybrany temat + gotowy artykuł/sekcję wydania do akceptacji.

## Konserwacja (raz na kwartał, 10 minut)

- `feeds.yml` — dopisz nowe źródła, usuń te, które nic nie wnoszą.
- `keywords.yml` — dostrój wagi: jeśli w „🔥 Najtrafniejsze" trafiają śmieci, obniż wagę winnego słowa; jeśli dobre rzeczy lądują nisko — podbij.
- Zerknij na zużycie Actions (Settings → Billing) — przy tym harmonogramie nie zbliżysz się do limitu darmowego.

## ⚠ Zastrzeżenia

1. Adresy feedów z `[SPRAWDŹ]` wymagają weryfikacji po pierwszym uruchomieniu (Krok 4) — to jedyny element „na wiarę" w tej paczce.
2. Godzina 06:00 UTC to 08:00 czasu PL latem i 07:00 zimą; GitHub potrafi opóźnić harmonogram o kilkanaście minut — to normalne.
3. Digest zbiera treści cudze jako LINKI z krótkimi zajawkami do Twojego użytku redakcyjnego — do biuletynu zawsze piszemy własny tekst, nigdy nie przeklejamy treści źródeł.
