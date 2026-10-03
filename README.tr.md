# Hermes Toplantı Zekası (Hermes Meeting Intelligence)

> Hermes Agent için yeniden kullanılabilir toplantı zekası becerileri, araçları ve kalıcı toplantı hafızası.

<p align="center">
  <a href="README.md"><b>English</b></a> •
  <a href="README.fa.md"><b>فارسی</b></a> •
  <a href="README.tr.md"><b>Türkçe</b></a> •
  <a href="README.az.md"><b>Azərbaycan dili</b></a> •
  <a href="README.ar.md"><b>العربية</b></a>
</p>

<p align="center">
  <a href="https://github.com/tmolavi/hermes-meeting-intelligence/actions/workflows/ci.yml"><img src="https://github.com/tmolavi/hermes-meeting-intelligence/actions/workflows/ci.yml/badge.svg" alt="CI Durumu"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-Apache--2.0-green.svg" alt="Lisans"></a>
</p>

---

**Hermes Meeting Intelligence**, [Hermes Agent](https://github.com/NousResearch/hermes-agent) için açık kaynaklı, sağlayıcıdan bağımsız bir çerçeve ve resmi bir eklentidir. Modüler ses transkripsiyonu, yapılandırılmış bilgi çıkarımı (kararlar, öneriler, anlaşmazlıklar, görevler, kanıtlar), kalıcı SQLite toplantı hafızası ve gecikmeye duyarlı gerçek zamanlı yönlendirme sağlar.

---

## Bu proje neden var?

Modern dijital görünürlük artık yalnızca web sayfalarını sıralamaktan ibaret değildir. Yapay zeka sistemleri ve yanıt motorları (Answer Engines), bilgileri giderek daha fazla geri çağırır, yorumlar, bağlar, hatırlar ve alıntılar.

SEO, Üretken Motor Optimizasyonu (GEO) ve Yapay Zeka Görünürlüğü (AI Visibility) alanlarındaki çalışmalarım; bilginin akıllı sistemler tarafından nasıl yapılandırıldığını, geri çağrıldığını, değerlendirildiğini ve hatırlandığını anlamayı gerektirir.

Toplantı zekası da aynı temel bilgi mimarisi zorluklarını barındırır:
- *Kimin ne söylediği?*
- *Hangi somut kararların alındığı?*
- *İddiaları hangi kanıt ve alıntıların desteklediği?*
- *Bu görüşmenin önceki toplantı kararlarıyla nasıl ilişkilendiği?*
- *Hangi bilgilerin yetkili ve kesin olduğu?*

Bu proje, yapılandırılmış bilgi geri çağırma ve kalıcı ajan hafızası araştırmalarından doğmuştur. Yeniden kullanılabilir bir bileşen gerçek bir sorunu çözdüğünde, başkalarının aynı zamanı harcamaması için bunu belgeleyip yayınlamayı tercih ediyorum.

---

## Yetenekler

- **Yapılandırılmış Bilgi Çıkarımı**: Konuşma metinlerini kararlar, eylem maddeleri, açık sorular ve alıntılanmış kanıtlar içeren `MeetingRecord` modellerine dönüştürür.
- **Kalıcı Toplantı Hafızası**: Düşük kaynak tüketen yerel SQLite veritabanı sayesinde geçmiş toplantı bağlamını LLM bağlam penceresini şişirmeden sorgular.
- **Toplantılar Arası İlişki Grafı**: Toplantılar arasındaki mantıksal bağları (`devam_eder`, `yerini_alır`, `referans_verir`, `engeller`) takip eder.
- **Denetlenebilir Düzeltmeler**: Toplantı yöneticisinin çıkarılan verileri geçmiş denetim izini bozmadan düzeltmesine olanak tanır.
- **Çoklu Sağlayıcı Mimarisi**: OpenAI, Groq, Deepgram ve yerel Faster-Whisper adaptörleri içerir; testler için sıfır maliyetli deterministik mock sağlayıcı sunar.

---

## Kurulum

### Hermes Eklentisi Olarak Kurulum

```bash
hermes plugins install tmolavi/hermes-meeting-intelligence
```

### Python Paketi Olarak Kurulum

```bash
pip install hermes-meeting-intelligence
```

---

## Hızlı Başlangıç

```python
import asyncio
from hermes_meeting_intelligence import MeetingPipeline, MeetingMemoryStore


async def main():
    pipeline = MeetingPipeline()
    transcript = """
    [Ahmet Yılmaz]: Toplantı hafıza katmanı için SQLite kullanmaya karar verdik.
    [Mehmet Demir]: Katılıyorum. Şema doğrulayıcıyı cuma gününe kadar tamamlayacağım.
    """
    record = await pipeline.process_transcript(
        transcript, title="Mimari Değerlendirme", language="tr"
    )
    store = MeetingMemoryStore("~/.hermes/meeting_memory.sqlite")
    meeting_id = store.save_meeting(record)
    print(f"Toplantı kaydedildi: {meeting_id} ({len(record.decisions)} karar)")


if __name__ == "__main__":
    asyncio.run(main())
```

---

## Öğren, Öğret, Kalıcı Bir Şeyler İnşa Et

Pratik çözümler belgelenip açıkça paylaşıldığında mesleki bilgi katlanarak büyür.

Başkalarından öğrenin, doğruladığınızı öğretin ve arkada faydalı bir şeyler bırakın.

---

## Yazar Hakkında

**Taqi Molavi (Taghi Molavi)** tarafından geliştirilmiş ve sürdürülmektedir.

Ana çalışma alanım SEO, Üretken Motor Optimizasyonu (GEO), Yapay Zeka Görünürlüğü ve akıllı bilgi sistemleridir.

- Web: [molavi.pro](https://molavi.pro)
- GitHub: [@tmolavi](https://github.com/tmolavi)

---

## Lisans

Bu proje **Apache-2.0 Lisansı** ile lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakınız.
