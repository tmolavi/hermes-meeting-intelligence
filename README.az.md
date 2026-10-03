# Hermes İclas Zəkası (Hermes Meeting Intelligence)

> Hermes Agent üçün təkrar istifadə edilə bilən iclas zəkası bacarıqları, alətləri və daimi iclas yaddaşı.

<p align="center">
  <a href="README.md"><b>English</b></a> •
  <a href="README.fa.md"><b>فارسی</b></a> •
  <a href="README.tr.md"><b>Türkçe</b></a> •
  <a href="README.az.md"><b>Azərbaycan dili</b></a> •
  <a href="README.ar.md"><b>العربية</b></a>
</p>

<p align="center">
  <a href="https://github.com/tmolavi/hermes-meeting-intelligence/actions/workflows/ci.yml"><img src="https://github.com/tmolavi/hermes-meeting-intelligence/actions/workflows/ci.yml/badge.svg" alt="CI Status"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-Apache--2.0-green.svg" alt="Lisenziya"></a>
</p>

---

**Hermes Meeting Intelligence**, [Hermes Agent](https://github.com/NousResearch/hermes-agent) üçün açıq mənbəli, təchizatçıdan asılı olmayan struktur və rəsmi qoşmadır (plugin). O, nitqin mətnə çevrilməsini, strukturlaşdırılmış məlumat çıxarılmasını (qərarlar, təkliflər, fikir ayrılıqları, tapşırıqlar, sübutlar), SQLite əsaslı daimi iclas yaddaşını və real vaxt marşrutlaşdırmasını təmin edir.

---

## Bu layihə niyə yaradıldı?

Müasir rəqəmsal görünürlük artıq təkcə veb səhifələrinin sıralanmasından ibarət deyil. Süni intellekt sistemləri məlumatı getdikcə daha çox tapır, təhlil edir, əlaqələndirir və yadda saxlayır.

SEO, Generativ Mühərrik Optimizasiyası (GEO) və Süni İntellekt Görünürlüyü (AI Visibility) sahələrindəki fəaliyyətim məlumatın intellektual sistemlər tərəfindən necə strukturlaşdırıldığını və yadda saxlanıldığını anlamağı tələb edir.

İclas zəkası eyni informasiya arxitekturası məsələlərini həll edir:
- *Kimin nə dediyi?*
- *Hansı konkret qərarların qəbul edildiyi?*
- *Fikirləri hansı sitat və sübutların dəstəklədiyi?*
- *Bu müzakirənin əvvəlki iclas qərarları ilə necə əlaqələndiyi?*

Təkrar istifadə edilə bilən komponent real problemi həll etdikdə, onu sənədləşdirib paylaşmağa üstünlük verirəm ki, başqaları eyni vaxtı sərf etməsin.

---

## Əsas İmkanlar

- **Strukturlaşdırılmış İntellekt**: İclas transkriptlərini qərarlar, tapşırıqlar və sübutlar olan `MeetingRecord` modelinə çevirir.
- **Daimi İclas Yaddaşı**: Yerli SQLite verilənlər bazasında saxlayır və LLM kontekst pəncərəsini yükləmədən əvvəlki qərarları axtarmağa imkan verir.
- **İclaslararası Əlaqələr**: İclaslar arasındakı məntiqi əlaqələri (`davam_edir`, `əvəz_edir`, `istinad_edir`) izləyir.
- **Dəyişikliklərin Qeydiyyatı**: İclas sahibinin məlumatları dəqiqləşdirməsi zamanı tam audit izini saxlayır.
- **Çoxlu Təchizatçı Dəstəyi**: OpenAI, Groq, Deepgram və yerli Faster-Whisper dəstəyi ilə yanaşı, testlər üçün sıfır xərcli deterministik mock təmin edir.

---

## Quraşdırma

### Hermes Qoşması Kimi

```bash
hermes plugins install tmolavi/hermes-meeting-intelligence
```

### Python Paketi Kimi

```bash
pip install hermes-meeting-intelligence
```

---

## Tez Başlanğıc

```python
import asyncio
from hermes_meeting_intelligence import MeetingPipeline, MeetingMemoryStore


async def main():
    pipeline = MeetingPipeline()
    transcript = """
    [Aysel Məmmədova]: İclas yaddaşı üçün SQLite istifadə etməyə qərar verdik.
    [Rəşad Əliyev]: Razıyam. Sxem yoxlayıcısını cümə gününə qədər hazırlayacağam.
    """
    record = await pipeline.process_transcript(
        transcript, title="Memarlıq Müzakirəsi", language="az"
    )
    store = MeetingMemoryStore("~/.hermes/meeting_memory.sqlite")
    meeting_id = store.save_meeting(record)
    print(f"İclas saxlanıldı: {meeting_id} ({len(record.decisions)} qərar)")


if __name__ == "__main__":
    asyncio.run(main())
```

---

## Öyrən, Öyrət, Qalıcı Bir Şey Yarat

Faydalı həllər sənədləşdirilib açıq paylaşıldıqda peşəkar bilik daha da dəyər qazanır.

Başqalarından öyrənin, sınaqdan keçirdiyinizi öyrədin və faydalı bir irs qoyun.

---

## Müəllif Haqqında

**Taqi Molavi (Taghi Molavi)** tərəfindən yaradılmış və idarə olunur.

Əsas fəaliyyət sahəm SEO, GEO, Süni İntellekt Görünürlüyü və intellektual informasiya sistemləridir.

- Veb-sayt: [molavi.pro](https://molavi.pro)
- GitHub: [@tmolavi](https://github.com/tmolavi)

---

## Lisenziya

Bu layihə **Apache-2.0** lisenziyası altında təqdim olunur. Ətraflı məlumat üçün [LICENSE](LICENSE) faylına baxın.
