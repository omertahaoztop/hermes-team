# hermes-team

Telegram süper grubunda yaşayan kişisel yapay zekâ ajanlarından oluşan bir ekip;
[Hermes Agent](https://github.com/NousResearch/hermes-agent) üzerine kurulu. Her rol için bir
ajan, her ajan için bir konu, okumaya değer bir şey üreten tek bir zamanlanmış çalışma.

Temel fikir: ajan, uğradığın bir sohbet botu değildir. Kendi kimliği, talimatları, hafızası,
durumu ve zamanlaması olan bir **profil**dir — ve sana belli bir ritimde rapor verir.
Dokuz rol, dokuz konu; hafıza bankası dışında paylaşılan hiçbir şey yok.

```
                    Telegram süper grubu
  ┌──────────────────────────────────────────────────────┐
  │  General        ← buradan her ajanla yazışırsın      │
  │  ──────────────────────────────────────────────────  │
  │  Calendar  Task  Issue  Anchor  News  Scout  Mail …  │
  └──────────────────────────────────────────────────────┘
        ▲          ▲          ▲          ▲
        │          │          │          │
   ┌────┴───┐ ┌────┴───┐ ┌────┴───┐ ┌────┴───┐
   │ profil │ │ profil │ │ profil │ │ profil │   her biri: SOUL.md, SKILL.md,
   │takvim  │ │ görev  │ │ issue  │ │ haber  │   .env, state/, cron/, hafıza
   └────────┘ └────────┘ └────────┘ └────────┘
```

## Bu yapı neden

| Karar | Gerekçe |
|---|---|
| Ajan = profil, yeni bir ilkel değil | İzolasyon bedava gelir: ayrı token, skill, durum, hafıza, zamanlama |
| Her ajan için bir konu | Beş sabah raporu bir sohbeti gömer; konuyu açarsın ya da görmezden gelirsin |
| Varsayılan salt-okunur | Takipçine yazabilen ajan, denetlemek zorunda olduğun ajandır. Önerir, asla uygulamaz |
| Her çalışma bir mesaj üretir | Sessiz ajan, bozuk ajandan ayırt edilemez. [`[SILENT]` neden kaldırıldı](docs/output-contract.md) |
| Kanıt yoksa satır da yok | Her satır bir iş kimliği, bir bağlantı ya da `file:field` taşır. Kaynaksız cümle olmaz |
| Deterministik toplayıcılar | Model veriyi yorumlar, asla getirmez. Getirmek script'in işi |

## Dokuz rol

Genel roller — her biri kendi kaynaklarınla dolduracağın bir şablon. Hangisinin ne okuduğu ve
ne ürettiği için [docs/bot-roles.md](docs/bot-roles.md).

| # | Rol | Okur | Üretir |
|---|---|---|---|
| 1 | **Primary** | kendi notların, durum bildirimlerin | günlük check-in, haftalık desen |
| 2 | **Calendar** | ICS akışları | gün planı, çakışmalar, hazırlık |
| 3 | **Tasks** | görev takipçisi API'si | 4–6 bayat görev hatırlatması |
| 4 | **Issues** | issue takipçisi API'si | açık/gecikmiş kayıtlar + öneriler |
| 5 | **Anchor** | aktivite günlüğü, enerji | sabah çapası, akşam önerisi |
| 6 | **News** | RSS/Atom, HN | her biri gerekçelenmiş 4–6 sinyal |
| 7 | **Scout** | GitHub, paket indeksleri | dikkate değer 4–6 depo |
| 8 | **Mail** | IMAP/Gmail | ayrıştırılmış 5–8 öğe, asla göndermez |
| 9 | **Ops** | olay notları, runbook'lar | postmortem iskeleti, prod adımları |

## Hızlı başlangıç

```bash
git clone https://github.com/<you>/hermes-team && cd hermes-team
cp templates/SOUL.template.md   ~/.hermes/profiles/<role>/SOUL.md
cp templates/SKILL.template.md  ~/.hermes/profiles/<role>/skills/<role>/SKILL.md
install -m 755 bin/state.py ~/.hermes/scripts/state.py
```

Sonra tek bir rutin oluştur, duraklatılmış halde; ancak ilk çalışma kendini kanıtladıktan
sonra devreye al. Tüm sıra [docs/setup.md](docs/setup.md) içinde.

## İçinde ne var

| Yol | Ne |
|---|---|
| `docs/architecture.md` | Ajan başına profil neden, gateway nasıl bağlanıyor |
| `docs/bot-roles.md` | Dokuz rol: kaynaklar, çıktı biçimi, hata modu |
| `docs/output-contract.md` | Her ajanın `SOUL.md` dosyasına gömülen ortak sözleşme |
| `docs/state-management.md` | Durum yazımı için tek yardımcı, ve onu zorunlu kılan hata |
| `docs/setup.md` | BotFather → profil → soul → skill → rutin |
| `templates/` | `SOUL`, `SKILL`, ortak kurallar, rutin tablosu |
| `bin/state.py` | Ajan başına durum dosyaları için atomik okuma/yazma |
| `bin/deploy.sh` | `templates/` içeriğini `~/.hermes/profiles/` altına iter |

## Bu deponun kodladığı sert kurallar

- **Git'te sır yok.** Token'lar profilin `.env` dosyasında durur, asla burada.
- **Dış dünyaya hiçbir şey gönderilmez.** Mail yok, yorum yok, PR yok, takvime yazma yok.
  Yalnız okuma ve raporlama.
- **Bir rutin, bir çalışma kendini kanıtlayana kadar duraklatılmış kalır.** "Kuruldu" kanıt
  değildir; `cron/output/` kaydı ve gerçek bir mesaj kanıttır.
- **Kimsenin okumadığı ajanı sil.** Okunmayan ajan negatif değerdir.

## Lisans

MIT — bkz. [LICENSE](LICENSE).
